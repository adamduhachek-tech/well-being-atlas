/**
 * Shared, controlled tag vocabulary for the gallery. Both the manifest
 * generator (scripts/build-manifest.mjs) and the gallery UI import from here,
 * so filter chips and inferred tags can never drift out of sync.
 *
 * Two independent tag dimensions:
 *   - subtopic: what the article is about
 *   - scope:    geographic reach
 *   - source:   the survey family behind the data
 */

export type Subtopic =
  | "income"
  | "gender"
  | "race"
  | "religion"
  | "age"
  | "trust"
  | "community"
  | "politics"
  | "health"
  | "geography";

export type Scope = "US" | "Global" | "Europe";

export type Source =
  | "GSS"
  | "Gallup US Daily"
  | "Gallup World Poll"
  | "WVS"
  | "ESS";

export const SUBTOPICS: { key: Subtopic; label: string }[] = [
  { key: "income", label: "Income" },
  { key: "gender", label: "Gender" },
  { key: "race", label: "Race" },
  { key: "religion", label: "Religion" },
  { key: "age", label: "Age" },
  { key: "trust", label: "Trust" },
  { key: "community", label: "Community" },
  { key: "politics", label: "Politics" },
  { key: "health", label: "Health & Despair" },
  { key: "geography", label: "Geography" },
];

export const SCOPES: Scope[] = ["US", "Global", "Europe"];

export const SOURCES: Source[] = [
  "GSS",
  "Gallup US Daily",
  "Gallup World Poll",
  "WVS",
  "ESS",
];

/** Deterministic accent color per subtopic — used for chips and the
 *  gradient fallback when an article has no captured thumbnail. */
export const SUBTOPIC_COLOR: Record<Subtopic, string> = {
  income: "#2f7d6b",
  gender: "#b5402c",
  race: "#7a5ca8",
  religion: "#b07c2e",
  age: "#46618c",
  trust: "#3f7d9e",
  community: "#9a6a3c",
  politics: "#9c3b52",
  health: "#7a3b2e",
  geography: "#4a7a4a",
};

export const SUBTOPIC_LABEL: Record<Subtopic, string> = Object.fromEntries(
  SUBTOPICS.map((s) => [s.key, s.label])
) as Record<Subtopic, string>;

export interface Tags {
  subtopics: Subtopic[];
  scope: Scope[];
  sources: Source[];
}

const SUBTOPIC_PATTERNS: { key: Subtopic; re: RegExp }[] = [
  { key: "income", re: /\b(income|money|rich|wealth|gni|gdp|financ|poverty|poor|pay|earn|dollar|\$)\b/i },
  { key: "gender", re: /\b(gender|wom[ae]n|m[ae]n|female|male|\bsex\b|paradox)\b/i },
  { key: "race", re: /\b(race|racial|black|white|hispanic|latino|ethnic)\b/i },
  { key: "religion", re: /\b(relig|faith|church|worship|pray|normative|god|spiritual)\b/i },
  { key: "age", re: /\b(age|aged|ageing|aging|young|old|elder|generation|cohort|u-curve|midlife|life-?stage)\b/i },
  { key: "trust", re: /\b(trust|distrust|confidence)\b/i },
  { key: "community", re: /\b(communit|social capital|connection|neighbo|isolat|evening|generosity|civic|lonel|friend|belong)\b/i },
  { key: "politics", re: /\b(politic|vote|voting|election|flip|trump|obama|partisan|\bred\b|\bblue\b|ballot|democrat|republican)\b/i },
  { key: "health", re: /\b(despair|death|mortalit|suicide|depress|mental|\bpain\b|anxiet|sad|stress|worry|health|wellbeing crisis)\b/i },
  { key: "geography", re: /\b(geograph|county|counties|\bmap\b|\bstate\b|states|region|place|thriv|spatial|where)\b/i },
];

/** Infer tags from an article's title, description, and dataset label.
 *  Conservative: only the survey-family source it can prove from the dataset
 *  string drives scope, with a text fallback. Returns at least one subtopic. */
export function inferTags(input: {
  title?: string | null;
  description?: string | null;
  dataset?: string | null;
}): Tags {
  const text = [input.title, input.description].filter(Boolean).join(" ");
  const ds = (input.dataset ?? "").toLowerCase();

  const subtopics = SUBTOPIC_PATTERNS.filter((p) => p.re.test(text)).map(
    (p) => p.key
  );

  const sources: Source[] = [];
  const scope = new Set<Scope>();
  if (/general social survey|\bgss\b/.test(ds)) {
    sources.push("GSS");
    scope.add("US");
  }
  if (/gallup.*us daily|us daily|motherlode/.test(ds)) {
    sources.push("Gallup US Daily");
    scope.add("US");
  }
  if (/gallup world poll|world poll/.test(ds)) {
    sources.push("Gallup World Poll");
    scope.add("Global");
  }
  if (/world values survey|\bwvs\b/.test(ds)) {
    sources.push("WVS");
    scope.add("Global");
  }
  if (/european social survey|\bess\b/.test(ds)) {
    sources.push("ESS");
    scope.add("Europe");
  }

  // Scope fallbacks from text when the dataset string is unhelpful.
  if (scope.size === 0) {
    if (/\b(countr(y|ies)|world|global|nation)\b/i.test(text)) scope.add("Global");
    else if (/\b(europe|european)\b/i.test(text)) scope.add("Europe");
    else scope.add("US");
  }

  return {
    subtopics: subtopics.length ? subtopics : ["health"],
    scope: [...scope],
    sources,
  };
}
