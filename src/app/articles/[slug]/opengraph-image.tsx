import { ImageResponse } from "next/og";
import { getArticle } from "@/lib/articles";
import { Sparkmark, SPARK_LIGHT } from "@/lib/sparkmark";
import { SITE_NAME, siteUrl } from "@/lib/site";
import { OG_SIZE, loadOgFonts, fetchImageDataUrl } from "@/lib/og";
import manifest from "@/data/articles.json";

export const size = OG_SIZE;
export const contentType = "image/png";
export const alt = "Article share card";

export default async function OgImage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const [article, fonts] = await Promise.all([getArticle(slug), loadOgFonts()]);

  // Prefer the captured chart thumbnail; fall back to the sparkmark glyph.
  const entry = (
    manifest.articles as {
      slug: string;
      thumbnail: string | null;
      dataset: string | null;
      readMinutes: number | null;
    }[]
  ).find((a) => a.slug === slug);
  const thumb = entry?.thumbnail
    ? await fetchImageDataUrl(`${siteUrl()}${entry.thumbnail}`)
    : null;

  const title = article?.title ?? SITE_NAME;
  const dataset = article?.dataset ?? entry?.dataset ?? null;
  const readMinutes = article?.readingMinutes ?? entry?.readMinutes ?? null;
  const meta = [dataset, readMinutes ? `${readMinutes} min read` : null]
    .filter(Boolean)
    .join("  ·  ");

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          backgroundColor: "#EFEBE0",
          fontFamily: "Newsreader, serif",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            flex: 1,
            padding: 56,
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              borderTop: "5px solid #26231C",
              paddingTop: 18,
            }}
          >
            <div
              style={{
                fontFamily: "IBM Plex Mono, monospace",
                fontSize: 22,
                letterSpacing: 5,
                textTransform: "uppercase",
                color: "#B5402C",
              }}
            >
              {SITE_NAME}
            </div>
            <div
              style={{
                fontSize: title.length > 60 ? 54 : 66,
                lineHeight: 1.04,
                color: "#26231C",
                marginTop: 26,
                letterSpacing: -1,
              }}
            >
              {title}
            </div>
          </div>
          {meta && (
            <div
              style={{
                fontFamily: "IBM Plex Mono, monospace",
                fontSize: 19,
                letterSpacing: 1,
                textTransform: "uppercase",
                color: "#5C574A",
              }}
            >
              {meta}
            </div>
          )}
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 468,
            borderLeft: "2px solid #D8D2C2",
            backgroundColor: "#F7F4EC",
            overflow: "hidden",
          }}
        >
          {thumb ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={thumb}
              alt=""
              width={468}
              height={630}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          ) : (
            <Sparkmark
              seed={slug}
              primaryViz={article?.primaryViz ?? null}
              palette={SPARK_LIGHT}
              size={360}
            />
          )}
        </div>
      </div>
    ),
    { ...size, fonts: fonts.length ? fonts : undefined }
  );
}
