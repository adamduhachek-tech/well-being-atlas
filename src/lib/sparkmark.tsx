/**
 * Sparkmarks: deterministic miniature chart abstractions, seeded by an
 * article's slug and shaped by its primary visualization type. They stand in
 * for thumbnails (the articles are self-contained D3 essays with no cover
 * images) and reappear on the generated OG cards.
 *
 * Rendered as plain SVG primitives so the same code works in React pages and
 * inside `ImageResponse` (satori).
 */

type Primitive =
  | { kind: "rect"; x: number; y: number; w: number; h: number; c: number; o?: number }
  | { kind: "circle"; cx: number; cy: number; r: number; c: number; o?: number }
  | { kind: "line"; x1: number; y1: number; x2: number; y2: number; c: number; sw: number; o?: number }
  | { kind: "path"; d: string; c: number; sw?: number; filled?: boolean; o?: number };

/** Palette slots: 0 ink, 1 vermillion, 2 gold, 3 slate blue, 4 faint ink. */
export const SPARK_LIGHT = ["#26231C", "#B5402C", "#C3953B", "#46618C", "#8C8676"];
export const SPARK_DARK = ["#E6E1D3", "#D96A52", "#D9B05E", "#7E9CC9", "#7E796C"];

function makeRng(seed: string): () => number {
  let h = 1779033703 ^ seed.length;
  for (let i = 0; i < seed.length; i++) {
    h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  let a = (h ^= h >>> 16) >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const r2 = (n: number) => Math.round(n * 100) / 100;

function wobblyPath(rng: () => number, x0: number, x1: number, yBase: number, amp: number, steps = 6): string {
  let d = `M ${x0} ${r2(yBase + (rng() - 0.5) * amp)}`;
  const dx = (x1 - x0) / steps;
  for (let i = 1; i <= steps; i++) {
    const x = x0 + dx * i;
    const y = yBase + (rng() - 0.5) * amp;
    d += ` L ${r2(x)} ${r2(y)}`;
  }
  return d;
}

type Family =
  | "grid"
  | "slope"
  | "lines"
  | "ridges"
  | "dots"
  | "fan"
  | "dumbbell"
  | "multiples";

function familyFor(primaryViz: string | null, rng: () => number): Family {
  const v = (primaryViz ?? "").toLowerCase();
  if (v.includes("choropleth")) return "grid";
  if (v.includes("slope") || v.includes("paired") || v.includes("trajector")) return "slope";
  if (v.includes("stream") || v.includes("time-series") || v.includes("ribbon")) return "lines";
  if (v.includes("distribution") || v.includes("ridge")) return "ridges";
  if (v.includes("scatter") || v.includes("relationship")) return "dots";
  if (v.includes("quantile") || v.includes("fan")) return "fan";
  if (v.includes("dumbbell")) return "dumbbell";
  if (v.includes("multiple") || v.includes("small")) return "multiples";
  const all: Family[] = ["grid", "slope", "lines", "ridges", "dots", "fan", "dumbbell", "multiples"];
  return all[Math.floor(rng() * all.length)];
}

export function sparkmarkPrimitives(seed: string, primaryViz: string | null): Primitive[] {
  const rng = makeRng(seed);
  const family = familyFor(primaryViz, rng);
  const accent = 1 + Math.floor(rng() * 3); // 1..3
  const prims: Primitive[] = [];

  switch (family) {
    case "grid": {
      const n = 5;
      const cell = 100 / n;
      for (let row = 0; row < n; row++) {
        for (let col = 0; col < n; col++) {
          const v = rng();
          if (v < 0.18) continue; // gaps read as coastline
          const c = v > 0.82 ? accent : v > 0.6 ? (accent % 3) + 1 : 4;
          prims.push({
            kind: "rect",
            x: r2(10 + col * cell),
            y: r2(10 + row * cell),
            w: r2(cell - 2),
            h: r2(cell - 2),
            c,
            o: v > 0.6 ? 1 : 0.25 + v * 0.5,
          });
        }
      }
      break;
    }
    case "slope": {
      const count = 5 + Math.floor(rng() * 3);
      const hero = Math.floor(rng() * count);
      for (let i = 0; i < count; i++) {
        const y1 = 20 + rng() * 80;
        const y2 = 20 + rng() * 80;
        const isHero = i === hero;
        prims.push({
          kind: "line", x1: 18, y1: r2(y1), x2: 102, y2: r2(y2),
          c: isHero ? accent : 4, sw: isHero ? 4 : 2, o: isHero ? 1 : 0.55,
        });
        prims.push({ kind: "circle", cx: 18, cy: r2(y1), r: isHero ? 4.5 : 3, c: isHero ? accent : 4, o: isHero ? 1 : 0.55 });
        prims.push({ kind: "circle", cx: 102, cy: r2(y2), r: isHero ? 4.5 : 3, c: isHero ? accent : 4, o: isHero ? 1 : 0.55 });
      }
      break;
    }
    case "lines": {
      const count = 3 + Math.floor(rng() * 2);
      for (let i = 0; i < count; i++) {
        const isHero = i === count - 1;
        prims.push({
          kind: "path",
          d: wobblyPath(rng, 12, 108, 30 + i * (60 / count), 26, 7),
          c: isHero ? accent : 4,
          sw: isHero ? 4 : 2.5,
          o: isHero ? 1 : 0.55,
        });
      }
      break;
    }
    case "ridges": {
      const rows = 4;
      for (let i = 0; i < rows; i++) {
        const yBase = 32 + i * 20;
        const peak = 14 + rng() * 16;
        const px = 30 + rng() * 60;
        const d = `M 12 ${yBase} C ${r2(px - 16)} ${yBase}, ${r2(px - 10)} ${r2(yBase - peak)}, ${r2(px)} ${r2(yBase - peak)} C ${r2(px + 10)} ${r2(yBase - peak)}, ${r2(px + 16)} ${yBase}, 108 ${yBase}`;
        prims.push({ kind: "path", d, c: i === rows - 1 ? accent : 0, sw: 2.5, o: 0.4 + (i / rows) * 0.6 });
      }
      break;
    }
    case "dots": {
      const count = 14 + Math.floor(rng() * 8);
      const heroIdx = Math.floor(rng() * count);
      for (let i = 0; i < count; i++) {
        const x = 15 + rng() * 90;
        const y = 105 - (x - 15) * 0.55 - rng() * 32;
        const isHero = i === heroIdx;
        prims.push({
          kind: "circle", cx: r2(x), cy: r2(Math.max(12, y)), r: isHero ? 6 : 2.5 + rng() * 2,
          c: isHero ? accent : 4, o: isHero ? 1 : 0.5 + rng() * 0.4,
        });
      }
      break;
    }
    case "fan": {
      const count = 5;
      for (let i = 0; i < count; i++) {
        const spread = (i - (count - 1) / 2) / ((count - 1) / 2);
        const yEnd = 60 + spread * (30 + rng() * 14);
        const mid = i === Math.floor(count / 2);
        prims.push({
          kind: "path",
          d: `M 14 ${r2(86 - rng() * 6)} C 50 ${r2(80 - rng() * 10)}, 78 ${r2(yEnd + spread * 8)}, 106 ${r2(yEnd)}`,
          c: mid ? accent : 4, sw: mid ? 4 : 2, o: mid ? 1 : 0.55,
        });
      }
      break;
    }
    case "dumbbell": {
      const rows = 5;
      for (let i = 0; i < rows; i++) {
        const y = 22 + i * 19;
        const xa = 16 + rng() * 35;
        const xb = xa + 18 + rng() * (96 - xa - 18);
        const isHero = i === Math.floor(rng() * rows);
        prims.push({ kind: "line", x1: r2(xa), y1: y, x2: r2(xb), y2: y, c: 4, sw: 2, o: 0.6 });
        prims.push({ kind: "circle", cx: r2(xa), cy: y, r: isHero ? 5 : 4, c: 4, o: 0.9 });
        prims.push({ kind: "circle", cx: r2(xb), cy: y, r: isHero ? 5 : 4, c: accent, o: 1 });
      }
      break;
    }
    case "multiples": {
      for (let row = 0; row < 2; row++) {
        for (let col = 0; col < 2; col++) {
          const x0 = 14 + col * 50;
          const y0 = 36 + row * 50;
          const hero = rng() > 0.6;
          prims.push({ kind: "line", x1: x0, y1: y0, x2: x0 + 40, y2: y0, c: 4, sw: 1, o: 0.5 });
          prims.push({
            kind: "path",
            d: wobblyPath(rng, x0, x0 + 40, y0 - 12, 18, 4),
            c: hero ? accent : 0, sw: 2.5, o: hero ? 1 : 0.7,
          });
        }
      }
      break;
    }
  }
  return prims;
}

export function Sparkmark({
  seed,
  primaryViz,
  palette = SPARK_LIGHT,
  size,
  className,
  useCssVars = false,
}: {
  seed: string;
  primaryViz: string | null;
  palette?: string[];
  size?: number;
  className?: string;
  /** On the site, colors come from CSS custom properties so dark mode works. */
  useCssVars?: boolean;
}) {
  const prims = sparkmarkPrimitives(seed, primaryViz);
  const color = (c: number) => (useCssVars ? `var(--spark-${c})` : palette[c]);

  return (
    <svg
      viewBox="0 0 120 120"
      width={size}
      height={size}
      className={className}
      role="img"
      aria-hidden="true"
    >
      {prims.map((p, i) => {
        switch (p.kind) {
          case "rect":
            return <rect key={i} x={p.x} y={p.y} width={p.w} height={p.h} fill={color(p.c)} opacity={p.o ?? 1} />;
          case "circle":
            return <circle key={i} cx={p.cx} cy={p.cy} r={p.r} fill={color(p.c)} opacity={p.o ?? 1} />;
          case "line":
            return (
              <line key={i} x1={p.x1} y1={p.y1} x2={p.x2} y2={p.y2} stroke={color(p.c)} strokeWidth={p.sw} strokeLinecap="round" opacity={p.o ?? 1} />
            );
          case "path":
            return (
              <path
                key={i}
                d={p.d}
                fill={p.filled ? color(p.c) : "none"}
                stroke={p.filled ? "none" : color(p.c)}
                strokeWidth={p.sw ?? 2}
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity={p.o ?? 1}
              />
            );
        }
      })}
    </svg>
  );
}
