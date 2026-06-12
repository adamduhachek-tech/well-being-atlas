import "server-only";
import { cacheLife, cacheTag } from "next/cache";
import { S3Client, ListObjectsV2Command } from "@aws-sdk/client-s3";
import * as cheerio from "cheerio";

export const BUCKET_URL =
  process.env.NEXT_PUBLIC_ARTICLE_BUCKET_URL ??
  "https://happy.t3.tigrisfiles.io";

const BUCKET = process.env.ARTICLE_BUCKET ?? "happy";
const ENRICH_CONCURRENCY = 8;

export interface Article {
  slug: string;
  key: string;
  url: string;
  title: string;
  description: string | null;
  dataset: string | null;
  construct: string | null;
  primaryViz: string | null;
  readingMinutes: number | null;
  /** ISO date string, from the bucket's LastModified */
  date: string;
  image: string | null;
}

interface ManifestEntry {
  slug?: string;
  title?: string;
  dek?: string;
  dataset?: string;
  construct?: string;
  primaryViz?: string;
  path?: string;
}

interface Manifest {
  title?: string;
  description?: string;
  articles?: ManifestEntry[];
}

function slugify(key: string): string {
  return key
    .toLowerCase()
    .replace(/\.html$/, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function humanizeKey(key: string): string {
  return slugify(key)
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

async function listHtmlKeys(): Promise<{ key: string; date: string }[]> {
  const s3 = new S3Client({
    region: process.env.AWS_REGION ?? "auto",
    endpoint: process.env.AWS_ENDPOINT_URL_S3 ?? "https://t3.storage.dev",
  });
  const out: { key: string; date: string }[] = [];
  let token: string | undefined;
  do {
    const res = await s3.send(
      new ListObjectsV2Command({ Bucket: BUCKET, ContinuationToken: token })
    );
    for (const obj of res.Contents ?? []) {
      const key = obj.Key;
      if (!key || !key.endsWith(".html")) continue;
      if (key === "index.html") continue;
      out.push({
        key,
        date: (obj.LastModified ?? new Date(0)).toISOString(),
      });
    }
    token = res.IsTruncated ? res.NextContinuationToken : undefined;
  } while (token);
  return out;
}

async function fetchManifest(): Promise<Manifest | null> {
  try {
    const res = await fetch(`${BUCKET_URL}/gallery.json`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return (await res.json()) as Manifest;
  } catch {
    return null;
  }
}

interface Extracted {
  title: string | null;
  description: string | null;
  image: string | null;
  readingMinutes: number | null;
}

async function extractFromHtml(key: string): Promise<Extracted> {
  const res = await fetch(`${BUCKET_URL}/${encodeURIComponent(key)}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`GET ${key} -> ${res.status}`);
  const html = await res.text();
  const $ = cheerio.load(html);

  const title =
    $('meta[property="og:title"]').attr("content")?.trim() ||
    $("title").first().text().trim() ||
    $("h1").first().text().trim() ||
    null;

  const description =
    $('meta[property="og:description"]').attr("content")?.trim() ||
    $('meta[name="description"]').attr("content")?.trim() ||
    $(".dek").first().text().trim().replace(/\s+/g, " ") ||
    $("p").first().text().trim().replace(/\s+/g, " ") ||
    null;

  let image =
    $('meta[property="og:image"]').attr("content")?.trim() ||
    $("img").first().attr("src")?.trim() ||
    null;
  if (image && !/^https?:\/\//.test(image)) {
    image = new globalThis.URL(image, `${BUCKET_URL}/`).href;
  }

  $("script, style, svg").remove();
  const words = $("body").text().split(/\s+/).filter(Boolean).length;
  const readingMinutes = words > 0 ? Math.max(1, Math.round(words / 220)) : null;

  return { title, description, image, readingMinutes };
}

async function mapWithConcurrency<T, R>(
  items: T[],
  limit: number,
  fn: (item: T) => Promise<R>
): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let next = 0;
  async function worker() {
    while (next < items.length) {
      const i = next++;
      results[i] = await fn(items[i]);
    }
  }
  await Promise.all(
    Array.from({ length: Math.min(limit, items.length) }, worker)
  );
  return results;
}

/**
 * Lists every article in the bucket, enriched with metadata extracted from
 * the HTML itself and from the curated gallery.json manifest when present.
 * Files that are newer revisions of the same article (same title) are
 * deduplicated, keeping the most recent upload.
 */
export async function listArticles(): Promise<Article[]> {
  "use cache";
  cacheLife("hours");
  cacheTag("articles");

  const [keys, manifest] = await Promise.all([listHtmlKeys(), fetchManifest()]);

  const byPath = new Map<string, ManifestEntry>();
  const bySlug = new Map<string, ManifestEntry>();
  for (const entry of manifest?.articles ?? []) {
    if (entry.path) byPath.set(entry.path, entry);
    if (entry.slug) bySlug.set(entry.slug, entry);
  }

  const enriched = await mapWithConcurrency(keys, ENRICH_CONCURRENCY, async ({ key, date }) => {
    const slug = slugify(key);
    const entry = byPath.get(key) ?? bySlug.get(slug);
    let extracted: Extracted = {
      title: null,
      description: null,
      image: null,
      readingMinutes: null,
    };
    try {
      extracted = await extractFromHtml(key);
    } catch (err) {
      // One malformed file must never break the gallery.
      console.error(`[articles] failed to extract ${key}:`, err);
    }
    const article: Article = {
      slug,
      key,
      url: `${BUCKET_URL}/${encodeURIComponent(key)}`,
      title: entry?.title ?? extracted.title ?? humanizeKey(key),
      description: entry?.dek ?? extracted.description,
      dataset: entry?.dataset ?? null,
      construct: entry?.construct ?? null,
      primaryViz: entry?.primaryViz ?? null,
      readingMinutes: extracted.readingMinutes,
      date,
      image: extracted.image,
    };
    return article;
  });

  // Dedup pass 1: identical slugs (e.g. "a_b.html" and "a-b.html") — keep newest.
  // Dedup pass 2: identical titles under different keys — keep newest, but
  // carry over curated manifest fields from the older revision if missing.
  const merge = (keep: Article, drop: Article): Article => ({
    ...keep,
    description: keep.description ?? drop.description,
    dataset: keep.dataset ?? drop.dataset,
    construct: keep.construct ?? drop.construct,
    primaryViz: keep.primaryViz ?? drop.primaryViz,
    readingMinutes: keep.readingMinutes ?? drop.readingMinutes,
    image: keep.image ?? drop.image,
  });

  const dedupe = (items: Article[], keyOf: (a: Article) => string) => {
    const map = new Map<string, Article>();
    for (const a of items) {
      const k = keyOf(a);
      const existing = map.get(k);
      if (!existing) {
        map.set(k, a);
      } else if (a.date > existing.date) {
        map.set(k, merge(a, existing));
      } else {
        map.set(k, merge(existing, a));
      }
    }
    return [...map.values()];
  };

  const deduped = dedupe(
    dedupe(enriched, (a) => a.slug),
    (a) => a.title.toLowerCase().trim()
  );

  return deduped.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export async function getArticle(slug: string): Promise<Article | null> {
  const articles = await listArticles();
  return articles.find((a) => a.slug === slug) ?? null;
}

export async function getSiteIntro(): Promise<{
  title: string;
  description: string;
}> {
  "use cache";
  cacheLife("hours");
  cacheTag("articles");
  const manifest = await fetchManifest();
  return {
    title: manifest?.title ?? "Readings of Well-Being",
    description:
      manifest?.description ??
      "Independent data-journalism articles on psychological well-being.",
  };
}
