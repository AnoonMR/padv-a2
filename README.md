# Activity 2 — Data Storytelling Through Visualization

**Course:** Predictive Analytics and Data Visualization (25MCAAI302) · MCA AIML Sem III · AY 2026–27
**Student:** Anoon M R (25MCAR0179) · **Faculty:** Prof. Rahul Pawar · **Due:** 06-11-2026
**Dataset:** UCI Forest Fires — Montesinho Natural Park, Portugal (same dataset as Activity 1)

## Deliverables (handbook: Dashboard, Report and Presentation)

| File | What it is |
|---|---|
| `Activity2_Report.docx` / `.pdf` | Report: cover, certificate, Table of Contents, Problem Statement, Dataset, Solution, Screenshots, Conclusion, References |
| `Activity2_Presentation.pptx` / `.pdf` | 20-slide presentation with speaker notes |
| `dashboard/app.py` | Interactive Plotly Dash dashboard (filters, KPIs, 6 charts, risk predictor) |
| `dashboard/Wildfire_Dashboard.html` | Offline static copy of the dashboard — opens in any browser |
| `Activity2_Data_Storytelling.ipynb` | Full analysis notebook (executed, with outputs) |

## Run the dashboard

```
pip install dash plotly pandas scikit-learn
python dashboard/app.py
```
Then open http://127.0.0.1:8050

## Folder layout

- `data/` — raw `forestfires.csv`, `forestfires.names`, cleaned `forestfires_clean.csv`
- `figures/` — all chart PNGs (+ `dashboard/` screenshots)
- `outputs/` — `metrics.json`, interactive treemap / parallel-sets HTML
- `_build/` — scripts that regenerate everything:
  `build_notebook.py` (from `notebook_source.py`) → `dashboard/build_static.py` → `screenshots.py` → `build_report.py` (+ `report_body.py`) → `build_ppt.py` → `to_pdf.py`
