# -*- coding: utf-8 -*-
"""Assemble index.html for 'The Two Clocks of Growing Old' from data.json."""
import json

d = json.load(open('data.json', encoding='utf-8'))

DATA = {
    "meta": d["meta"],
    "bands": d["bands"],
    "item_labels": d["item_labels"],
    "construct": d["construct"],
    "global_profiles": d["global_profiles"],
    "changes": d["changes"],
    "peaks": d["peaks"],
    "by_income": d["by_income"],
    "income_order": d["income_order"],
    "by_region": d["by_region"],
    "region_order": d["region_order"],
    "soc_summary": d["soc_summary"],
}
DATA_JSON = json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Two Clocks of Growing Old — what ageing does to a day, around the world</title>
<meta name="description" content="Gallup World Poll, 2005–2020, 2.3 million interviews in 165 countries: as people age, the mind's agitations — stress, anger — fall to lifetime lows, while pain, sadness and the body's limits climb. And whether old age is calm or anxious is sorted, above all, by money.">
<style>
  :root{
    --paper:#f7f3ec;
    --paper-deep:#ece4d7;
    --ink:#241c22;
    --ink-soft:#544850;
    --ink-faint:#897c84;
    --rule:#e0d6c9;
    --calm:#2f7d6b;          /* teal — the emotions that quiet with age */
    --calm-soft:#dcebe6;
    --burden:#b5462a;        /* burnt red — pain, sadness, the body's tax */
    --burden-soft:#f1ddd4;
    --worry:#8a3b6b;         /* plum — worry / money-anxiety */
    --max-col:760px;
    --max-wide:960px;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{margin:0;background:var(--paper);color:var(--ink);
    font-family:Georgia,"Iowan Old Style","Times New Roman",serif;
    font-size:18px;line-height:1.65;-webkit-font-smoothing:antialiased}
  .col{max-width:var(--max-col);margin:0 auto;padding:0 20px}
  .wide{max-width:var(--max-wide);margin:0 auto;padding:0 20px}

  header.masthead{padding:64px 0 8px}
  .kicker{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
    font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--burden);font-weight:700;margin:0 0 18px}
  h1{font-size:clamp(34px,6.2vw,60px);line-height:1.03;letter-spacing:-.015em;margin:0 0 18px;font-weight:700}
  h1 .hl{color:var(--burden)}
  h1 .hl2{color:var(--calm)}
  .dek{font-size:clamp(18px,2.6vw,22px);line-height:1.5;color:var(--ink-soft);margin:0 0 26px;max-width:680px;font-style:italic}
  .byline{font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;color:var(--ink-faint);
    border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:10px 0;display:flex;gap:18px;flex-wrap:wrap}
  .byline b{color:var(--ink-soft);font-weight:600}

  main p{margin:0 0 1.25em}
  main section{margin:44px 0}
  h2{font-size:clamp(23px,3.4vw,31px);line-height:1.2;margin:1.6em 0 .6em;letter-spacing:-.01em}
  .lede::first-letter{font-size:3.4em;float:left;line-height:.82;padding:.06em .12em 0 0;color:var(--burden);font-weight:700}

  .statstrip{display:flex;gap:0;flex-wrap:wrap;margin:38px 0;border-top:3px solid var(--ink);border-bottom:1px solid var(--rule)}
  .stat{flex:1 1 180px;padding:18px 18px 18px 0;min-width:150px}
  .stat + .stat{border-left:1px solid var(--rule);padding-left:18px}
  .stat .num{font-size:clamp(29px,4.4vw,40px);font-weight:700;letter-spacing:-.02em;line-height:1.05}
  .stat .num.calm{color:var(--calm)}
  .stat .num.burden{color:var(--burden)}
  .stat .lbl{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;color:var(--ink-soft);line-height:1.45;margin-top:6px}

  figure{margin:34px 0;padding:0}
  .fig-head{font-family:ui-sans-serif,system-ui,sans-serif;margin:0 0 4px}
  .fig-head .fig-title{font-size:17px;font-weight:700;letter-spacing:-.01em}
  .fig-head .fig-sub{font-size:13.5px;color:var(--ink-soft);margin-top:3px;line-height:1.5}
  .chart-wrap{position:relative;margin-top:14px}
  .chart-wrap svg{display:block;width:100%;height:auto}
  figcaption{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;color:var(--ink-faint);margin-top:10px;line-height:1.5;border-top:1px solid var(--rule);padding-top:8px}

  .controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-family:ui-sans-serif,system-ui,sans-serif;margin:14px 0 2px}
  .controls .grp-label{font-size:12px;color:var(--ink-faint);letter-spacing:.06em;text-transform:uppercase;margin-right:2px}
  button.pill{font-family:inherit;font-size:13px;font-weight:600;border:1.5px solid var(--rule);background:#fff;color:var(--ink-soft);
    border-radius:999px;padding:6px 13px;cursor:pointer;line-height:1;display:inline-flex;align-items:center;gap:7px;
    transition:border-color .15s, background .15s, color .15s}
  button.pill .dot{width:10px;height:10px;border-radius:50%;display:inline-block}
  button.pill[aria-pressed="true"]{border-color:var(--ink);background:var(--ink);color:var(--paper)}
  button.pill:hover{border-color:var(--ink-soft)}
  button.pill:focus-visible{outline:3px solid var(--calm);outline-offset:2px}

  .tip{position:absolute;pointer-events:none;z-index:5;background:var(--ink);color:var(--paper);
    font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;line-height:1.45;padding:8px 11px;border-radius:7px;max-width:240px;
    box-shadow:0 3px 14px rgba(36,28,34,.3);opacity:0;transition:opacity .12s}
  .tip b{font-size:13.5px}

  .pullquote{margin:40px 0;padding:6px 0 6px 22px;border-left:4px solid var(--calm);font-size:clamp(20px,3vw,26px);line-height:1.4;font-style:italic;color:var(--ink-soft)}
  .pullquote em{color:var(--burden);font-style:inherit}

  .note-box{background:var(--calm-soft);border-radius:10px;padding:16px 20px;font-family:ui-sans-serif,system-ui,sans-serif;font-size:14px;line-height:1.6;color:var(--ink-soft);margin:26px 0}
  .note-box b{color:var(--ink)}

  .legend{display:flex;gap:14px;flex-wrap:wrap;font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;color:var(--ink-soft);margin:8px 0 0}
  .legend span{display:inline-flex;align-items:center;gap:6px}
  .legend i{width:12px;height:3px;border-radius:2px;display:inline-block}

  footer{margin-top:70px;border-top:3px solid var(--ink);background:#efe7d9;padding:36px 0 60px}
  footer h2{font-size:20px;margin:0 0 14px}
  footer .col{font-family:ui-sans-serif,system-ui,sans-serif;font-size:13.5px;line-height:1.7;color:var(--ink-soft)}
  footer ul{padding-left:18px;margin:.5em 0}
  footer li{margin-bottom:.55em}
  footer cite{font-style:italic}
  code{background:var(--paper-deep);padding:1px 5px;border-radius:4px;font-size:.86em}

  text.axis-lab,.tick text{font-family:ui-sans-serif,system-ui,sans-serif}
  @media (max-width:520px){
    body{font-size:16.5px}
    .stat{flex:1 1 45%}
    .stat + .stat{border-left:none;padding-left:0}
  }
</style>
</head>
<body>

<header class="masthead">
  <div class="col">
    <p class="kicker">A world atlas of well-being · The texture of a day</p>
    <h1>The Two Clocks of <span class="hl2">Growing</span> <span class="hl">Old</span></h1>
    <p class="dek">Ageing does two opposite things to a day. It quiets the mind's agitations — stress and anger fall to the lowest levels of a whole life — while the body's pain and a slow sadness rise to their highest. Across 165 countries, both clocks run at once. What money decides is which one you hear loudest.</p>
    <div class="byline">
      <span><b>Data:</b> Gallup World Poll, 2005–2020</span>
      <span><b>N:</b> 2.28 million interviews · 165 countries</span>
      <span><b>Measure:</b> yesterday's feelings (experiential)</span>
    </div>
  </div>
</header>

<main>
  <div class="col">
    <section aria-label="Introduction">
      <p class="lede">The morning after each interview, before any talk of ladders or life as a whole, the Gallup World Poll asks something smaller and more honest: <em>how was yesterday?</em> Did you feel a lot of enjoyment? A lot of worry? Stress, anger, sadness, physical pain — yes or no, for the day just gone. Stack two million of those answers and sort them by age, and a pattern emerges that the famous life-satisfaction curves miss entirely. Growing older is not one trend. It is two, pulling in opposite directions.</p>
      <p>On one clock, the storms of feeling calm. Stress is highest not in old age but in the churning middle of life — the years of careers and dependents — and from there it falls away, reaching its lowest point among people over 65. Anger does the same: the old are the least likely of anyone to have spent yesterday angry. On the other clock, the body keeps its own time. Physical pain climbs steadily and without exception, from fewer than one in five young adults to nearly one in two of the oldest. Sadness rises with it; day-to-day enjoyment thins. The mind grows quieter even as the body grows heavier.</p>

      <div class="statstrip" role="group" aria-label="Key statistics">
        <div class="stat">
          <div class="num burden">18% → 47%</div>
          <div class="lbl">share reporting physical pain "yesterday", youngest to oldest — the body's tax, paid everywhere</div>
        </div>
        <div class="stat">
          <div class="num calm">lowest at 65+</div>
          <div class="lbl">stress and anger both bottom out in old age; stress peaks in the middle years, not the last ones</div>
        </div>
        <div class="stat">
          <div class="num">0.31 vs 0.47</div>
          <div class="lbl">old-age worry in rich vs poor countries — a clean crossover: the young worry alike, the old do not</div>
        </div>
      </div>

      <p>This piece is about the second question the survey asks — the <em>experiential</em> one, the felt texture of a day — and deliberately not about how people rate their lives overall, which moves to its own, more circumstantial rhythm. (Where the life-rating curve dips and recovers, and where it doesn't, is <a href="../u-curve-across-countries/" style="color:var(--burden)">a separate story</a>.) Held to the simple question of how yesterday actually <em>felt</em>, the human lifespan turns out to have a surprisingly consistent emotional architecture — and a few revealing places where it cracks along the lines of wealth and culture.</p>
    </section>

    <section aria-label="The two clocks">
      <h2>The storms calm; the body collects</h2>
      <p>Start with the hard feelings — the share of people, at each age, who say a given unpleasant state filled a lot of their day yesterday. Two of them, <strong style="color:var(--calm)">stress and anger</strong>, trace gentle arches that peak in the middle of life and subside toward its end. The other two, <strong style="color:var(--burden)">pain and sadness</strong>, only climb. <strong style="color:var(--worry)">Worry</strong> rises and then holds. Toggle to the good feelings and the mirror appears: enjoyment fades with age, and the sense of having someone to count on erodes — but being well-rested, ground down through the working years, recovers handsomely once those years are behind you. The oldest people in the world sleep, it seems, the most soundly.</p>
    </section>
  </div>

  <div class="wide">
    <figure aria-label="Global age profiles of daily feelings">
      <div class="fig-head">
        <div class="fig-title">What a day feels like, from 15 to 75 — the whole world averaged</div>
        <div class="fig-sub">Share of people who say they felt each state "a lot of the day yesterday", by age band, population-weighted across 165 countries. Switch between the hard feelings and the good ones; hover or tap any point.</div>
      </div>
      <div class="controls" id="clk-controls" role="toolbar" aria-label="Feeling-set and spotlight controls">
        <span class="grp-label">Show</span>
        <span id="clk-setpills"></span>
        <span class="grp-label" style="margin-left:10px">Spotlight</span>
        <span id="clk-itempills"></span>
      </div>
      <div class="chart-wrap" id="clk-chart">
        <div class="tip" id="clk-tip" role="status" aria-live="polite"></div>
      </div>
      <figcaption>Gallup World Poll, 2005–2020. Each line population-weights country band means by population (<code>ctry_pop_millions</code>); within-country weighting by <code>wgt</code>. Items are binary "a lot of the day yesterday" except the positive-affect index (a 0–1 mean of five positive items). “Hard feelings” share a 0–50% axis; “good feelings” a 50–100% axis. Band cells under 80 raw interviews were suppressed before aggregating.</figcaption>
    </figure>
  </div>

  <div class="col">
    <section aria-label="Reading the clocks">
      <p>The shape worth dwelling on is the arch of stress. It is tempting to imagine anxiety as the companion of frailty, mounting as the years run out. The data say the reverse: stress is the signature emotion of the <em>middle</em>, the decade or two when a person is most loaded with obligations and least free to set them down. Psychologists have a name for the calming that follows — the theory of <em>socioemotional selectivity</em>, the idea that as the horizon shortens, people prune their lives toward what soothes and away from what provokes. Whatever the mechanism, the fingerprint is unmistakable and global: by the seventies, the average person is less stressed, less angry, and better rested than they have been since adolescence.</p>

      <div class="pullquote">Old age, the world over, is the least angry and least stressed time of life. It is also the most pained. Both are true of the same people on the same morning.</div>

      <p>None of which the body forgives. Pain and the sense that health limits daily activity rise on an almost mechanical gradient — pain from 18 percent of the young to 47 percent of the old, functional limitation from 13 percent to 49 — and they are the one part of this story no culture and no income escapes. The emotional dividend of age is real, but it is collected in a body that is, by every measure here, increasingly hard to live in.</p>
    </section>

    <section aria-label="Worry and money">
      <h2>Worry keeps a ledger</h2>
      <p>If stress is about time, worry is about money — and here the single global average hides the most telling pattern in the data. Split the world's countries by income and ask, at each age, who spent yesterday worried. Among the young, the four income tiers are almost on top of one another; a worried twenty-year-old looks much the same in a rich country as in a poor one. Then the lines fan apart, and in old age they do something startling: they <em>cross</em> and reverse. In wealthy countries, worry crests in the striving years and then recedes — the over-65s are the <em>least</em> worried people in the rich world. In low-income countries it never recedes at all; it climbs to its lifetime peak in old age, when bodies fail and savings don't exist and there is no pension to fall back on.</p>
    </section>
  </div>

  <div class="wide">
    <figure aria-label="Worry by age and national income group">
      <div class="fig-head">
        <div class="fig-title">The young worry alike; the old are sorted by what their country can afford</div>
        <div class="fig-sub">Share worried "a lot of the day yesterday", by age band, within four World Bank income groups (population-weighted). Hover for values.</div>
      </div>
      <div class="chart-wrap" id="wry-chart">
        <div class="tip" id="wry-tip" role="status" aria-live="polite"></div>
      </div>
      <figcaption>Gallup World Poll, 2005–2020. Country income groups are World Bank classifications joined on ISO3. Each group line population-weights its member countries. The reversal is in <em>level</em>: rich and poor young adults worry at similar rates (~31–32%), but by 65+ the gap opens to roughly 0.31 vs 0.47 — about sixteen percentage points.</figcaption>
    </figure>
  </div>

  <div class="col">
    <section aria-label="The body's tax">
      <h2>The one tax nobody dodges</h2>
      <p>Set worry's crossover beside pain's gradient and the contrast is the whole argument in miniature. Worry <em>diverges</em> with age — the same starting point branching toward very different fates. Pain just <em>shifts</em> upward with hardship: the two poorest groups of countries sit well above the rich ones at every age, and all four climb the same staircase toward old age. A twenty-year-old in the poorest countries already reports as much daily pain as a forty-something in the richest. Wealth buys earlier comfort and a gentler slope — but not exemption: old age hurts more than youth in every economy on Earth, and even the cushioned high-income curve nearly doubles across a lifetime.</p>
    </section>
  </div>

  <div class="wide">
    <figure aria-label="Physical pain by age and national income group">
      <div class="fig-head">
        <div class="fig-title">Pain rises in every economy — and stays heaviest where life is hardest</div>
        <div class="fig-sub">Share reporting physical pain "a lot of the day yesterday", by age band, within four income groups (population-weighted).</div>
      </div>
      <div class="chart-wrap" id="pain-chart">
        <div class="tip" id="pain-tip" role="status" aria-live="polite"></div>
      </div>
      <figcaption>Gallup World Poll, 2005–2020. Unlike worry's reversal, the two poorer groups sit clearly above the richer ones at every age, and all four climb steeply toward old age — pain is shifted upward by hardship, not bent into a different shape (the upper-middle and high-income lines, both low, do cross late). A companion measure, "health problems limit your daily activity," rises even more steeply: 13% of the young to 49% of the old worldwide.</figcaption>
    </figure>
  </div>

  <div class="col">
    <section aria-label="Who catches the old">
      <h2>Who catches you when you fall</h2>
      <p>One more question reaches past feeling into circumstance: <em>if you were in trouble, do you have relatives or friends you can count on?</em> Almost everywhere, the answer dips through midlife — the busy, self-reliant middle — and then, in most of the world, recovers in old age as family closes back in. In Latin America, in Sub-Saharan Africa, across the rich West, the old are about as supported as the young, or nearly. The exception is sharp enough to see from across the room: in <strong>East Asia</strong>, the sense of having someone to count on falls through midlife and simply does not come back, sitting in old age at the lowest level of any region with a comparable income. Rapid ageing, shrinking families, and the long unwinding of multi-generational households have left a growing cohort of older East Asians materially developed and socially exposed — a pattern that reads, in this single question, like the demographic story of the region compressed into a line.</p>
    </section>
  </div>

  <div class="wide">
    <figure aria-label="Social support by age across world regions">
      <div class="fig-head">
        <div class="fig-title">"Someone to count on", across a lifetime — and the East Asian exception</div>
        <div class="fig-sub">Share saying they have relatives or friends to rely on in trouble, by age band, by region (population-weighted). Tap a region to spotlight it.</div>
      </div>
      <div class="controls" id="soc-controls" role="toolbar" aria-label="Region spotlight controls">
        <span class="grp-label">Spotlight</span>
        <span id="soc-pills"></span>
      </div>
      <div class="chart-wrap" id="soc-chart">
        <div class="tip" id="soc-tip" role="status" aria-live="polite"></div>
      </div>
      <figcaption>Gallup World Poll, 2005–2020. Region lines population-weight member countries. The "count on" item is self-reported and shaped by cultural response styles — East Asian respondents tend toward the middle of any scale and toward modesty about personal ties, which inflates the regional gap somewhat; treat the East Asian level as directional, though its failure to recover in old age is the genuinely distinctive feature.</figcaption>
    </figure>
  </div>

  <div class="col">
    <section aria-label="What it means">
      <h2>The shape of a life, felt from the inside</h2>
      <p>Put the four pictures together and a coherent account of ageing emerges — one that the headline life-satisfaction debates, fixated on whether the curve makes a U, tend to talk past. Subjectively, growing old is a trade. The mind hands back its agitation: less stress, less anger, more rest, a hard-won equanimity that arrives almost everywhere regardless of circumstance. The body, in exchange, asks for more: more pain, more limitation, a thinning of simple daily pleasure. That trade is the universal core, visible on every continent and at every income level.</p>
      <p>What varies — and varies enormously — is everything layered on top of it. Whether the equanimity of age is spent in security or in dread is decided largely by money: the same human tendency to worry less with age is granted to the rich and denied to the poor, who worry most precisely when they can do least about it. Whether old age is socially full or socially thin is decided largely by culture and demography, and here the world is not converging on the Western pattern so much as splitting, with East Asia's developed-but-exposed elders marking one emerging pole. The felt experience of the end of life, in other words, rests on a shared biological floor and a wildly uneven social ceiling.</p>
      <p>The usual cautions apply, and matter. These are <em>experiential</em> snapshots — a single day, remembered the next morning — not the considered verdicts people render on their lives as a whole, and the two genuinely diverge: the ladder of life-evaluation can sag in the very years when daily stress is also falling. The poll is a repeated cross-section, so an age "profile" blends the effect of getting older with the different histories of different birth cohorts. Self-reports of pain, worry and support are filtered through language and culture before they reach a spreadsheet. And gaps smaller than a few percentage points between regions should be read as ties. Set against all that, the central shape holds with unusual steadiness: two clocks, running in opposite directions, in nearly every country the survey reaches. Growing old is not getting happier or getting sadder. It is both at once — and the balance you strike depends, more than we like to admit, on where you happen to do it.</p>
    </section>
  </div>
</main>

<footer>
  <div class="col">
    <h2>Notes &amp; data</h2>
    <ul>
      <li><b>Source.</b> Gallup World Poll, interview-level microdata, 2005–2020 (<code>gallup_world.parquet</code>; 2,293,396 interviews, 165 countries with valid age and weight). The "yesterday" affect items — enjoyment, worry, stress, anger, sadness, physical pain, well-rested — are binary ("a lot of the day yesterday" = 1). "Someone to count on" and "health limits daily activity" are likewise yes/no.</li>
      <li><b>Construct.</b> This article is about <em>experiential</em> well-being — the felt quality of a recent day — kept deliberately separate from <em>evaluative</em> life-rating (the Cantril ladder), which appears only for contrast. The two are distinct psychological constructs and are never averaged together here.</li>
      <li><b>Coverage.</b> The Gallup World affect items have ~91–96% item response and, unlike the Gallup US Daily file, show no discontinuity around 2013, so the whole 2005–2020 period is pooled to maximise age coverage. (Item response by year was checked directly.)</li>
      <li><b>Weighting.</b> Within each country, interviews are weighted by Gallup's <code>wgt</code>. Every global, income-group and regional figure population-weights country band means by <code>ctry_pop_millions</code> — never an unweighted average of country averages.</li>
      <li><b>Age profiles &amp; suppression.</b> Six age bands, 15–24 to 65+. Country×band cells with fewer than 80 raw interviews are dropped before aggregation. Profiles pool all survey years by design, to isolate the age shape rather than the time trend.</li>
      <li><b>Cohorts, not just ageing.</b> The poll is a repeated cross-section; an age profile mixes the effect of growing older with differences between birth cohorts. The patterns here are best read as how well-being is <em>distributed across ages at a point in time</em>, which is what a person experiences as the social reality of each life-stage, rather than as a guaranteed individual trajectory.</li>
      <li><b>Response style.</b> Cross-cultural differences in scale use affect levels — notably East Asian central tendency on the "someone to count on" item. Treat cross-region <em>levels</em> as directional and read the <em>shapes</em> (and within-region age changes) as the firmer evidence.</li>
      <li><b>Reading.</b> A. Steptoe, A. Deaton &amp; A.A. Stone (2015), "Subjective wellbeing, health, and ageing," <cite>The Lancet</cite> 385:640–648. A.A. Stone, J.E. Schwartz, J.E. Broderick &amp; A. Deaton (2010), "A snapshot of the age distribution of psychological well-being in the United States," <cite>PNAS</cite> 107(22):9985–9990. L.L. Carstensen (2006), "The influence of a sense of time on human development," <cite>Science</cite> 312:1913–1915 (socioemotional selectivity). World Happiness Report chapters on age and on the social foundations of well-being.</li>
    </ul>
  </div>
</footer>

<script type="module">
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

const DATA = __DATA__;
const INK="#241c22", FAINT="#897c84", RULE="#e0d6c9", PAPER="#f7f3ec";
const CALM="#2f7d6b", BURDEN="#b5462a", WORRY="#8a3b6b";
const BANDS = DATA.bands;
const LABELS = DATA.item_labels;
const f2 = d3.format(".2f");
const fpct = v => Math.round(v*100)+"%";
const fpct1 = v => (v*100).toFixed(1)+"%";

function clearSvg(c){ c.querySelectorAll("svg").forEach(s=>s.remove()); }
function baseSvg(c,w,h,label,desc){
  const svg=d3.select(c).append("svg").attr("viewBox",`0 0 ${w} ${h}`).attr("role","img").attr("aria-label",label);
  svg.append("title").text(label); if(desc) svg.append("desc").text(desc); return svg;
}
function placeTip(tip,wrap,px,py,html){
  tip.innerHTML=html; tip.style.opacity=1;
  const ww=wrap.clientWidth, tw=tip.offsetWidth;
  let left=px-tw/2; left=Math.max(4,Math.min(ww-tw-4,left));
  tip.style.left=left+"px"; tip.style.top=Math.max(0,py-tip.offsetHeight-14)+"px";
}
function hideTip(tip){ tip.style.opacity=0; }

/* generic multi-line age-profile drawer */
function drawLines(opts){
  const {wrap,tip,series,yDom,fmt,focus,annot,desc,label}=opts;
  clearSvg(wrap); hideTip(tip);
  const w=Math.max(320,wrap.clientWidth);
  const h=Math.max(330,Math.min(470,w*0.56));
  const narrow=w<560;
  const m={t:24,r:narrow?16:140,b:46,l:46};
  const svg=baseSvg(wrap,w,h,label,desc);
  const x=d3.scalePoint().domain(BANDS).range([m.l,w-m.r]).padding(0.5);
  const y=d3.scaleLinear().domain(yDom).range([h-m.b,m.t]);
  const yt=y.ticks(6);
  svg.append("g").selectAll("line").data(yt).join("line")
    .attr("x1",m.l).attr("x2",w-m.r).attr("y1",d=>y(d)).attr("y2",d=>y(d)).attr("stroke",RULE);
  svg.append("g").selectAll("text").data(yt).join("text")
    .attr("x",m.l-8).attr("y",d=>y(d)).attr("dy","0.32em").attr("text-anchor","end")
    .attr("font-size",11).attr("fill",FAINT).attr("class","axis-lab").text(fmt);
  svg.append("g").selectAll("text").data(BANDS).join("text")
    .attr("x",d=>x(d)).attr("y",h-m.b+20).attr("text-anchor","middle")
    .attr("font-size",narrow?10:11).attr("fill",FAINT).attr("class","axis-lab").text(d=>d);
  svg.append("text").attr("x",(m.l+w-m.r)/2).attr("y",h-8).attr("text-anchor","middle")
    .attr("font-size",11.5).attr("fill",FAINT).attr("class","axis-lab").text("Age band");

  const line=d3.line().x(d=>x(d.band)).y(d=>y(d.v)).curve(d3.curveMonotoneX).defined(d=>d.v!=null);
  const order=series.filter(s=>s.key!==focus).concat(series.filter(s=>s.key===focus));
  for(const s of order){
    const op = focus==null?1:(s.key===focus?1:0.16);
    const sw = s.key===focus?4:(s.emphasis?3.2:2.4);
    const pts=BANDS.map((b,i)=>({band:b,v:s.values[i]}));
    svg.append("path").datum(pts).attr("fill","none").attr("stroke",s.color)
      .attr("stroke-width",sw).attr("stroke-opacity",op).attr("stroke-linecap","round")
      .attr("stroke-dasharray",s.dash||null).attr("d",line);
    svg.append("g").selectAll("circle").data(pts.filter(p=>p.v!=null)).join("circle")
      .attr("cx",d=>x(d.band)).attr("cy",d=>y(d.v)).attr("r",s.key===focus?3.8:2.8)
      .attr("fill",s.color).attr("fill-opacity",op).attr("stroke",PAPER).attr("stroke-width",1);
    if(!narrow){
      const last=pts.filter(p=>p.v!=null).slice(-1)[0];
      svg.append("text").attr("x",x(last.band)+10).attr("y",y(last.v)).attr("dy","0.32em")
        .attr("font-size",12).attr("font-weight",s.key===focus||focus==null?700:500)
        .attr("fill",s.color).attr("fill-opacity",Math.max(0.5,op)).attr("class","axis-lab").text(s.label);
    }
  }
  if(annot) annot(svg,x,y,narrow);

  const flat=[];
  series.forEach(s=>BANDS.forEach((b,i)=>{ if(s.values[i]!=null) flat.push({band:b,v:s.values[i],label:s.label,color:s.color}); }));
  svg.append("rect").attr("x",m.l).attr("y",m.t).attr("width",w-m.l-m.r).attr("height",h-m.t-m.b)
    .attr("fill","transparent")
    .on("mousemove touchmove",function(ev){
      const [mx,my]=d3.pointer(ev,this.ownerSVGElement);
      const near=d3.least(flat,p=>Math.hypot(x(p.band)-mx,y(p.v)-my));
      if(!near||Math.hypot(x(near.band)-mx,y(near.v)-my)>46){hideTip(tip);return;}
      const sc=wrap.clientWidth/w;
      placeTip(tip,wrap,x(near.band)*sc,y(near.v)*sc,
        `<b style="color:#fff">${near.label}</b><br>ages ${near.band}<br><b>${fmt(near.v)}</b>`);
    })
    .on("mouseleave touchend",()=>hideTip(tip));
}

/* =========================================================
   1. THE TWO CLOCKS (toggle hard / good)
   ========================================================= */
const clkWrap=document.getElementById("clk-chart"), clkTip=document.getElementById("clk-tip");
const SETS={
  hard:{
    items:[
      {key:"physical_pain",color:BURDEN,emphasis:true},
      {key:"sadness",color:"#cf7d4f"},
      {key:"worry",color:WORRY},
      {key:"stress",color:CALM,emphasis:true},
      {key:"anger",color:"#5aa896"},
    ],
    yDom:[0.12,0.50],fmt:fpct
  },
  good:{
    items:[
      {key:"enjoyment",color:"#c98a3a",emphasis:true},
      {key:"well_rested",color:"#6f9bbf"},
      {key:"social_support",color:CALM,emphasis:true},
      {key:"pos_affect",color:BURDEN,dash:"1 5"},
    ],
    yDom:[0.55,0.92],fmt:fpct
  }
};
let clkSet="hard", clkFocus=null;
function clkSeries(){
  const set=SETS[clkSet];
  return set.items.map(it=>({key:it.key,color:it.color,emphasis:it.emphasis,dash:it.dash,
    label:LABELS[it.key],values:DATA.global_profiles[it.key]}));
}
function drawClocks(){
  const set=SETS[clkSet];
  drawLines({wrap:clkWrap,tip:clkTip,series:clkSeries(),yDom:set.yDom,fmt:set.fmt,focus:clkFocus,
    label:"Line chart of how common each daily feeling is by age band, worldwide.",
    desc: clkSet==="hard"
      ?"Physical pain and sadness climb with age; stress and anger arch up in midlife then fall to lifetime lows in old age."
      :"Enjoyment and social support thin with age while well-rested dips in midlife and recovers in old age.",
    annot:(svg,x,y,narrow)=>{
      if(clkSet==="hard" && (clkFocus==null||clkFocus==="physical_pain")){
        const p=DATA.global_profiles["physical_pain"];
        svg.append("text").attr("x",x("55-64")).attr("y",y(p[4])-12).attr("text-anchor","middle")
          .attr("font-size",11).attr("font-weight",700).attr("fill",BURDEN).attr("class","axis-lab").text("pain climbs");
      }
      if(clkSet==="hard" && (clkFocus==null||clkFocus==="stress")){
        const p=DATA.global_profiles["stress"];
        svg.append("text").attr("x",x("35-44")).attr("y",y(p[2])-10).attr("text-anchor","middle")
          .attr("font-size",11).attr("font-weight",700).attr("fill",CALM).attr("class","axis-lab").text("stress peaks midlife");
      }
    }});
}
function buildClkControls(){
  const setHost=document.getElementById("clk-setpills");
  setHost.innerHTML="";
  for(const [k,lab] of [["hard","The hard feelings"],["good","The good feelings"]]){
    const b=document.createElement("button"); b.className="pill"; b.textContent=lab;
    b.setAttribute("aria-pressed",String(clkSet===k));
    b.addEventListener("click",()=>{clkSet=k; clkFocus=null; buildClkControls(); drawClocks();});
    setHost.appendChild(b);
  }
  const itemHost=document.getElementById("clk-itempills");
  itemHost.innerHTML="";
  for(const it of SETS[clkSet].items){
    const b=document.createElement("button"); b.className="pill";
    b.setAttribute("aria-pressed",String(clkFocus===it.key));
    b.innerHTML=`<span class="dot" style="background:${it.color}"></span>${LABELS[it.key]}`;
    b.addEventListener("click",()=>{clkFocus=clkFocus===it.key?null:it.key; buildClkControls(); drawClocks();});
    itemHost.appendChild(b);
  }
}

/* =========================================================
   2 & 3. INCOME-GROUP LINE CHARTS (worry, pain)
   ========================================================= */
const INCOME_COLOR={
  "Low income":"#b5462a","Lower middle income":"#d4884a",
  "Upper middle income":"#6f9bbf","High income":"#2f7d6b"
};
const INCOME_SHORT={
  "Low income":"Low income","Lower middle income":"Lower-middle",
  "Upper middle income":"Upper-middle","High income":"High income"
};
function incomeSeries(item){
  return DATA.income_order.map(inc=>({key:inc,color:INCOME_COLOR[inc],
    label:INCOME_SHORT[inc],values:DATA.by_income[item][inc],
    emphasis:(inc==="High income"||inc==="Low income")}));
}
const wryWrap=document.getElementById("wry-chart"), wryTip=document.getElementById("wry-tip");
function drawWorry(){
  drawLines({wrap:wryWrap,tip:wryTip,series:incomeSeries("worry"),yDom:[0.22,0.49],fmt:fpct,focus:null,
    label:"Worry by age within four national income groups; the rich and poor lines cross in old age.",
    desc:"In high-income countries worry falls after midlife; in low-income countries it climbs to a lifetime peak in old age.",
    annot:(svg,x,y)=>{
      const hi=DATA.by_income.worry["High income"], lo=DATA.by_income.worry["Low income"];
      svg.append("text").attr("x",x("65+")).attr("y",y(lo[5])-10).attr("text-anchor","end")
        .attr("font-size",11).attr("font-weight",700).attr("fill","#b5462a").attr("class","axis-lab").text("poor: worry peaks");
      svg.append("text").attr("x",x("65+")).attr("y",y(hi[5])+16).attr("text-anchor","end")
        .attr("font-size",11).attr("font-weight",700).attr("fill","#2f7d6b").attr("class","axis-lab").text("rich: worry eases");
    }});
}
const painWrap=document.getElementById("pain-chart"), painTip=document.getElementById("pain-tip");
function drawPain(){
  drawLines({wrap:painWrap,tip:painTip,series:incomeSeries("physical_pain"),yDom:[0.1,0.62],fmt:fpct,focus:null,
    label:"Physical pain by age within four national income groups; all rise in near-parallel.",
    desc:"Pain rises with age in every income group; poorer groups sit higher at every age but the lines climb in parallel."});
}

/* =========================================================
   4. SOCIAL SUPPORT BY REGION
   ========================================================= */
const REGION_COLOR={
  "Northern America":"#2f7d6b","Australia-New Zealand":"#3f9e86","European Union":"#4a7ba6",
  "Europe-Other":"#7d9cb8","Commonwealth of Independent States":"#8a3b6b","East Asia":"#b5462a",
  "Southeast Asia":"#d08a4f","South Asia":"#a9772e","Latin America and the Caribbean":"#c98a3a",
  "Middle East and North Africa":"#6b8e3a","Sub-Saharan Africa":"#9a6a4a"
};
const REGION_SHORT={
  "Northern America":"N. America","Australia-New Zealand":"Australia–NZ","European Union":"EU",
  "Europe-Other":"Other Europe","Commonwealth of Independent States":"Post-Soviet","East Asia":"East Asia",
  "Southeast Asia":"SE Asia","South Asia":"South Asia","Latin America and the Caribbean":"Latin America",
  "Middle East and North Africa":"MENA","Sub-Saharan Africa":"Sub-Saharan Africa"
};
const socWrap=document.getElementById("soc-chart"), socTip=document.getElementById("soc-tip");
let socFocus="East Asia";
function socSeries(){
  return DATA.region_order.map(reg=>({key:reg,color:REGION_COLOR[reg]||FAINT,
    label:REGION_SHORT[reg]||reg,values:DATA.by_region.social_support[reg],
    emphasis:(reg==="East Asia")}));
}
function drawSoc(){
  drawLines({wrap:socWrap,tip:socTip,series:socSeries(),yDom:[0.5,1.0],fmt:fpct,focus:socFocus,
    label:"Share with someone to count on, by age, across world regions; East Asia fails to recover in old age.",
    desc:"Most regions dip in midlife and recover in old age; East Asia keeps falling and stays lowest among comparably rich regions."});
}
function buildSocPills(){
  const host=document.getElementById("soc-pills"); host.innerHTML="";
  // a compact subset of pills to spotlight, plus 'All'
  const picks=["East Asia","Latin America and the Caribbean","Sub-Saharan Africa","European Union","Commonwealth of Independent States"];
  const all=document.createElement("button"); all.className="pill"; all.textContent="All regions";
  all.setAttribute("aria-pressed",String(socFocus==null));
  all.addEventListener("click",()=>{socFocus=null; buildSocPills(); drawSoc();});
  host.appendChild(all);
  for(const reg of picks){
    const b=document.createElement("button"); b.className="pill";
    b.setAttribute("aria-pressed",String(socFocus===reg));
    b.innerHTML=`<span class="dot" style="background:${REGION_COLOR[reg]}"></span>${REGION_SHORT[reg]}`;
    b.addEventListener("click",()=>{socFocus=socFocus===reg?null:reg; buildSocPills(); drawSoc();});
    host.appendChild(b);
  }
}

/* boot + resize */
buildClkControls(); drawClocks();
drawWorry(); drawPain();
buildSocPills(); drawSoc();
let raf=null;
const ro=new ResizeObserver(()=>{
  if(raf)cancelAnimationFrame(raf);
  raf=requestAnimationFrame(()=>{drawClocks(); drawWorry(); drawPain(); drawSoc();});
});
ro.observe(clkWrap);
</script>
</body>
</html>
"""

html = HTML.replace("__DATA__", DATA_JSON)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("wrote index.html (%d bytes)" % len(html))
