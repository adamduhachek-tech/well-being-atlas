import { ImageResponse } from "next/og";
import { getArticle } from "@/lib/articles";
import { Sparkmark, SPARK_LIGHT } from "@/lib/sparkmark";
import { SITE_NAME } from "@/lib/site";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "Article card";

async function loadGoogleFont(
  family: string,
  weight: number,
  italic = false
): Promise<ArrayBuffer | null> {
  try {
    const ital = italic ? 1 : 0;
    const css = await (
      await fetch(
        `https://fonts.googleapis.com/css2?family=${encodeURIComponent(family)}:ital,wght@${ital},${weight}`
      )
    ).text();
    const match = css.match(
      /src: url\((.+?)\) format\('(opentype|truetype)'\)/
    );
    if (!match) return null;
    const res = await fetch(match[1]);
    if (!res.ok) return null;
    return await res.arrayBuffer();
  } catch {
    return null;
  }
}

export default async function OgImage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const article = await getArticle(slug);

  const [display, mono] = await Promise.all([
    loadGoogleFont("Newsreader", 500),
    loadGoogleFont("IBM Plex Mono", 500),
  ]);
  const fonts = [
    display && { name: "Newsreader", data: display, weight: 500 as const },
    mono && { name: "IBM Plex Mono", data: mono, weight: 500 as const },
  ].filter(Boolean) as { name: string; data: ArrayBuffer; weight: 500 }[];

  const title = article?.title ?? SITE_NAME;
  const meta = [
    article?.dataset,
    article?.readingMinutes ? `${article.readingMinutes} min read` : null,
  ]
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
          padding: 56,
          fontFamily: "Newsreader, serif",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            flex: 1,
            paddingRight: 48,
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
                fontSize: title.length > 60 ? 56 : 68,
                lineHeight: 1.05,
                color: "#26231C",
                marginTop: 28,
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
                fontSize: 20,
                letterSpacing: 2,
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
            width: 420,
            backgroundColor: "#F7F4EC",
            border: "2px solid #D8D2C2",
          }}
        >
          <Sparkmark
            seed={slug}
            primaryViz={article?.primaryViz ?? null}
            palette={SPARK_LIGHT}
            size={360}
          />
        </div>
      </div>
    ),
    { ...size, fonts: fonts.length ? fonts : undefined }
  );
}
