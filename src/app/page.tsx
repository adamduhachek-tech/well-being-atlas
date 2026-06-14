import { Suspense } from "react";
import { getGalleryItems } from "@/lib/gallery";
import { GalleryGrid } from "@/components/GalleryGrid";

// Editorial framing for the masthead. Kept count-independent so the heading
// never goes stale as articles are added to the bucket.
const INTRO = {
  title: "Readings in Well-Being",
  description:
    "An evolving index of independent, reproducible data essays on how people rate their lives — each hand-built from survey microdata: the GSS, Gallup (US Daily and World Poll), and the World and European value surveys.",
};

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
  const items = await getGalleryItems();
  return <GalleryGrid items={items} intro={INTRO} />;
}

function GallerySkeleton() {
  return (
    <div className="masthead" aria-busy="true" aria-label="Loading articles">
      <hr className="masthead-rule" />
      <div className="masthead-kicker">
        <span>The Well-Being Atlas</span>
      </div>
      <div className="card-grid" style={{ marginTop: 40 }}>
        {Array.from({ length: 6 }, (_, i) => (
          <div className="card card--skeleton" key={i}>
            <div className="card-thumb skeleton-block" />
            <div className="card-body">
              <div className="skeleton-lines">
                <div style={{ width: "70%", height: 20 }} />
                <div style={{ width: "95%" }} />
                <div style={{ width: "40%" }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
