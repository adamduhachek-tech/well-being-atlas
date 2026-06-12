"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Article } from "@/lib/articles";
import { Sparkmark } from "@/lib/sparkmark";

const dateFmt = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
});

export function GalleryIndex({
  articles,
  intro,
}: {
  articles: Article[];
  intro: { title: string; description: string };
}) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return articles;
    return articles.filter((a) =>
      [a.title, a.description, a.dataset, a.primaryViz]
        .filter(Boolean)
        .some((field) => field!.toLowerCase().includes(q))
    );
  }, [articles, query]);

  const searching = query.trim().length > 0;
  const [lead, ...rest] = filtered;

  return (
    <>
      <header className="masthead">
        <hr className="masthead-rule" />
        <p className="masthead-kicker">
          <span>The Well-Being Atlas</span>
          <span>An index of data essays</span>
        </p>
        <h1>{renderTitle(intro.title)}</h1>
        <p className="masthead-desc">{intro.description}</p>
        <div className="search-row">
          <label className="search-count" htmlFor="gallery-search">
            {filtered.length} of {articles.length} readings
          </label>
          <input
            id="gallery-search"
            className="search-input"
            type="search"
            placeholder="Search titles, deks, datasets…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoComplete="off"
          />
        </div>
      </header>

      {filtered.length === 0 ? (
        <div className="ledger">
          <p className="no-results">
            Nothing in the index matches “{query}”.
          </p>
        </div>
      ) : (
        <ol className="ledger">
          {lead && (
            <li
              className={searching ? "entry" : "entry entry--lead"}
              style={{ "--stagger": 0 } as React.CSSProperties}
            >
              <Entry article={lead} index={1} />
            </li>
          )}
          {rest.map((a, i) => (
            <li
              className="entry"
              key={a.slug}
              style={{ "--stagger": Math.min(i + 1, 12) } as React.CSSProperties}
            >
              <Entry article={a} index={i + 2} />
            </li>
          ))}
        </ol>
      )}
    </>
  );
}

function renderTitle(title: string) {
  // Italicize the last word as a small typographic flourish.
  const words = title.split(" ");
  if (words.length < 2) return title;
  const last = words.pop()!;
  return (
    <>
      {words.join(" ")} <em>{last}</em>
    </>
  );
}

function Entry({ article, index }: { article: Article; index: number }) {
  return (
    <Link className="entry-link" href={`/articles/${article.slug}`}>
      <span className="entry-no" aria-hidden="true">
        №{String(index).padStart(2, "0")}
      </span>
      <span className="entry-mark">
        <Sparkmark
          seed={article.slug}
          primaryViz={article.primaryViz}
          useCssVars
        />
      </span>
      <span className="entry-body">
        <h2 className="entry-title">{article.title}</h2>
        {article.description && (
          <p className="entry-desc">{article.description}</p>
        )}
        <span className="entry-meta">
          {article.dataset && <span>{article.dataset}</span>}
          {article.primaryViz && (
            <span className="viz">{article.primaryViz}</span>
          )}
          {article.readingMinutes && (
            <span>{article.readingMinutes} min read</span>
          )}
          <span>
            <time dateTime={article.date}>
              {dateFmt.format(new Date(article.date))}
            </time>
          </span>
        </span>
      </span>
    </Link>
  );
}
