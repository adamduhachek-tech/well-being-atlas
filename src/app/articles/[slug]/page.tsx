import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { listArticles, getArticle } from "@/lib/articles";
import { ShareBar } from "@/components/ShareBar";
import { SITE_NAME, siteUrl } from "@/lib/site";

// With cacheComponents, slugs beyond generateStaticParams render on demand
// by default — new bucket uploads resolve without a redeploy.
export async function generateStaticParams() {
  const articles = await listArticles();
  return articles.map((a) => ({ slug: a.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const article = await getArticle(slug);
  if (!article) return { title: "Not found" };

  const canonical = `${siteUrl()}/articles/${article.slug}`;
  return {
    title: article.title,
    description: article.description ?? undefined,
    alternates: { canonical },
    openGraph: {
      type: "article",
      url: canonical,
      siteName: SITE_NAME,
      title: article.title,
      description: article.description ?? undefined,
      publishedTime: article.date,
    },
    twitter: {
      card: "summary_large_image",
      title: article.title,
      description: article.description ?? undefined,
    },
  };
}

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const article = await getArticle(slug);
  if (!article) notFound();

  return (
    <main id="content">
      <header className="article-chrome">
        <Link href="/" className="back-link">
          <span aria-hidden="true">←</span> Index
        </Link>
        <span className="article-chrome-title">{article.title}</span>
        <ShareBar title={article.title} description={article.description} />
      </header>
      {/* The original essay, served untouched from the bucket. The articles
          are interactive D3 documents that fetch sibling assets, so they need
          scripts and their own origin. */}
      <iframe
        className="article-frame"
        src={article.url}
        title={article.title}
        sandbox="allow-scripts allow-same-origin"
        loading="eager"
      />
    </main>
  );
}
