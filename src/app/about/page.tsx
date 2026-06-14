import type { Metadata } from "next";
import Link from "next/link";
import { SITE_NAME } from "@/lib/site";

const ABOUT_DESC =
  "The Well-Being Atlas is maintained by Adam Duhachek and Vishal Singh — data visualizations on psychological well-being built from the GSS, Gallup, WVS, and ESS.";

// Only the page title/description are set here; the openGraph/twitter card
// (image included) is inherited from the root layout + app/opengraph-image so
// sharing /about shows the site card. Overriding openGraph here would drop the
// inherited file image.
export const metadata: Metadata = {
  title: "About",
  description: ABOUT_DESC,
};

const DATASETS = [
  { name: "General Social Survey (GSS)", note: "U.S. attitudes and well-being, 1972–present" },
  { name: "Gallup US Daily", note: "Large-scale U.S. daily tracking of life evaluation and affect" },
  { name: "Gallup World Poll", note: "Comparable well-being measures across ~150 countries" },
  { name: "World Values Survey (WVS)", note: "Cross-national values and life satisfaction" },
  { name: "European Social Survey (ESS)", note: "Biennial survey across European countries" },
];

export default function AboutPage() {
  return (
    <main id="content" className="about">
      <header className="about-head">
        <nav className="masthead-kicker" aria-label="Site">
          <Link href="/" className="nav-link">
            ← The Well-Being Atlas
          </Link>
        </nav>
        <h1>About the {SITE_NAME.replace("The ", "")}</h1>
      </header>

      <div className="about-body">
        <p className="about-lede">
          This website is maintained by <strong>Adam Duhachek</strong> and{" "}
          <strong>Vishal Singh</strong>. It provides data visualizations on
          psychological well-being using prominent datasets from the research
          literature.
        </p>
        <p>
          Each piece is a self-contained, hand-built data essay: every figure is
          computed from survey microdata with the appropriate sampling weights
          and traced back to a reproducible script. The aim is to read these
          sources honestly — reporting effect sizes plainly, flagging where a
          result is within noise, and staying inside the construct each survey
          item actually measures.
        </p>

        <h2>Datasets</h2>
        <ul className="dataset-list">
          {DATASETS.map((d) => (
            <li key={d.name}>
              <span className="dataset-name">{d.name}</span>
              <span className="dataset-note">{d.note}</span>
            </li>
          ))}
        </ul>

        <p className="about-back">
          <Link href="/" className="nav-link">
            ← Back to the index
          </Link>
        </p>
      </div>
    </main>
  );
}
