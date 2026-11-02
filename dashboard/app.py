"""Montesinho Wildfire Dashboard — Activity 2 (PADV, 25MCAAI302)

Run:  python dashboard/app.py      then open http://127.0.0.1:8050
Data: data/forestfires_clean.csv (written by Activity2_Data_Storytelling.ipynb)

Filtered views can be opened (and shared) by URL, e.g.
  http://127.0.0.1:8050/?season=Summer&day=Weekend
  http://127.0.0.1:8050/?months=7-9&p_month=3&p_temp=8&p_rh=75
"""
from pathlib import Path
from urllib.parse import parse_qs

import numpy as np
from dash import Dash, Input, Output, dcc, html, no_update
from dash.exceptions import PreventUpdate
from sklearn.ensemble import RandomForestClassifier

import figures as F

A2 = Path(__file__).resolve().parent.parent
df = F.load(A2 / "data" / "forestfires_clean.csv")

# ---- Early-warning model (same configuration as the notebook) ----
FEATURES = ["X", "Y", "month_num", "day_num", "FFMC", "DMC", "DC", "ISI", "temp", "RH", "wind", "rain"]
rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, class_weight="balanced", random_state=42, n_jobs=-1)
rf.fit(df[FEATURES], df["fire"])
# Tier cut-offs = tertiles of the out-of-fold probabilities computed in the notebook
T1, T2 = np.quantile(df["risk_prob"], [1 / 3, 2 / 3])
TIER_RATES = df.groupby("risk_tier", observed=True)["fire"].mean().mul(100).round(0).to_dict()

app = Dash(__name__, title="Montesinho Wildfire Dashboard")


def kpi_tiles(d):
    return [html.Div([html.Div(label, className="kpi-label"), html.Div(value, className="kpi-value")], className="kpi")
            for label, value in F.kpis(d)]


def card(graph_id, wide=False):
    return html.Div(dcc.Graph(id=graph_id, config={"displaylogo": False}), className="card wide" if wide else "card")


def slider(id_, label, lo, hi, step, value):
    return html.Div([html.Label(label, className="ctl-label"),
                     dcc.Slider(id=id_, min=lo, max=hi, step=step, value=value, marks=None)], className="ctl")


app.layout = html.Div(className="page", children=[
    dcc.Location(id="url"),
    html.Header([
        html.H1("Montesinho Natural Park — Wildfire Dashboard"),
        html.P("When does the park burn, why, and where? 513 observations (UCI Forest Fires, Portugal). "
               "Filters apply to every chart and KPI below.", className="sub"),
    ]),
    # One filter row above everything it scopes
    html.Div(className="filters", children=[
        html.Div([html.Label("Season", className="ctl-label"),
                  dcc.Checklist(id="f-season", options=F.SEASON_ORDER, value=F.SEASON_ORDER, inline=True, className="chk")]),
        html.Div([html.Label("Months", className="ctl-label"),
                  dcc.RangeSlider(id="f-month", min=1, max=12, step=1, value=[1, 12],
                                  marks={i + 1: m for i, m in enumerate(F.MONTH_LBL)})], className="grow"),
        html.Div([html.Label("Day type", className="ctl-label"),
                  dcc.RadioItems(id="f-day", options=["All", "Weekday", "Weekend"], value="All", inline=True, className="chk")]),
    ]),
    html.Div(id="kpis", className="kpis"),
    html.Div(className="grid", children=[
        card("g-month"), card("g-treemap"),
        card("g-scatter"), card("g-spatial"),
        card("g-parsets", wide=True),
        card("g-corr"),
        # ---- Risk predictor ----
        html.Div(className="card predictor", children=[
            html.H3("Early-warning risk check"),
            html.P("Random Forest trained on all 513 observations. Cross-validated ROC-AUC ≈ 0.60 — use the tier "
                   "to rank days, not as a yes/no alarm.", className="note"),
            html.Div(className="pred-grid", children=[
                html.Div([html.Label("Month", className="ctl-label"),
                          dcc.Dropdown(id="p-month", options=[{"label": m, "value": i + 1} for i, m in enumerate(F.MONTH_LBL)],
                                       value=8, clearable=False)], className="ctl"),
                html.Div([html.Label("Grid cell (X, Y)", className="ctl-label"),
                          dcc.Dropdown(id="p-cell", options=[{"label": f"X={x}, Y={y}", "value": f"{x},{y}"}
                                                              for x, y in sorted(df[["X", "Y"]].drop_duplicates().itertuples(index=False))],
                                       value="6,5", clearable=False)], className="ctl"),
                slider("p-temp", "Temperature (°C)", 2, 34, 0.5, 22),
                slider("p-rh", "Relative humidity (%)", 15, 100, 1, 40),
                slider("p-wind", "Wind (km/h)", 0, 10, 0.1, 4),
                slider("p-ffmc", "FFMC (fine-fuel moisture code)", 60, 97, 0.1, 91.6),
                slider("p-dmc", "DMC (duff moisture code)", 1, 300, 1, 108),
                slider("p-dc", "DC (drought code)", 7, 861, 1, 664),
                slider("p-isi", "ISI (initial spread index)", 0, 25, 0.1, 8.4),
            ]),
            html.Div(id="p-out", className="pred-out"),
        ]),
    ]),
    html.Footer("Activity 2 · Predictive Analytics and Data Visualization (25MCAAI302) · Anoon M R (25MCAR0179) · "
                "Data: Cortez & Morais (2007), UCI ML Repository"),
])


