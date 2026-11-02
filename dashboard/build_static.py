"""Export a self-contained, offline HTML version of the dashboard (no Python needed to view it)."""
from pathlib import Path

import plotly.io as pio

import figures as F

HERE = Path(__file__).resolve().parent
df = F.load(HERE.parent / "data" / "forestfires_clean.csv")
css = (HERE / "assets" / "style.css").read_text(encoding="utf-8")

figs = [("g-month", F.monthly_bars(df), False), ("g-treemap", F.treemap(df), False),
        ("g-scatter", F.scatter(df), False), ("g-spatial", F.spatial(df), False),
        ("g-parsets", F.parallel_sets(df), True), ("g-corr", F.correlogram(df), False)]
cards = []
for i, (fid, fig, wide) in enumerate(figs):
    div = pio.to_html(fig, include_plotlyjs=(i == 0), full_html=False, div_id=fid, config={"displaylogo": False, "responsive": True})
    cards.append(f'<div class="card{" wide" if wide else ""}">{div}</div>')
kpis = "".join(f'<div class="kpi"><div class="kpi-label">{k}</div><div class="kpi-value">{v}</div></div>' for k, v in F.kpis(df))

insights = """
<div class="card predictor">
  <h3>Key insights</h3>
  <ul class="note">
    <li><b>August + September</b> = 69% of observations and <b>81% of burned hectares</b>.</li>
    <li>The <b>10 largest fires</b> account for about <b>half</b> of all burned area.</li>
    <li>The Drought Code keeps building until September; temperature peaks in July.</li>
    <li>Hot &amp; dry days (&gt;22&nbsp;°C, RH&nbsp;&lt;35%) have the largest average fire (30 ha vs 9 ha).</li>
    <li>Two grid cells, (6,5) and (8,6), hold 40% of all burned hectares.</li>
    <li>A Random Forest ranks days into risk tiers (High tier: 60% fire rate vs 42% in Low).</li>
  </ul>
  <p class="note">This is a static snapshot of all data. For filters and the live risk predictor run
  <code>python dashboard/app.py</code>.</p>
</div>"""

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Montesinho Wildfire Dashboard</title><style>{css}</style></head>
<body><div class="page">
<header><h1>Montesinho Natural Park — Wildfire Dashboard</h1>
<p class="sub">When does the park burn, why, and where? 513 observations (UCI Forest Fires, Portugal). Static snapshot.</p></header>
<div class="kpis">{kpis}</div>
<div class="grid">{"".join(cards)}{insights}</div>
<footer>Activity 2 · Predictive Analytics and Data Visualization (25MCAAI302) · Anoon M R (25MCAR0179) ·
Data: Cortez &amp; Morais (2007), UCI ML Repository</footer>
</div></body></html>"""
out = HERE / "Wildfire_Dashboard.html"
out.write_text(html, encoding="utf-8")
print("Wrote", out, f"({out.stat().st_size / 1e6:.1f} MB)")
