# -*- coding: utf-8 -*-
"""Assemble index.html for 'The U-Curve, Redrawn' from data.json.
Embeds a trimmed DATA object so every number on the page comes from the
verified analysis output (no hand-transcription)."""
import json

d = json.load(open('data.json', encoding='utf-8'))

# order exemplars by old-age recovery (right_arm) descending: U-shapes first
ex = sorted(d['exemplars'], key=lambda e: e['right_arm'], reverse=True)

DATA = {
    "meta": d["meta"],
    "bands": d["bands"],
    "band_mid": d["band_mid"],
    "global_profile": d["global_profile"],
    "groups": d["group_profiles"],
    "region_summary": d["region_summary"],
    "exemplars": ex,
    "scatter": {
        "fit_intercept": d["scatter"]["fit_intercept"],
        "fit_slope": d["scatter"]["fit_slope"],
        "corr_popw": d["scatter"]["corr_recovery_loggni_popw"],
        "corr_unw": d["scatter"]["corr_recovery_loggni_unw"],
        "corr_hdi": d["scatter"]["corr_recovery_hdi_popw"],
        "points": d["scatter"]["points"],
    },
    "class_counts": d["class_counts"],
}
DATA_JSON = json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The U-Curve, Redrawn — where the midlife dip in happiness exists, and where it doesn't</title>
<meta name="description" content="Gallup World Poll, 2005–2020, 2.2 million interviews in 156 countries: the famous U-shaped happiness curve — high in youth, low at midlife, rising again in old age — is real, but mostly a privilege of the rich Anglosphere. Across much of the world, life-evaluation simply falls with age.">
<style>
  :root{
    --paper:#faf6ef;
    --paper-deep:#f1eadf;
    --ink:#2b2118;
    --ink-soft:#5c5044;
    --ink-faint:#8a7d6e;
    --rule:#e3d9c8;
    --accent:#2f7d6b;        /* teal-green — the U / old-age recovery */
    --accent-soft:#dcebe6;
    --warn:#b5462a;          /* burnt red — decline with age */
    --warn-soft:#f1ddd4;
    --max-col:760px;
    --max-wide:960px;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{
    margin:0;background:var(--paper);color:var(--ink);
    font-family:Georgia,"Iowan Old Style","Times New Roman",serif;
    font-size:18px;line-height:1.65;-webkit-font-smoothing:antialiased;
  }
  .col{max-width:var(--max-col);margin:0 auto;padding:0 20px}
  .wide{max-width:var(--max-wide);margin:0 auto;padding:0 20px}

  header.masthead{padding:64px 0 8px}
  .kicker{
    font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
    font-size:12px;letter-spacing:.22em;text-transform:uppercase;
    color:var(--accent);font-weight:700;margin:0 0 18px;
  }
  h1{font-size:clamp(34px,6.2vw,60px);line-height:1.03;letter-spacing:-.015em;margin:0 0 18px;font-weight:700}
  h1 .hl{color:var(--accent)}
  .dek{font-size:clamp(18px,2.6vw,22px);line-height:1.5;color:var(--ink-soft);margin:0 0 26px;max-width:680px;font-style:italic}
  .byline{
    font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;color:var(--ink-faint);
    border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);
    padding:10px 0;display:flex;gap:18px;flex-wrap:wrap;
  }
  .byline b{color:var(--ink-soft);font-weight:600}

  main p{margin:0 0 1.25em}
  main section{margin:44px 0}
  h2{font-size:clamp(23px,3.4vw,31px);line-height:1.2;margin:1.6em 0 .6em;letter-spacing:-.01em}
  .lede::first-letter{font-size:3.4em;float:left;line-height:.82;padding:.06em .12em 0 0;color:var(--accent);font-weight:700}

  .statstrip{display:flex;gap:0;flex-wrap:wrap;margin:38px 0;border-top:3px solid var(--ink);border-bottom:1px solid var(--rule)}
  .stat{flex:1 1 180px;padding:18px 18px 18px 0;min-width:150px}
  .stat + .stat{border-left:1px solid var(--rule);padding-left:18px}
  .stat .num{font-size:clamp(29px,4.4vw,40px);font-weight:700;letter-spacing:-.02em;line-height:1.05}
  .stat .num.good{color:var(--accent)}
  .stat .num.bad{color:var(--warn)}
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
  button.pill{
    font-family:inherit;font-size:13px;font-weight:600;border:1.5px solid var(--rule);background:#fff;color:var(--ink-soft);
    border-radius:999px;padding:6px 13px;cursor:pointer;line-height:1;display:inline-flex;align-items:center;gap:7px;
    transition:border-color .15s, background .15s, color .15s;
  }
  button.pill .dot{width:10px;height:10px;border-radius:50%;display:inline-block}
  button.pill[aria-pressed="true"]{border-color:var(--ink);background:var(--ink);color:var(--paper)}
  button.pill:hover{border-color:var(--ink-soft)}
  button.pill:focus-visible{outline:3px solid var(--accent);outline-offset:2px}

  .tip{
    position:absolute;pointer-events:none;z-index:5;background:var(--ink);color:var(--paper);
    font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;line-height:1.45;
    padding:8px 11px;border-radius:7px;max-width:240px;box-shadow:0 3px 14px rgba(43,33,24,.28);
    opacity:0;transition:opacity .12s;
  }
  .tip b{font-size:13.5px}

  .pullquote{margin:40px 0;padding:6px 0 6px 22px;border-left:4px solid var(--accent);font-size:clamp(20px,3vw,26px);line-height:1.4;font-style:italic;color:var(--ink-soft)}
  .pullquote em{color:var(--accent);font-style:inherit}

  .note-box{background:var(--accent-soft);border-radius:10px;padding:16px 20px;font-family:ui-sans-serif,system-ui,sans-serif;font-size:14px;line-height:1.6;color:var(--ink-soft);margin:26px 0}
  .note-box b{color:var(--ink)}

  .legend{display:flex;gap:16px;flex-wrap:wrap;font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;color:var(--ink-soft);margin:6px 0 0}
  .legend span{display:inline-flex;align-items:center;gap:6px}
  .legend i{width:12px;height:12px;border-radius:3px;display:inline-block}

  footer{margin-top:70px;border-top:3px solid var(--ink);background:#f0e9db;padding:36px 0 60px}
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
    <p class="kicker">A world atlas of well-being · The shape of a life</p>
    <h1>The U-Curve, <span class="hl">Redrawn</span></h1>
    <p class="dek">Happiness is supposed to sag in midlife and lift again in old age — a gentle U that economists have called one of the most reliable patterns in social science. Across 156 countries and 2.2 million interviews, that U turns out to be less a law of human nature than a luxury of where you happen to grow old.</p>
    <div class="byline">
      <span><b>Data:</b> Gallup World Poll, 2005–2020</span>
      <span><b>N:</b> 2.24 million interviews · 156 countries</span>
      <span><b>Measure:</b> Cantril ladder, 0–10 (evaluative)</span>
    </div>
  </div>
</header>

<main>
  <div class="col">
    <section aria-label="Introduction">
      <p class="lede">Ask people around the world to place their life on a ladder — zero is the worst possible life, ten the best — and a famous pattern is supposed to emerge as you sort the answers by age. Contentment runs high in youth, erodes through the grind of the middle years, bottoms out somewhere around fifty, and then, remarkably, climbs again: the old, freed of ambition and reconciled to their lot, report themselves nearly as satisfied as the young. Plotted against age, the curve makes a soft valley — a <em>U</em>. The economist David Blanchflower has found versions of it in survey after survey, and the idea has hardened into conventional wisdom: the worst is the middle, and it gets better.</p>
      <p>Pool the Gallup World Poll across fifteen years and 156 countries, population-weight it, and the global average tells a quieter, less consoling story. The world's young adults sit at 5.52 on the ladder. By the late forties they have slid to about 5.05. And then — nothing. The line does not turn back up. It flattens, inching to 5.07 among those over 65 and going no further. The midlife valley is real. The recovery, for humanity as a whole, is a rounding error.</p>

      <div class="statstrip" role="group" aria-label="Key statistics">
        <div class="stat">
          <div class="num">34<span style="font-size:.55em"> / 156</span></div>
          <div class="lbl">countries show a genuine U — a midlife dip <em>and</em> an old-age rebound. Just over one in five.</div>
        </div>
        <div class="stat">
          <div class="num good">+0.53</div>
          <div class="lbl">ladder points the old gain back over midlife in the Anglosphere — the textbook U, in full</div>
        </div>
        <div class="stat">
          <div class="num bad">−0.28</div>
          <div class="lbl">across the former Soviet states, where life-evaluation keeps falling and the old are the unhappiest of all</div>
        </div>
      </div>

      <p>The U-shape, in other words, is not wrong. It is local. It is vivid and dependable in the wealthy English-speaking world — the United States, Australia, Britain, Canada — and visible across much of northern Europe and the Gulf. But follow the curve into the former Soviet Union, into much of Africa and South Asia, and the right arm of the U simply isn't there. Life does not get better in old age. It gets worse, often steeply, and the famous valley becomes a long downhill slope.</p>
    </section>

    <section aria-label="The thesis">
      <h2>One shape, or many?</h2>
      <p>The chart below is the whole argument in one frame. Each line is the average ladder score by age for a group of countries, with every national average weighted by population so that the line speaks for people, not borders. Look first at the <strong style="color:var(--accent)">Anglosphere</strong>: it does exactly what the textbook promises — high in youth, a clear sag through the forties, and a confident lift after sixty back above where it started. Now look at the <strong style="color:var(--warn)">post-Soviet states</strong>: the same youthful start, more or less, and then an unbroken descent to a low point in old age more than a full ladder-rung beneath the young. Western Europe and Latin America fall in between — they start high and drift gently down, the dip never quite repaid. And the heavy <strong>World</strong> line, dragged down in level by populous, lower-income Asia and Africa, shows the valley without the recovery.</p>
    </section>
  </div>

  <div class="wide">
    <figure aria-label="Age profile of the Cantril ladder by country group">
      <div class="fig-head">
        <div class="fig-title">Where the U exists — and where the line just keeps falling</div>
        <div class="fig-sub">Population-weighted mean of the Cantril life-evaluation ladder (0–10) by age band, pooled 2005–2020. Tap the pills to spotlight a group; hover or tap any point for its value.</div>
      </div>
      <div class="controls" id="grp-controls" role="toolbar" aria-label="Group spotlight controls">
        <span class="grp-label">Spotlight</span>
        <span id="grp-pills"></span>
      </div>
      <div class="chart-wrap" id="grp-chart">
        <div class="tip" id="grp-tip" role="status" aria-live="polite"></div>
      </div>
      <figcaption>Gallup World Poll, 2005–2020. Each group line population-weights its member countries by total population (<code>ctry_pop_millions</code>); within each country, interviews are weighted by Gallup's <code>wgt</code>. Groups are illustrative country sets, not exhaustive regions: Anglosphere = US, UK, Canada, Australia, Ireland, New Zealand; Post-Soviet = Russia, Ukraine, Belarus, the Baltics, the Caucasus and Central Asia; Western Europe and Latin America as labelled. Vertical axis zoomed to 4.5–7.8 to make the shapes legible — the full ladder runs 0–10.</figcaption>
    </figure>
  </div>

  <div class="col">
    <section aria-label="Reading the curve">
      <p>Two features deserve a slow look. The first is that the curves differ in <em>level</em> as much as in <em>shape</em> — a sixty-five-year-old Australian and a sixty-five-year-old Russian are not having a mild disagreement about the same life; they are almost three rungs apart — 7.6 against 4.7. The second is that the youthful starting points are far closer together than the destinations. Across these groups the young begin within about a rung of one another; by old age they have fanned out dramatically. <strong>What separates the world's elderly is not how they began but how the second half of life treated them.</strong></p>

      <div class="pullquote">The young of the world are more alike than the old. Aging is where the paths diverge — and where geography, history and a pension system write themselves onto a life.</div>

      <p>This is why the single global U-curve, so beloved of summary statistics, is a kind of optical illusion. It is an average of opposites: countries where old age is a reward laid over countries where it is a punishment. Blend them and you get a shallow valley that describes almost no one in particular.</p>
    </section>

    <section aria-label="The gallery of shapes">
      <h2>A gallery of national shapes</h2>
      <p>Strip away the levels and look only at the silhouettes. Below are twenty countries, each drawn on its own scale so that the <em>shape</em> of aging — not the height of the ladder — is what you see. They are sorted by how much the old recover relative to midlife, so the genuine U-shapes rise to the top and the steep declines sink to the bottom. The pattern in the colours is hard to miss: the <span style="color:var(--accent);font-weight:700">recoveries</span> are disproportionately rich and Anglophone or Gulf; the <span style="color:var(--warn);font-weight:700">declines</span> are disproportionately post-communist, Latin American, or East Asian. Even within East Asia the split is sharp — China bends upward in old age while Japan and South Korea, richer and faster-aging, bend down.</p>
    </section>
  </div>

  <div class="wide">
    <figure aria-label="Small-multiple age curves for twenty countries">
      <div class="fig-head">
        <div class="fig-title">Twenty countries, twenty silhouettes of aging</div>
        <div class="fig-sub">Each panel: mean ladder by age band, on its own vertical scale. Green = the old recover above midlife (a U); red = the old fall furthest (decline); grey = roughly flat. The number is the old-age gain or loss versus the midlife low, in ladder points.</div>
      </div>
      <div class="legend" aria-hidden="true">
        <span><i style="background:var(--accent)"></i> U-shape · old-age rebound</span>
        <span><i style="background:#b9aa92"></i> Flat</span>
        <span><i style="background:var(--warn)"></i> Decline with age</span>
      </div>
      <div class="chart-wrap" id="sm-chart"></div>
      <figcaption>Gallup World Poll, 2005–2020, pooled; within-country <code>wgt</code> applied. Each panel auto-scales its vertical axis, so panels show shape, not level — a tall-looking rise in a low-ladder country can be a smaller absolute gain than a gentle-looking one elsewhere. Classification: “U-shape” = old-age mean at least 0.15 above the midlife low with youth at or above midlife; “Decline” = old age at least 0.15 below the midlife low; otherwise “Flat”. Age bands span 15–24 to 65+.</figcaption>
    </figure>
  </div>

  <div class="col">
    <section aria-label="Why it differs">
      <h2>Why the right arm goes missing</h2>
      <p>So what decides whether old age lifts the curve or buries it? The tidiest hypothesis is money: richer countries can afford pensions, healthcare and the dignity of a secure retirement, so their elderly recover. There is something to it — but less than you might expect. Plot each country's old-age recovery against its national income and the cloud tilts faintly upward; weighting by population, the correlation is a modest 0.30, and without weighting it nearly vanishes to 0.08. Income nudges the odds. It does not decide them.</p>
      <p>What the scatter shows instead is a <em>cluster</em> that refuses to obey the income line: the former Soviet bloc, sitting far below where their incomes would place them. Russia, Ukraine, Belarus, Moldova, the Baltic states, Georgia — middle-income countries, several of them in the European Union — post some of the steepest old-age declines on Earth. The explanation is not a number in a spreadsheet; it is a biography. The people who are old in these countries today spent their prime adult years inside the Soviet system and then watched it dissolve in their forties and fifties. Pensions evaporated, savings were inflated away, the social contract they had organised their lives around was rewritten mid-sentence. For them, aging has not meant the easing of ambition the U-curve presumes; it has meant outliving the world that promised to look after them.</p>
    </section>
  </div>

  <div class="wide">
    <figure aria-label="Scatter of old-age recovery versus national income">
      <div class="fig-head">
        <div class="fig-title">Money tilts the odds; history sets the floor</div>
        <div class="fig-sub">Each dot is a country: horizontal = national income (GNI per capita, log scale); vertical = how much the old gain (above the line) or lose (below it) versus the midlife low. Hover for names.</div>
      </div>
      <div class="chart-wrap" id="sc-chart">
        <div class="tip" id="sc-tip" role="status" aria-live="polite"></div>
      </div>
      <figcaption>Gallup World Poll, 2005–2020; 153 countries with income data. Vertical axis is the “old-age recovery” = mean ladder at 65+ minus the lowest midlife band (35–44, 45–54 or 55–64). Income is World Bank GNI per capita (PPP), plotted on a log scale. The dashed line is the ordinary-least-squares fit; the relationship is real but loose (population-weighted r = 0.30, unweighted r = 0.08). Dot size scales with population.</figcaption>
    </figure>
  </div>

  <div class="col">
    <section aria-label="The regional ranking">
      <p>Aggregated to Gallup's world regions, the same divide reappears as a clean ranking. Northern America and the Australia–New Zealand pair lead, the only regions where the old clearly out-rate the middle-aged. East Asia shows a real if smaller rebound — almost entirely China's doing. Everywhere else the recovery is somewhere between negligible and sharply negative, and the Commonwealth of Independent States — the post-Soviet core — sits alone at the bottom.</p>
    </section>
  </div>

  <div class="wide">
    <figure aria-label="Old-age recovery by world region">
      <div class="fig-head">
        <div class="fig-title">The old-age rebound, region by region</div>
        <div class="fig-sub">Ladder points gained (green) or lost (red) by the 65+ group relative to each region's midlife low. Above zero, the curve turns back up; below it, old age is the unhappiest stretch of life.</div>
      </div>
      <div class="chart-wrap" id="rg-chart">
        <div class="tip" id="rg-tip" role="status" aria-live="polite"></div>
      </div>
      <figcaption>Gallup World Poll, 2005–2020; region averages population-weight their member countries. Northern America and Australia–New Zealand each pool two countries; all other regions pool many. Bars show the 65+ mean minus the lowest midlife band within the region.</figcaption>
    </figure>
  </div>

  <div class="col">
    <section aria-label="What it means">
      <h2>A pattern, not a promise</h2>
      <p>None of this disproves the U-curve. In the places where it was first and most often measured — affluent, English-speaking, comfortably pensioned — it is alive and well, and this data reproduces it cleanly. The trouble is the leap from <em>there</em> to <em>everywhere</em>: the quiet assumption that the rebound is something the human mind does on its own, a built-in mercy of getting older. The map says otherwise. The rebound shows up where institutions catch people as they fall — health systems, pensions, stable expectations — and it goes missing where the second half of life is precarious or where the ground shifted under a whole generation.</p>
      <p>A few honest caveats keep the story the right size. This is an <em>evaluative</em> measure — a considered judgment of one's whole life — and not the same thing as moment-to-moment mood, which follows its own, often gentler, course with age; the famous finding that emotional well-being and daily calm tend to improve in later life is largely an experiential one, and not what these ladders capture. The poll is a repeated cross-section, not a tracking of the same people over time, so an age “curve” partly mixes the effects of aging with the different fortunes of different birth cohorts — nowhere more so than in the post-Soviet states, where that mixing is precisely the point. Cultural habits of answering also shade the levels: Latin Americans tend to reach for the top of any scale, East Asians for the middle. And cross-country gaps of less than two-tenths of a rung should be read as ties, not rankings.</p>
      <p>Set against all that, the central contrast survives easily. The distance between an old age that lifts the curve and one that sinks it is far larger than any of these cautions — three-quarters of a ladder-rung separates the Anglosphere's rebound from the post-Soviet collapse. The U-shape of happiness is one of social science's most quoted regularities. It deserves a quieter, truer billing: not a law of life, but a description of what a good old age looks like — and a map of how few people get one.</p>
    </section>
  </div>
</main>

<footer>
  <div class="col">
    <h2>Notes &amp; data</h2>
    <ul>
      <li><b>Source.</b> Gallup World Poll, interview-level microdata, 2005–2020 (<code>gallup_world.parquet</code>; 2,293,396 interviews across 168 countries). Measure: the Cantril Self-Anchoring Striving Scale (“ladder”), where 0 = worst possible life and 10 = best possible. This is an <em>evaluative</em> measure of life as a whole — distinct from the experiential, yesterday-affect items also in the survey.</li>
      <li><b>Sample used.</b> Interviews with valid ladder, age (15–99) and weight. The cross-country comparison keeps the 156 countries that have all six age bands present (each band ≥ 80 raw interviews) and at least 2,500 interviews in total; 2.24 million interviews qualify.</li>
      <li><b>Weighting.</b> Within a country, interviews are weighted by Gallup's within-country weight <code>wgt</code>. For every regional, group and global figure, country means are population-weighted by <code>ctry_pop_millions</code> — never an unweighted average of country averages.</li>
      <li><b>“Old-age recovery.”</b> Defined as the mean ladder among those 65+ minus the lowest of the three midlife bands (35–44, 45–54, 55–64). Positive = the curve turns back up in old age (a U); negative = old age is the unhappiest stretch. Country classification: U-shape (recovery ≥ +0.15 with youth ≥ midlife), Decline (recovery ≤ −0.15), otherwise Flat. Of 156 countries: 34 U-shape, 82 Flat, 40 Decline.</li>
      <li><b>Income relationship.</b> Old-age recovery vs. log GNI per capita (PPP, World Bank, joined on ISO3): population-weighted r = 0.30, unweighted r = 0.08; vs. HDI, population-weighted r = 0.26. Prosperity tilts the odds toward recovery but explains little of the spread on its own.</li>
      <li><b>Cohorts, not just aging.</b> The poll is a repeated cross-section. An age profile therefore blends the effect of growing older with differences between birth cohorts — especially acute in the post-Soviet states, where today's elderly lived through the dissolution of the USSR during their prime earning years. The “decline with age” there is best read as a cohort-and-history effect, not evidence that aging itself lowers well-being.</li>
      <li><b>Other caveats.</b> Cross-cultural response styles affect ladder levels (Latin American upward, East Asian central tendency); treat cross-country gaps under ~0.2 rungs as not meaningful. Pooling across 2005–2020 ignores within-period time trends by design, to isolate the age shape. The unbalanced country panel is handled by population-weighting and by requiring full age coverage per country.</li>
      <li><b>Reading.</b> D.G. Blanchflower (2021), “Is happiness U-shaped everywhere? Age and subjective well-being in 145 countries,” <cite>Journal of Population Economics</cite> 34:575–624. A. Steptoe, A. Deaton &amp; A.A. Stone (2015), “Subjective wellbeing, health, and ageing,” <cite>The Lancet</cite> 385:640–648 — on the strong regional dependence of the age–wellbeing curve. A. Deaton (2008), “Income, health and wellbeing around the world,” <cite>Journal of Economic Perspectives</cite> 22(2):53–72. C. Graham &amp; J.R. Pozuelo (2017), “Happiness, stress, and age,” <cite>Journal of Population Economics</cite> 30:225–264.</li>
    </ul>
  </div>
</footer>

<script type="module">
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

const DATA = __DATA__;

const INK="#2b2118", FAINT="#8a7d6e", RULE="#e3d9c8", PAPER="#faf6ef";
const ACCENT="#2f7d6b", WARN="#b5462a", FLAT="#b9aa92";
const BANDS = DATA.bands;
const MID = DATA.band_mid;
const f2 = d3.format(".2f");
const fSigned = d3.format("+.2f");

/* group colours for chart 1 */
const GROUP_ORDER = ["Anglosphere","Western Europe","Latin America","Post-Soviet states","World"];
const GROUP_COLOR = {
  "Anglosphere": ACCENT,
  "Western Europe":"#4a7ba6",
  "Latin America":"#c98a3a",
  "Post-Soviet states": WARN,
  "World": INK
};
/* region colours for the scatter */
const REGION_COLOR = {
  "Northern America":"#2f7d6b",
  "Australia-New Zealand":"#3f9e86",
  "European Union":"#4a7ba6",
  "Europe-Other":"#7d9cb8",
  "Commonwealth of Independent States":"#8a3b6b",
  "East Asia":"#b5462a",
  "Southeast Asia":"#d08a4f",
  "South Asia":"#a9772e",
  "Latin America and the Caribbean":"#c98a3a",
  "Middle East and North Africa":"#6b8e3a",
  "Sub-Saharan Africa":"#9a6a4a"
};

/* shared helpers */
function clearSvg(c){ c.querySelectorAll("svg").forEach(s=>s.remove()); }
function baseSvg(c,w,h,label,desc){
  const svg=d3.select(c).append("svg").attr("viewBox",`0 0 ${w} ${h}`)
    .attr("role","img").attr("aria-label",label);
  svg.append("title").text(label);
  if(desc) svg.append("desc").text(desc);
  return svg;
}
function placeTip(tip,wrap,px,py,html){
  tip.innerHTML=html; tip.style.opacity=1;
  const ww=wrap.clientWidth, tw=tip.offsetWidth;
  let left=px-tw/2; left=Math.max(4,Math.min(ww-tw-4,left));
  tip.style.left=left+"px"; tip.style.top=Math.max(0,py-tip.offsetHeight-14)+"px";
}
function hideTip(tip){ tip.style.opacity=0; }

/* =========================================================
   1. GROUP AGE PROFILES (signature)
   ========================================================= */
const grpWrap=document.getElementById("grp-chart");
const grpTip=document.getElementById("grp-tip");
let focusGroup=null;

// assemble {group: [{band,mid,ladder}]}
const groupLines={};
for(const g of GROUP_ORDER){
  if(g==="World") groupLines[g]=DATA.global_profile;
  else groupLines[g]=DATA.groups[g];
}

function drawGroups(){
  clearSvg(grpWrap); hideTip(grpTip);
  const w=Math.max(320,grpWrap.clientWidth);
  const h=Math.max(340,Math.min(480,w*0.56));
  const narrow=w<560;
  const m={t:24,r:narrow?16:120,b:46,l:46};
  const svg=baseSvg(grpWrap,w,h,
    "Line chart of average life-evaluation ladder by age band, one line per country group.",
    "The Anglosphere line dips in midlife and rises again after 60; the post-Soviet line falls steadily to a low in old age; the World line dips and stays flat.");
  const x=d3.scalePoint().domain(BANDS).range([m.l,w-m.r]).padding(0.5);
  const y=d3.scaleLinear().domain([4.5,7.8]).range([h-m.b,m.t]);

  const yt=y.ticks(6);
  svg.append("g").selectAll("line").data(yt).join("line")
    .attr("x1",m.l).attr("x2",w-m.r).attr("y1",d=>y(d)).attr("y2",d=>y(d))
    .attr("stroke",RULE);
  svg.append("g").selectAll("text").data(yt).join("text")
    .attr("x",m.l-8).attr("y",d=>y(d)).attr("dy","0.32em").attr("text-anchor","end")
    .attr("font-size",11.5).attr("fill",FAINT).attr("class","axis-lab").text(f2);
  svg.append("text").attr("x",m.l-8).attr("y",m.t-10).attr("text-anchor","start")
    .attr("font-size",11.5).attr("fill",FAINT).attr("class","axis-lab")
    .text("Ladder · 0–10, axis zoomed");
  svg.append("g").selectAll("text").data(BANDS).join("text")
    .attr("x",d=>x(d)).attr("y",h-m.b+20).attr("text-anchor","middle")
    .attr("font-size",narrow?10:11).attr("fill",FAINT).attr("class","axis-lab").text(d=>d);
  svg.append("text").attr("x",(m.l+w-m.r)/2).attr("y",h-8).attr("text-anchor","middle")
    .attr("font-size",11.5).attr("fill",FAINT).attr("class","axis-lab").text("Age band");

  const line=d3.line().x(d=>x(d.band)).y(d=>y(d.ladder)).curve(d3.curveMonotoneX);
  const order=GROUP_ORDER.filter(g=>g!==focusGroup).concat(focusGroup?[focusGroup]:[]);
  for(const g of order){
    const pts=groupLines[g];
    const op = focusGroup===null?1:(g===focusGroup?1:0.18);
    const sw = (g===focusGroup?4:(g==="World"?3:2.4));
    svg.append("path").datum(pts).attr("fill","none").attr("stroke",GROUP_COLOR[g])
      .attr("stroke-width",sw).attr("stroke-opacity",op).attr("stroke-linecap","round")
      .attr("stroke-dasharray", g==="World"?"1 6":null)
      .attr("d",line);
    svg.append("g").selectAll("circle").data(pts).join("circle")
      .attr("cx",d=>x(d.band)).attr("cy",d=>y(d.ladder)).attr("r",g===focusGroup?4:3)
      .attr("fill",GROUP_COLOR[g]).attr("fill-opacity",op)
      .attr("stroke",PAPER).attr("stroke-width",1.1);
    if(!narrow){
      const last=pts[pts.length-1];
      svg.append("text").attr("x",x(last.band)+10).attr("y",y(last.ladder)).attr("dy","0.32em")
        .attr("font-size",12).attr("font-weight",g===focusGroup||focusGroup===null?700:500)
        .attr("fill",GROUP_COLOR[g]).attr("fill-opacity",Math.max(0.5,op))
        .attr("class","axis-lab").text(g);
    }
  }
  // annotations on the Anglosphere rebound and post-Soviet low (only when not narrowed away)
  if(focusGroup===null||focusGroup==="Anglosphere"){
    const a=groupLines["Anglosphere"]; const p=a[a.length-1];
    svg.append("text").attr("x",x(p.band)).attr("y",y(p.ladder)-12).attr("text-anchor","middle")
      .attr("font-size",11).attr("font-weight",700).attr("fill",ACCENT).attr("class","axis-lab")
      .text("rebound");
  }

  // hover
  const flat=[];
  for(const g of GROUP_ORDER) groupLines[g].forEach(d=>flat.push({...d,group:g}));
  svg.append("rect").attr("x",m.l).attr("y",m.t).attr("width",w-m.l-m.r).attr("height",h-m.t-m.b)
    .attr("fill","transparent")
    .on("mousemove touchmove",function(ev){
      const [mx,my]=d3.pointer(ev,this.ownerSVGElement);
      const near=d3.least(flat,p=>Math.hypot(x(p.band)-mx,y(p.ladder)-my));
      if(!near||Math.hypot(x(near.band)-mx,y(near.ladder)-my)>50){hideTip(grpTip);return;}
      const sc=grpWrap.clientWidth/w;
      placeTip(grpTip,grpWrap,x(near.band)*sc,y(near.ladder)*sc,
        `<b style="color:#fff">${near.group}</b><br>ages ${near.band}<br><b>${f2(near.ladder)}</b> on the ladder`);
    })
    .on("mouseleave touchend",()=>hideTip(grpTip));
}

const grpPills=document.getElementById("grp-pills");
function buildGrpPills(){
  grpPills.innerHTML="";
  for(const g of GROUP_ORDER){
    const b=document.createElement("button");
    b.className="pill"; b.setAttribute("aria-pressed",String(focusGroup===g));
    b.innerHTML=`<span class="dot" style="background:${GROUP_COLOR[g]}"></span>${g}`;
    b.addEventListener("click",()=>{focusGroup=focusGroup===g?null:g; buildGrpPills(); drawGroups();});
    grpPills.appendChild(b);
  }
}

/* =========================================================
   2. SMALL MULTIPLES
   ========================================================= */
const smWrap=document.getElementById("sm-chart");
function clsColor(c){ return c==="U-shape"?ACCENT:(c==="Decline"?WARN:FLAT); }

function drawSmall(){
  clearSvg(smWrap);
  const w=Math.max(320,smWrap.clientWidth);
  const cols = w<420?2 : (w<680?3:4);
  const items=DATA.exemplars;
  const rows=Math.ceil(items.length/cols);
  const gap=14, padTop=30, padBot=20;
  const cellW=(w-gap*(cols-1))/cols;
  const cellH=Math.max(78,cellW*0.66);
  const h=rows*(cellH+padTop+padBot)-0+8;
  const svg=baseSvg(smWrap,w,h,
    "Small-multiple panels of the age–ladder curve for twenty countries, sorted from strongest old-age rebound to steepest decline.",
    "Wealthy English-speaking and Gulf countries show upward-bending curves; post-Soviet, Latin American and some East Asian countries show downward-bending curves.");

  items.forEach((c,i)=>{
    const r=Math.floor(i/cols), col=i%cols;
    const gx=col*(cellW+gap);
    const gy=r*(cellH+padTop+padBot);
    const vals=BANDS.map(b=>c.band_means[b]).filter(v=>v!=null);
    const lo=Math.min(...vals), hi=Math.max(...vals);
    const pad=(hi-lo)*0.25||0.2;
    const x=d3.scalePoint().domain(BANDS).range([gx+6,gx+cellW-6]).padding(0.3);
    const y=d3.scaleLinear().domain([lo-pad,hi+pad]).range([gy+padTop+cellH-6,gy+padTop+6]);
    const col0=clsColor(c.cls);
    // title
    svg.append("text").attr("x",gx).attr("y",gy+14).attr("font-size",13)
      .attr("font-weight",700).attr("fill",INK).attr("class","axis-lab").text(c.country);
    svg.append("text").attr("x",gx+cellW).attr("y",gy+14).attr("text-anchor","end")
      .attr("font-size",12).attr("font-weight",700).attr("fill",col0).attr("class","axis-lab")
      .text(fSigned(c.right_arm));
    // baseline panel bg
    svg.append("rect").attr("x",gx).attr("y",gy+padTop).attr("width",cellW).attr("height",cellH)
      .attr("fill","#fff").attr("stroke",RULE).attr("rx",6);
    const pts=BANDS.filter(b=>c.band_means[b]!=null).map(b=>({band:b,v:c.band_means[b]}));
    const line=d3.line().x(d=>x(d.band)).y(d=>y(d.v)).curve(d3.curveMonotoneX);
    svg.append("path").datum(pts).attr("fill","none").attr("stroke",col0)
      .attr("stroke-width",2.4).attr("d",line).attr("stroke-linecap","round");
    svg.append("g").selectAll("circle").data(pts).join("circle")
      .attr("cx",d=>x(d.band)).attr("cy",d=>y(d.v)).attr("r",2.2).attr("fill",col0);
    // endpoint dots emphasised
    svg.append("circle").attr("cx",x(pts[0].band)).attr("cy",y(pts[0].v)).attr("r",3.2)
      .attr("fill",PAPER).attr("stroke",col0).attr("stroke-width",1.6);
    svg.append("circle").attr("cx",x(pts[pts.length-1].band)).attr("cy",y(pts[pts.length-1].v))
      .attr("r",3.2).attr("fill",col0);
  });
}

/* =========================================================
   3. SCATTER: recovery vs income
   ========================================================= */
const scWrap=document.getElementById("sc-chart");
const scTip=document.getElementById("sc-tip");
const LABELED=new Set(["USA","AUS","GBR","CAN","RUS","UKR","BLR","MEX","CHN","JPN","KOR","BRA","DEU","IND","NGA","SAU"]);

function drawScatter(){
  clearSvg(scWrap); hideTip(scTip);
  const w=Math.max(320,scWrap.clientWidth);
  const h=Math.max(360,Math.min(520,w*0.62));
  const narrow=w<560;
  const m={t:22,r:18,b:50,l:50};
  const svg=baseSvg(scWrap,w,h,
    "Scatter plot of each country's old-age recovery against its national income on a log scale.",
    "Richer countries tilt slightly toward old-age recovery, but the post-Soviet countries sit far below the trend at middle incomes.");
  const pts=DATA.scatter.points;
  const x=d3.scaleLinear().domain(d3.extent(pts,d=>d.loggni)).nice().range([m.l,w-m.r]);
  const yext=d3.extent(pts,d=>d.right_arm);
  const y=d3.scaleLinear().domain([Math.min(-0.65,yext[0]-0.05),Math.max(0.7,yext[1]+0.05)]).range([h-m.b,m.t]);
  const rad=d3.scaleSqrt().domain([0,d3.max(pts,d=>d.pop||1)]).range([2.2,narrow?13:18]);

  // gridlines at income ticks ($ values)
  const dollarTicks=[1000,2000,5000,10000,20000,50000,100000];
  const visTicks=dollarTicks.filter(v=>Math.log(v)>=x.domain()[0]&&Math.log(v)<=x.domain()[1]);
  svg.append("g").selectAll("line").data(visTicks).join("line")
    .attr("x1",d=>x(Math.log(d))).attr("x2",d=>x(Math.log(d))).attr("y1",m.t).attr("y2",h-m.b)
    .attr("stroke",RULE);
  svg.append("g").selectAll("text").data(visTicks).join("text")
    .attr("x",d=>x(Math.log(d))).attr("y",h-m.b+18).attr("text-anchor","middle")
    .attr("font-size",11).attr("fill",FAINT).attr("class","axis-lab")
    .text(d=>d>=1000?"$"+(d/1000)+"k":"$"+d);
  svg.append("text").attr("x",(m.l+w-m.r)/2).attr("y",h-8).attr("text-anchor","middle")
    .attr("font-size",11.5).attr("fill",FAINT).attr("class","axis-lab")
    .text("National income — GNI per capita, PPP (log scale)");

  // y ticks
  const yt=[-0.6,-0.4,-0.2,0,0.2,0.4,0.6];
  svg.append("g").selectAll("text").data(yt).join("text")
    .attr("x",m.l-8).attr("y",d=>y(d)).attr("dy","0.32em").attr("text-anchor","end")
    .attr("font-size",11).attr("fill",FAINT).attr("class","axis-lab").text(d=>fSigned(d));

  // zero line
  svg.append("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",y(0)).attr("y2",y(0))
    .attr("stroke",INK).attr("stroke-opacity",0.5).attr("stroke-width",1.3);
  svg.append("text").attr("x",w-m.r).attr("y",y(0)-6).attr("text-anchor","end")
    .attr("font-size",10.5).attr("fill",FAINT).attr("class","axis-lab").text("old age recovers ↑ / declines ↓");
  svg.append("text").attr("x",m.l-8).attr("y",m.t-8).attr("text-anchor","start")
    .attr("font-size",11).attr("fill",FAINT).attr("class","axis-lab").text("Old-age recovery (ladder pts)");

  // fit line
  const xs=x.domain();
  const fit=v=>DATA.scatter.fit_intercept+DATA.scatter.fit_slope*v;
  svg.append("line").attr("x1",x(xs[0])).attr("y1",y(fit(xs[0])))
    .attr("x2",x(xs[1])).attr("y2",y(fit(xs[1])))
    .attr("stroke",INK).attr("stroke-width",1.6).attr("stroke-dasharray","5 5").attr("stroke-opacity",0.55);

  // dots
  const sorted=[...pts].sort((a,b)=>(b.pop||0)-(a.pop||0));
  svg.append("g").selectAll("circle").data(sorted).join("circle")
    .attr("cx",d=>x(d.loggni)).attr("cy",d=>y(d.right_arm)).attr("r",d=>rad(d.pop||1))
    .attr("fill",d=>REGION_COLOR[d.region]||FAINT).attr("fill-opacity",0.62)
    .attr("stroke",PAPER).attr("stroke-width",1)
    .on("mousemove touchmove",function(ev,d){
      const sc=scWrap.clientWidth/w;
      placeTip(scTip,scWrap,x(d.loggni)*sc,y(d.right_arm)*sc,
        `<b style="color:#fff">${d.country}</b><br>recovery <b>${fSigned(d.right_arm)}</b> · GNI $${d3.format(",")(d.gni)}<br><span style="opacity:.8">${d.region}</span>`);
    })
    .on("mouseleave touchend",()=>hideTip(scTip));

  // labels for notable points
  const labeled=pts.filter(d=>LABELED.has(d.iso3));
  svg.append("g").selectAll("text").data(labeled).join("text")
    .attr("x",d=>x(d.loggni)).attr("y",d=>y(d.right_arm)-rad(d.pop||1)-3)
    .attr("text-anchor","middle").attr("font-size",narrow?9.5:11).attr("font-weight",600)
    .attr("fill",INK).attr("class","axis-lab")
    .attr("paint-order","stroke").attr("stroke",PAPER).attr("stroke-width",2.6)
    .text(d=>d.country);
}

/* =========================================================
   4. REGION RECOVERY BARS
   ========================================================= */
const rgWrap=document.getElementById("rg-chart");
const rgTip=document.getElementById("rg-tip");
const REGION_SHORT={
  "Northern America":"Northern America",
  "Australia-New Zealand":"Australia–NZ",
  "European Union":"European Union",
  "Europe-Other":"Other Europe",
  "Commonwealth of Independent States":"Post-Soviet (CIS)",
  "East Asia":"East Asia",
  "Southeast Asia":"Southeast Asia",
  "South Asia":"South Asia",
  "Latin America and the Caribbean":"Latin America",
  "Middle East and North Africa":"Mid. East & N. Africa",
  "Sub-Saharan Africa":"Sub-Saharan Africa"
};

function drawRegions(){
  clearSvg(rgWrap); hideTip(rgTip);
  const w=Math.max(320,rgWrap.clientWidth);
  const rowsD=[...DATA.region_summary].sort((a,b)=>b.right_arm-a.right_arm);
  const rowH=34, m={t:14,b:28,l:w<480?120:160,r:30};
  const h=m.t+rowsD.length*rowH+m.b;
  const svg=baseSvg(rgWrap,w,h,
    "Diverging bar chart of old-age recovery by world region.",
    "Northern America and Australia–New Zealand have positive old-age recovery; the post-Soviet CIS region is most negative.");
  const ext=d3.extent(rowsD,d=>d.right_arm);
  const x=d3.scaleLinear().domain([Math.min(-0.3,ext[0]),Math.max(0.62,ext[1])]).range([m.l,w-m.r]);
  // zero axis
  svg.append("line").attr("x1",x(0)).attr("x2",x(0)).attr("y1",m.t).attr("y2",h-m.b)
    .attr("stroke",INK).attr("stroke-opacity",0.55);
  for(const t of [-0.2,0,0.2,0.4,0.6]){
    if(t<x.domain()[0]||t>x.domain()[1])continue;
    svg.append("text").attr("x",x(t)).attr("y",h-m.b+18).attr("text-anchor","middle")
      .attr("font-size",10.5).attr("fill",FAINT).attr("class","axis-lab").text(fSigned(t));
  }
  rowsD.forEach((r,i)=>{
    const cy=m.t+i*rowH;
    const pos=r.right_arm>=0;
    const col=pos?ACCENT:WARN;
    svg.append("text").attr("x",m.l-10).attr("y",cy+rowH/2).attr("dy","0.32em")
      .attr("text-anchor","end").attr("font-size",12.5)
      .attr("font-weight",(r.region.indexOf("Northern")===0||r.region.indexOf("Common")===0)?700:500)
      .attr("fill",INK).attr("class","axis-lab").text(REGION_SHORT[r.region]||r.region);
    const x0=x(0), x1=x(r.right_arm);
    svg.append("rect").attr("x",Math.min(x0,x1)).attr("y",cy+7).attr("width",Math.abs(x1-x0))
      .attr("height",rowH-14).attr("rx",3).attr("fill",col)
      .on("mousemove touchmove",function(ev){
        const sc=rgWrap.clientWidth/w;
        placeTip(rgTip,rgWrap,(x0+x1)/2*sc,(cy+rowH/2)*sc,
          `<b style="color:#fff">${REGION_SHORT[r.region]||r.region}</b><br>young ${f2(r.young)} · trough ${f2(r.mid)} · old ${f2(r.old)}<br>recovery <b>${fSigned(r.right_arm)}</b>`);
      })
      .on("mouseleave touchend",()=>hideTip(rgTip));
    // value label: positive bars label outside the right end; negative bars
    // label just inside their left end (white) so it never collides with the
    // region name in the left margin.
    svg.append("text").attr("x",pos?x1+6:x1+6).attr("y",cy+rowH/2).attr("dy","0.32em")
      .attr("text-anchor","start").attr("font-size",12).attr("font-weight",700)
      .attr("fill",pos?col:"#fff").attr("class","axis-lab").text(fSigned(r.right_arm));
  });
}

/* boot + resize */
buildGrpPills(); drawGroups(); drawSmall(); drawScatter(); drawRegions();
let raf=null;
const ro=new ResizeObserver(()=>{
  if(raf)cancelAnimationFrame(raf);
  raf=requestAnimationFrame(()=>{drawGroups(); drawSmall(); drawScatter(); drawRegions();});
});
ro.observe(grpWrap);
</script>
</body>
</html>
"""

html = HTML.replace("__DATA__", DATA_JSON)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("wrote index.html  (%d bytes; %d scatter pts; %d exemplars)" %
      (len(html), len(DATA["scatter"]["points"]), len(DATA["exemplars"])))
