import type { MetadataRoute } from "next";
import { listArticles } from "@/lib/articles";
import { siteUrl } from "@/lib/site";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = siteUrl();
  const articles = await listArticles();
  return [
    { url: base, changeFrequency: "daily", priority: 1 },
    ...articles.map((a) => ({
      url: `${base}/articles/${a.slug}`,
      lastModified: a.date,
      changeFrequency: "monthly" as const,
      priority: 0.8,
    })),
  ];
}
