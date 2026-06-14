/**
 * build-manifest.ts — standalone, idempotent, re-runnable.
 *
 * Introspects the Tigris bucket, extracts per-article metadata, infers tags
 * from the shared taxonomy, captures a thumbnail of each article's primary
 * visualization, uploads thumbnails to the bucket under `thumbnails/`, and
 * writes src/data/articles.json (read by the gallery at build/request time).
 *
 * Run:  npm run manifest
 *       npm run manifest -- --no-thumbnails   (metadata + tags only, fast)
 *
 * Credentials are read from .env.local only and never printed.
 */

import { S3Client, ListObjectsV2Command } from "@aws-sdk/client-s3";
import * as cheerio from "cheerio";
import puppeteer, { type Browser } from "puppeteer-core";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { inferTags, type Subtopic, type Scope, type Source } from "../src/lib/taxonomy.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

// ---- env ----
const env = Object.fromEntries(
  readFileSync(resolve(ROOT, ".env.local"), "utf8")
    .split(/\r?\n/)
    .filter((l) => l && !l.startsWith("#") && l.includes("="))
    .map((l) => {
      const i = l.indexOf("=");
      return [l.slice(0, i).trim(), l.slice(i + 1).trim()];
    })
);

const BUCKET = env.ARTICLE_BUCKET ?? "happy";
const BUCKET_URL =
  env.NEXT_PUBLIC_ARTICLE_BUCKET_URL ?? "https://happy.t3.tigrisfiles.io";
const NO_THUMBS = process.argv.includes("--no-thumbnails");
const CHROME =
  process.env.CHROME_PATH ??
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const s3 = new S3Client({
  region: env.AWS_REGION ?? "auto",
  endpoint: env.AWS_ENDPOINT_URL_S3,
  credentials: {
    accessKeyId: env.AWS_ACCESS_KEY_ID,
    secretAccessKey: env.AWS_SECRET_ACCESS_KEY,
  },
});

