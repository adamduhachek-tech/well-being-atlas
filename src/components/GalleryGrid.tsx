"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { GalleryItem } from "@/lib/gallery";
import {
  SUBTOPICS,
  SCOPES,
  SOURCES,
  SUBTOPIC_LABEL,
  SUBTOPIC_COLOR,
  type Subtopic,
} from "@/lib/taxonomy";
import { Sparkmark } from "@/lib/sparkmark";

const dateFmt = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
});

type FacetKey = string; // `subtopic:gender`, `scope:US`, `source:GSS`

export function GalleryGrid({
  items,
  intro,
}: {
  items: GalleryItem[];
  intro: { title: string; description: string };
}) {
  const [active, setActive] = useState<Set<FacetKey>>(new Set());
  const [query, setQuery] = useState("");

  // Only surface filter chips for tags that actually occur in the data.
  const present = useMemo(() => {
    const sub = new Set<string>();
    const scope = new Set<string>();
    const source = new Set<string>();
    for (const it of items) {
      it.subtopics.forEach((s) => sub.add(s));
      it.scope.forEach((s) => scope.add(s));
      it.sources.forEach((s) => source.add(s));
    }
    return { sub, scope, source };
  }, [items]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const subSel = [...active].filter((k) => k.startsWith("subtopic:")).map((k) => k.slice(9));
    const scopeSel = [...active].filter((k) => k.startsWith("scope:")).map((k) => k.slice(6));
    const sourceSel = [...active].filter((k) => k.startsWith("source:")).map((k) => k.slice(7));

    return items.filter((it) => {
      if (subSel.length && !subSel.some((s) => it.subtopics.includes(s as Subtopic))) return false;
      if (scopeSel.length && !scopeSel.some((s) => it.scope.includes(s as never))) return false;
      if (sourceSel.length && !sourceSel.some((s) => it.sources.includes(s as never))) return false;
      if (q) {
        const hay = [it.title, it.snippet, it.dataset].filter(Boolean).join(" ").toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [items, active, query]);

  const toggle = (key: FacetKey) =>
    setActive((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });

  const clearAll = () => {
    setActive(new Set());
    setQuery("");
  };

  const hasFilters = active.size > 0 || query.trim().length > 0;

  return (
    <>
      <header className="masthead">
        <hr className="masthead-rule" />
        <nav className="masthead-kicker" aria-label="Site">
          <span>The Well-Being Atlas</span>
          <Link href="/about" className="nav-link">
            About
          </Link>
        </nav>
        <h1>{renderTitle(intro.title)}</h1>
        <p className="masthead-desc">{intro.description}</p>
      </header>

      <section className="filters" aria-label="Filter articles">
        <div className="filter-group">
          <span className="filter-legend">Topic</span>
          <div className="chip-row">
            {SUBTOPICS.filter((s) => present.sub.has(s.key)).map((s) => (
              <FilterChip
                key={s.key}
                label={s.label}
                active={active.has(`subtopic:${s.key}`)}
                color={SUBTOPIC_COLOR[s.key]}
                onClick={() => toggle(`subtopic:${s.key}`)}
              />
            ))}
          </div>
        </div>
        <div className="filter-group">
          <span className="filter-legend">Scope &amp; source</span>
          <div className="chip-row">
            {SCOPES.filter((s) => present.scope.has(s)).map((s) => (
              <FilterChip
                key={s}
                label={s}
                active={active.has(`scope:${s}`)}
                onClick={() => toggle(`scope:${s}`)}
              />
            ))}
            {SOURCES.filter((s) => present.source.has(s)).map((s) => (
              <FilterChip
                key={s}
                label={s}
                active={active.has(`source:${s}`)}
                onClick={() => toggle(`source:${s}`)}
              />
            ))}
          </div>
        </div>

        <div className="filter-foot">
          <input
            className="search-input"
            type="search"
            placeholder="Search titles & snippets…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search articles"
            autoComplete="off"
          />
          <span className="result-count" aria-live="polite">
            {filtered.length} of {items.length}
          </span>
          {hasFilters && (
            <button type="button" className="clear-all" onClick={clearAll}>
              Clear all
            </button>
          )}
        </div>
      </section>

      {filtered.length === 0 ? (
        <p className="no-results">Nothing matches those filters.</p>
      ) : (
        <ul className="card-grid" aria-label="Articles">
          {filtered.map((it, i) => (
            <li
              className="card-cell"
              key={it.slug}
              style={{ "--stagger": Math.min(i, 11) } as React.CSSProperties}
            >
              <Card item={it} />
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

function FilterChip({
  label,
  active,
  color,
  onClick,
}: {
  label: string;
  active: boolean;
  color?: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={active ? "chip chip--active" : "chip"}
      aria-pressed={active}
      onClick={onClick}
      style={color ? ({ "--chip-color": color } as React.CSSProperties) : undefined}
    >
      {color && <span className="chip-dot" aria-hidden="true" />}
      {label}
    </button>
  );
}

function Card({ item }: { item: GalleryItem }) {
  const accent = item.subtopics[0]
    ? SUBTOPIC_COLOR[item.subtopics[0]]
    : "#8c8676";
  return (
    <Link className="card" href={`/articles/${item.slug}`}>
      <div className="card-thumb">
        {item.thumbnail ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={item.thumbnail}
            alt=""
            loading="lazy"
            decoding="async"
            className="card-thumb-img"
          />
        ) : (
          <div
            className="card-thumb-fallback"
            style={{ "--accent": accent } as React.CSSProperties}
          >
            <Sparkmark
              seed={item.slug}
              primaryViz={item.primaryViz}
              useCssVars
            />
          </div>
        )}
        <span className="card-no" aria-hidden="true">
          №{String(item.number).padStart(2, "0")}
        </span>
      </div>
      <div className="card-body">
        <h2 className="card-title">{item.title}</h2>
        {item.snippet && <p className="card-snippet">{item.snippet}</p>}
        <div className="card-foot">
          <span className="card-meta">
            <time dateTime={item.date}>{dateFmt.format(new Date(item.date))}</time>
            {item.readMinutes ? <span> · {item.readMinutes} min</span> : null}
            {item.dataset ? <span className="card-dataset"> · {item.dataset}</span> : null}
          </span>
          {item.subtopics.length > 0 && (
            <span className="card-chips">
              {item.subtopics.slice(0, 3).map((s) => (
                <span
                  className="tag"
                  key={s}
                  style={{ "--chip-color": SUBTOPIC_COLOR[s] } as React.CSSProperties}
                >
                  {SUBTOPIC_LABEL[s]}
                </span>
              ))}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}

function renderTitle(title: string) {
  const words = title.split(" ");
  if (words.length < 2) return title;
  const last = words.pop()!;
  return (
    <>
      {words.join(" ")} <em>{last}</em>
    </>
  );
}
