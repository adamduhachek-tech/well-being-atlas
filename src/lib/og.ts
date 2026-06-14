/** Shared helpers for the generated Open Graph / share cards. */

export const OG_SIZE = { width: 1200, height: 630 };

export interface OgFont {
  name: string;
  data: ArrayBuffer;
  weight: 400 | 500 | 600 | 700;
  style?: "normal" | "italic";
}

async function loadGoogleFont(
  family: string,
  weight: number,
  italic = false
): Promise<ArrayBuffer | null> {
  try {
    const ital = italic ? 1 : 0;
    const css = await (
      await fetch(
        `https://fonts.googleapis.com/css2?family=${encodeURIComponent(
          family
        )}:ital,wght@${ital},${weight}`
      )
    ).text();
    const match = css.match(/src: url\((.+?)\) format\('(opentype|truetype)'\)/);
    if (!match) return null;
    const res = await fetch(match[1]);
    if (!res.ok) return null;
    return await res.arrayBuffer();
  } catch {
    return null;
  }
}

/** Newsreader (display) + IBM Plex Mono (label) — the site's two faces. */
export async function loadOgFonts(): Promise<OgFont[]> {
  const [display, mono] = await Promise.all([
    loadGoogleFont("Newsreader", 600),
    loadGoogleFont("IBM Plex Mono", 500),
  ]);
  return [
    display && { name: "Newsreader", data: display, weight: 600 as const },
    mono && { name: "IBM Plex Mono", data: mono, weight: 500 as const },
  ].filter(Boolean) as OgFont[];
}

/** Fetch a same-origin thumbnail and inline it as a data URL so it embeds
 *  reliably in the Satori render. Returns null on any failure. */
export async function fetchImageDataUrl(url: string): Promise<string | null> {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const buf = Buffer.from(await res.arrayBuffer());
    const type = res.headers.get("content-type") ?? "image/png";
    return `data:${type};base64,${buf.toString("base64")}`;
  } catch {
    return null;
  }
}
