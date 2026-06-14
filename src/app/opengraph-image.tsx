import { ImageResponse } from "next/og";
import { Sparkmark, SPARK_LIGHT } from "@/lib/sparkmark";
import { SITE_NAME } from "@/lib/site";
import { OG_SIZE, loadOgFonts } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = "image/png";
export const alt = `${SITE_NAME} — an index of data essays on well-being`;

// A spread of visualization families so the strip reads as a varied gallery.
const STRIP: { seed: string; viz: string }[] = [
  { seed: "atlas-choropleth", viz: "choropleth" },
  { seed: "atlas-slope", viz: "slope" },
  { seed: "atlas-series", viz: "time-series" },
  { seed: "atlas-scatter", viz: "scatter" },
  { seed: "atlas-dumbbell", viz: "dumbbell" },
];

export default async function SiteOgImage() {
  const fonts = await loadOgFonts();

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          backgroundColor: "#EFEBE0",
          padding: 56,
          fontFamily: "Newsreader, serif",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              borderTop: "5px solid #26231C",
              paddingTop: 16,
              fontFamily: "IBM Plex Mono, monospace",
              fontSize: 20,
              letterSpacing: 4,
              textTransform: "uppercase",
              color: "#5C574A",
            }}
          >
            <span style={{ color: "#B5402C" }}>{SITE_NAME}</span>
            <span>An index of data essays</span>
          </div>
          <div
            style={{
              fontSize: 88,
              lineHeight: 1.02,
              letterSpacing: -2,
              color: "#26231C",
              marginTop: 40,
            }}
          >
            Readings in Well-Being
          </div>
          <div
            style={{
              fontSize: 30,
              lineHeight: 1.4,
              color: "#5C574A",
              marginTop: 20,
              maxWidth: 880,
            }}
          >
            Independent, reproducible data essays on how people rate their lives
            — built from the GSS, Gallup, and the world value surveys.
          </div>
        </div>

        <div style={{ display: "flex", gap: 18 }}>
          {STRIP.map((s) => (
            <div
              key={s.seed}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 196,
                height: 132,
                backgroundColor: "#F7F4EC",
                border: "1px solid #D8D2C2",
                borderRadius: 8,
              }}
            >
              <Sparkmark
                seed={s.seed}
                primaryViz={s.viz}
                palette={SPARK_LIGHT}
                size={104}
              />
            </div>
          ))}
        </div>
      </div>
    ),
    { ...size, fonts: fonts.length ? fonts : undefined }
  );
}