@app.callback(
    [Output("kpis", "children"), Output("g-month", "figure"), Output("g-treemap", "figure"), Output("g-scatter", "figure"),
     Output("g-spatial", "figure"), Output("g-parsets", "figure"), Output("g-corr", "figure")],
    [Input("f-season", "value"), Input("f-month", "value"), Input("f-day", "value")],
)
def update(seasons, months, day):
    d = df[df.season.isin(seasons or []) & df.month_num.between(months[0], months[1])]
    if day != "All":
        d = d[d.day_type == day]
    return (kpi_tiles(d), F.monthly_bars(d), F.treemap(d), F.scatter(d), F.spatial(d), F.parallel_sets(d), F.correlogram(d))


@app.callback(Output("p-out", "children"),
              [Input(i, "value") for i in ["p-month", "p-cell", "p-temp", "p-rh", "p-wind", "p-ffmc", "p-dmc", "p-dc", "p-isi"]])
def predict(month, cell, temp, rh, wind, ffmc, dmc, dc, isi):
    x, y = map(int, cell.split(","))
    row = [[x, y, month, 6, ffmc, dmc, dc, isi, temp, rh, wind, 0.0]]
    p = rf.predict_proba(row)[0, 1]
    tier = "High" if p >= T2 else "Moderate" if p >= T1 else "Low"
    return [html.Div([html.Span(f"{tier} risk", className=f"tier tier-{tier.lower()}"),
                      html.Span(f"model score {p:.2f}", className="score")]),
            html.P(f"Historically, {TIER_RATES.get(tier, 0):.0f}% of observations in the {tier} tier had a fire "
                   f"(overall {df.fire.mean() * 100:.0f}%).", className="note")]


# ---- Optional URL query string -> initial control values (shareable filtered views) ----
PRED_PARAMS = [("p_month", "p-month", int), ("p_cell", "p-cell", str), ("p_temp", "p-temp", float), ("p_rh", "p-rh", float),
               ("p_wind", "p-wind", float), ("p_ffmc", "p-ffmc", float), ("p_dmc", "p-dmc", float), ("p_dc", "p-dc", float),
               ("p_isi", "p-isi", float)]


@app.callback([Output("f-season", "value"), Output("f-month", "value"), Output("f-day", "value")] +
              [Output(cid, "value") for _, cid, _ in PRED_PARAMS],
              Input("url", "search"))
def from_url(search):
    q = {k: v[0] for k, v in parse_qs((search or "").lstrip("?")).items()}
    if not q:
        raise PreventUpdate
    season = [s for s in q["season"].split(",") if s in F.SEASON_ORDER] if "season" in q else no_update
    months = [int(m) for m in q["months"].split("-")] if "months" in q else no_update
    day = q["day"] if q.get("day") in ("All", "Weekday", "Weekend") else no_update
    preds = [cast(q[key]) if key in q else no_update for key, _, cast in PRED_PARAMS]
    return [season, months, day] + preds


if __name__ == "__main__":
    app.run(debug=False, port=8050)
