import "server-only";
import { listArticles, type Article } from "@/lib/articles";
import { inferTags, type Subtopic, type Scope, type Source } from "@/lib/taxonomy";
import manifestData from "@/data/articles.json";

/** One curated manifest entry, produced by scripts/build-manifest.mjs.
 *  Tags here are a re-runnable first pass and are meant to be hand-correctable. */
export interface ManifestEntry {
  slug: string;
  title?: string;
  snippet?: string;
  dataset?: string | null;
  readMinutes?: number | null;
  date?: string;
  thumbnail?: string | null;
  subtopics?: Subtopic[];
  scope?: Scope[];
  sources?: Source[];
}

interface Manifest {
  generatedAt: string | null;
  articles: ManifestEntry[];
}

const manifest = manifestData as Manifest;

export interface GalleryItem {
  slug: string;
  number: number;
  title: string;
  snippet: string | null;
  dataset: string | null;
  readMinutes: number | null;
  date: string;
  primaryViz: string | null;
  thumbnail: string | null;
  subtopics: Subtopic[];
  scope: Scope[];
  sources: Source[];
}

/**
 * The gallery's data source: the live bucket listing (auto-updating, cached)
 * is canonical, joined with the committed manifest by slug. Articles present
 * in the bucket but not yet in the manifest still appear — they get tags
 * inferred at runtime and fall back to a generated sparkmark thumbnail.
 * Re-running the manifest script upgrades them to captured thumbnails and
 * lets the tags be hand-corrected.
 */
export async function getGalleryItems(): Promise<GalleryItem[]> {
  const articles = await listArticles();
  const bySlug = new Map(manifest.articles.map((m) => [m.slug, m]));

  const items = articles.map((a, i): GalleryItem => {
    const m = bySlug.get(a.slug);
    const tags = inferTags({
      title: a.title,
      description: a.description,
      dataset: a.dataset,
    });
    return {
      slug: a.slug,
      number: i + 1, // assigned after the newest-first sort below
      title: m?.title ?? a.title,
      snippet: m?.snippet ?? a.description,
      dataset: m?.dataset ?? a.dataset,
      readMinutes: m?.readMinutes ?? a.readingMinutes,
      date: m?.date ?? a.date,
      primaryViz: a.primaryViz,
      thumbnail: m?.thumbnail ?? null,
      subtopics: m?.subtopics?.length ? m.subtopics : tags.subtopics,
      scope: m?.scope?.length ? m.scope : tags.scope,
      sources: m?.sources?.length ? m.sources : tags.sources,
    };
  });

  // listArticles() already returns newest-first; number the index from 1.
  return items.map((item, i) => ({ ...item, number: i + 1 }));
}

export type { Article };