// ---- helpers (kept in sync with src/lib/articles.ts on purpose) ----
function slugify(key: string): string {
  return key
    .toLowerCase()
    .replace(/\.html$/, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
function humanize(key: string): string {
  return slugify(key)
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

interface RawArticle {
  key: string;
  slug: string;
  date: string;
  title: string;
  snippet: string | null;
  dataset: string | null;
  readMinutes: number | null;
}

interface ManifestEntry extends Omit<RawArticle, never> {
  thumbnail: string | null;
  thumbnailSource: "captured" | "fallback";
  subtopics: Subtopic[];
  scope: Scope[];
  sources: Source[];
}

async function listHtml(): Promise<{ key: string; date: string }[]> {
  const out: { key: string; date: string }[] = [];
  let token: string | undefined;
  do {
    const res = await s3.send(
      new ListObjectsV2Command({ Bucket: BUCKET, ContinuationToken: token })
    );
    for (const o of res.Contents ?? []) {
      if (!o.Key || !o.Key.endsWith(".html") || o.Key === "index.html") continue;
      out.push({ key: o.Key, date: (o.LastModified ?? new Date(0)).toISOString() });
    }
    token = res.IsTruncated ? res.NextContinuationToken : undefined;
  } while (token);
  return out;
}

async function fetchManifestJson(): Promise<Map<string, { dataset?: string; dek?: string; title?: string }>> {
  const map = new Map<string, { dataset?: string; dek?: string; title?: string }>();
  try {
    const res = await fetch(`${BUCKET_URL}/gallery.json`, { cache: "no-store" });
    if (!res.ok) return map;
    const json = (await res.json()) as { articles?: { path?: string; slug?: string; title?: string; dek?: string; dataset?: string }[] };
    for (const a of json.articles ?? []) {
      const entry = { dataset: a.dataset, dek: a.dek, title: a.title };
      if (a.path) map.set(a.path, entry);
      if (a.slug) map.set(a.slug, entry);
    }
  } catch {
    /* manifest optional */
  }
  return map;
}

async function extract(key: string, gallery: Map<string, { dataset?: string; dek?: string; title?: string }>): Promise<Omit<RawArticle, "key" | "slug" | "date">> {
  const g = gallery.get(key) ?? gallery.get(slugify(key));
  try {
    const res = await fetch(`${BUCKET_URL}/${encodeURIComponent(key)}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`${res.status}`);
    const html = await res.text();
    const $ = cheerio.load(html);
    const title =
      g?.title ||
      $('meta[property="og:title"]').attr("content")?.trim() ||
      $("title").first().text().trim() ||
      $("h1").first().text().trim() ||
      humanize(key);
    const snippet =
      g?.dek ||
      $('meta[name="description"]').attr("content")?.trim() ||
      $(".dek").first().text().trim().replace(/\s+/g, " ") ||
      $("p").first().text().trim().replace(/\s+/g, " ") ||
      null;
    // dataset: gallery.json, or a "Gallup/GSS … , YYYY" style line in the byline
    let dataset = g?.dataset ?? null;
    if (!dataset) {
      // Just the survey family + an optional year span — avoid dragging in the
      // noisy interview-count tail that follows it in many bylines.
      const m = $("body")
        .text()
        .match(
          /(General Social Survey|Gallup World Poll|Gallup US Daily|World Values Survey|European Social Survey)(?:[,\s]+(\d{4}(?:\s*[–-]\s*\d{2,4})?))?/i
        );
      dataset = m ? (m[2] ? `${m[1]}, ${m[2].replace(/\s/g, "")}` : m[1]) : null;
    }
    $("script, style, svg").remove();
    const words = $("body").text().split(/\s+/).filter(Boolean).length;
    const readMinutes = words > 0 ? Math.max(1, Math.round(words / 220)) : null;
    return { title, snippet, dataset, readMinutes };
  } catch (err) {
    console.warn(`  ! extract failed for ${key}: ${(err as Error).message}`);
    return { title: g?.title ?? humanize(key), snippet: g?.dek ?? null, dataset: g?.dataset ?? null, readMinutes: null };
  }
}

/** newest-first, deduped by slug then by title (keep newest). */
function dedupe(items: RawArticle[]): RawArticle[] {
  const merge = (keep: RawArticle, drop: RawArticle): RawArticle => ({
    ...keep,
    snippet: keep.snippet ?? drop.snippet,
    dataset: keep.dataset ?? drop.dataset,
    readMinutes: keep.readMinutes ?? drop.readMinutes,
  });
  const pass = (arr: RawArticle[], keyOf: (a: RawArticle) => string) => {
    const m = new Map<string, RawArticle>();
    for (const a of arr) {
      const k = keyOf(a);
      const ex = m.get(k);
      if (!ex) m.set(k, a);
      else if (a.date > ex.date) m.set(k, merge(a, ex));
      else m.set(k, merge(ex, a));
    }
    return [...m.values()];
  };
  return pass(pass(items, (a) => a.slug), (a) => a.title.toLowerCase().trim()).sort(
    (a, b) => (a.date < b.date ? 1 : -1)
  );
}

async function captureThumbnail(browser: Browser, art: RawArticle): Promise<Buffer | null> {
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: 1200, height: 750, deviceScaleFactor: 1 });
    await page.goto(`${BUCKET_URL}/${encodeURIComponent(art.key)}`, {
      waitUntil: "domcontentloaded",
      timeout: 20000,
    });
    // Wait for D3 to draw a substantial SVG.
    const rect = await page
      .waitForFunction(
        () => {
          const svgs = Array.from(document.querySelectorAll("svg"));
          const big = svgs.find((s) => {
            const r = s.getBoundingClientRect();
            return r.width >= 280 && r.height >= 140 && s.querySelectorAll("*").length > 6;
          });
          if (!big) return null;
          big.scrollIntoView({ block: "center" });
          const r = big.getBoundingClientRect();
          return { top: r.top + window.scrollY, height: r.height };
        },
        { timeout: 11000, polling: 300 }
      )
      .then((h) => h.jsonValue() as Promise<{ top: number; height: number }>)
      .catch(() => null);

    await new Promise((r) => setTimeout(r, 700)); // let transitions settle

    const clipTop = rect ? Math.max(0, Math.round(rect.top - 48)) : 0;
    const buf = (await page.screenshot({
      type: "png",
      clip: { x: 0, y: clipTop, width: 1200, height: 750 },
      captureBeyondViewport: true,
    })) as Buffer;
    return buf;
  } catch (err) {
    console.warn(`  ! thumbnail capture failed for ${art.slug}: ${(err as Error).message}`);
    return null;
  } finally {
    await page.close().catch(() => {});
  }
}

// The Tigris credentials are read-only (PutObject → 403), so thumbnails are
// written into the Next app's public/ folder and served by the host instead
// of the bucket's `thumbnails/` prefix. Same result on the cards; versioned
// with the code. If write-capable creds are provided later, this is the one
// function to swap back to an S3 PutObject.
const THUMB_DIR = resolve(ROOT, "public/thumbnails");
function saveThumbnail(slug: string, buf: Buffer): string {
  mkdirSync(THUMB_DIR, { recursive: true });
  writeFileSync(resolve(THUMB_DIR, `${slug}.png`), buf);
  return `/thumbnails/${slug}.png`;
}

async function main() {
  console.log(`Listing bucket "${BUCKET}" …`);
  const [keys, gallery] = await Promise.all([listHtml(), fetchManifestJson()]);
  console.log(`  ${keys.length} html objects`);

  const raw: RawArticle[] = [];
  for (const { key, date } of keys) {
    const meta = await extract(key, gallery);
    raw.push({ key, slug: slugify(key), date, ...meta });
  }
  const articles = dedupe(raw);
  console.log(`  ${articles.length} articles after dedupe`);

  let browser: Browser | null = null;
  if (!NO_THUMBS) {
    if (!existsSync(CHROME)) {
      console.warn(`  ! Chrome not found at ${CHROME} — skipping thumbnails (set CHROME_PATH).`);
    } else {
      browser = await puppeteer.launch({ executablePath: CHROME, headless: "new" });
    }
  }

  const entries: ManifestEntry[] = [];
  let captured = 0;
  for (const art of articles) {
    const tags = inferTags({ title: art.title, description: art.snippet, dataset: art.dataset });
    let thumbnail: string | null = null;
    let thumbnailSource: "captured" | "fallback" = "fallback";
    if (browser) {
      const buf = await captureThumbnail(browser, art);
      if (buf) {
        thumbnail = saveThumbnail(art.slug, buf);
        thumbnailSource = "captured";
        captured++;
        console.log(`  ✓ ${art.slug} (${(buf.length / 1024).toFixed(0)} KB)`);
      } else {
        console.log(`  · ${art.slug} → fallback`);
      }
    } else if (existsSync(resolve(THUMB_DIR, `${art.slug}.png`))) {
      // --no-thumbnails: keep any thumbnail captured by a previous full run.
      thumbnail = `/thumbnails/${art.slug}.png`;
      thumbnailSource = "captured";
      captured++;
    }
    entries.push({
      ...art,
      thumbnail,
      thumbnailSource,
      subtopics: tags.subtopics,
      scope: tags.scope,
      sources: tags.sources,
    });
  }
  if (browser) await browser.close();

  const outPath = resolve(ROOT, "src/data/articles.json");
  writeFileSync(
    outPath,
    JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        articles: entries.map((e) => ({
          slug: e.slug,
          title: e.title,
          snippet: e.snippet,
          dataset: e.dataset,
          readMinutes: e.readMinutes,
          date: e.date,
          thumbnail: e.thumbnail,
          thumbnailSource: e.thumbnailSource,
          subtopics: e.subtopics,
          scope: e.scope,
          sources: e.sources,
        })),
      },
      null,
      2
    ) + "\n"
  );
  console.log(`\nWrote ${outPath}`);
  console.log(`  ${entries.length} entries, ${captured} thumbnails captured, ${entries.length - captured} fallbacks`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
