import { Suspense } from "react";
import { listArticles, getSiteIntro } from "@/lib/articles";
import { GalleryIndex } from "@/components/GalleryIndex";

export default function Home() {
  return (
    <main id="content">
      <Suspense fallback={<GallerySkeleton />}>
        <Gallery />
      </Suspense>
    </main>
  );
}

async function Gallery() {
  const [articles, intro] = await Promise.all([listArticles(), getSiteIntro()]);
  return <GalleryIndex articles={articles} intro={intro} />;
}

function GallerySkeleton() {
  return (
    <div className="masthead" aria-busy="true" aria-label="Loading articles">
      <hr className="masthead-rule" />
      <div className="masthead-kicker">
        <span>The Well-Being Atlas</span>
      </div>
      <div style={{ padding: "24px 0" }}>
        {Array.from({ length: 6 }, (_, i) => (
          <div className="skeleton-row" key={i}>
            <div />
            <div className="skeleton-block" />
            <div className="skeleton-lines">
              <div style={{ width: "55%", height: 22 }} />
              <div style={{ width: "85%" }} />
              <div style={{ width: "35%" }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
