"""Figure builders shared by the Dash app (app.py) and the static HTML export (build_static.py)."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SIZE_ORDER = ["No fire", "Small (<1 ha)", "Medium (1-10 ha)", "Large (>10 ha)"]
SIZE_COLORS = dict(zip(SIZE_ORDER, ["#b9b7ae", "#f0915c", "#c9501f", "#7a2a0e"]))
ORANGE_SCALE = [[0, "#fbe6d8"], [0.5, "#e0733f"], [1, "#7a2a0e"]]
DIVERGING = [[0, "#2a78d6"], [0.5, "#f0efec"], [1, "#e34948"]]
SEASON_ORDER = ["Winter", "Spring", "Summer", "Autumn"]
MONTH_LBL = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FONT = "Segoe UI, system-ui, -apple-system, sans-serif"


def _style(fig, title, height=360):
    fig.update_layout(template="plotly_white", height=height, title=dict(text=f"<b>{title}</b>", x=0.01, font=dict(size=15)),
                      font=dict(family=FONT, color=INK, size=12), paper_bgcolor="white", plot_bgcolor="white",
                      margin=dict(t=56, l=56, r=20, b=48), hoverlabel=dict(font_family=FONT),
                      legend=dict(orientation="h", y=-0.2, x=0))
    fig.update_xaxes(gridcolor=GRID, linecolor="#c3c2b7", zeroline=False)
    fig.update_yaxes(gridcolor=GRID, linecolor="#c3c2b7", zeroline=False)
    return fig


def load(path):
    df = pd.read_csv(path)
    df["size_class"] = pd.Categorical(df["size_class"], SIZE_ORDER, ordered=True)
    df["season"] = pd.Categorical(df["season"], SEASON_ORDER, ordered=True)
    return df


def kpis(d):
    if d.empty:
        return [("Observations", "0"), ("Fire rate", "–"), ("Hectares burned", "0"), ("Largest fire", "–"), ("Median temp", "–")]
    return [("Observations", f"{len(d):,}"),
            ("Fire rate", f"{d.fire.mean() * 100:.0f}%"),
            ("Hectares burned", f"{d.area.sum():,.0f} ha"),
            ("Largest fire", f"{d.area.max():,.0f} ha"),
            ("Median temp", f"{d.temp.median():.1f} °C")]


def monthly_bars(d):
    g = d.groupby(["month_num", "size_class"], observed=False).size().reset_index(name="n")
    fig = go.Figure()
    for cls in SIZE_ORDER:
        n = g[g.size_class == cls].set_index("month_num")["n"].reindex(range(1, 13), fill_value=0)
        fig.add_bar(x=MONTH_LBL, y=n, name=cls, marker=dict(color=SIZE_COLORS[cls], line=dict(color="white", width=1.5)),
                    hovertemplate="%{x}: %{y} obs.<extra>" + cls + "</extra>")
    fig.update_layout(barmode="stack", bargap=0.25, legend_traceorder="normal")
    return _style(fig, "Observations per month by fire outcome")


def treemap(d):
    tm = (d[d.area > 0].groupby(["season", "month_lbl"], observed=True)
          .agg(burned_ha=("area", "sum"), fires=("fire", "sum")).reset_index())
    if tm.empty:
        return _style(go.Figure(), "Burned hectares: season → month")
    fig = px.treemap(tm, path=[px.Constant("All"), "season", "month_lbl"], values="burned_ha", color="burned_ha",
                     color_continuous_scale=ORANGE_SCALE, custom_data=["fires"])
    fig.update_traces(texttemplate="<b>%{label}</b><br>%{value:,.0f} ha", marker=dict(line=dict(color="white", width=2)),
                      hovertemplate="<b>%{label}</b><br>%{value:,.1f} ha burned<extra></extra>")
    fig.update_layout(coloraxis_showscale=False)
    return _style(fig, "Treemap: burned hectares, season → month")


def scatter(d):
    fig = go.Figure()
    for cls in SIZE_ORDER:
        s = d[d.size_class == cls]
        fig.add_scatter(x=s.temp, y=s.RH, mode="markers", name=cls,
                        marker=dict(color=SIZE_COLORS[cls], size=6 if cls == "No fire" else 7 + s.log_area * 3.2,
                                    line=dict(color="white", width=1), opacity=0.8),
                        customdata=np.stack([s.area, s.month_lbl, s.wind], axis=-1) if len(s) else None,
                        hovertemplate="Temp %{x}°C · RH %{y}%<br>Wind %{customdata[2]} km/h · %{customdata[1]}<br>"
                                      "Burned %{customdata[0]:.2f} ha<extra>" + cls + "</extra>")
    fig.add_shape(type="rect", x0=22, x1=34, y0=10, y1=35, fillcolor=ORANGE, opacity=0.06, line_width=0, layer="below")
    fig.update_xaxes(title="Temperature (°C)"); fig.update_yaxes(title="Relative humidity (%)", range=[10, 101])
    return _style(fig, "Scatter: temperature vs humidity (marker size ~ log burned area)")


def spatial(d, metric="area"):
    agg = "sum" if metric == "area" else "size"
    p = d.pivot_table(index="Y", columns="X", values="area", aggfunc=agg).reindex(index=range(1, 10), columns=range(1, 10))
    title = "Park grid: hectares burned per cell" if metric == "area" else "Park grid: observations per cell"
    fig = go.Figure(go.Heatmap(z=p.values, x=list(range(1, 10)), y=list(range(1, 10)), colorscale=ORANGE_SCALE,
                               xgap=2, ygap=2, texttemplate="%{z:.0f}", hovertemplate="X=%{x}, Y=%{y}<br>%{z:,.1f}<extra></extra>",
                               colorbar=dict(title="ha" if metric == "area" else "obs.")))
    fig.update_yaxes(autorange="reversed", title="Y (north → south)", dtick=1, showgrid=False)
    fig.update_xaxes(title="X (west → east)", dtick=1, showgrid=False)
    return _style(fig, title)


def correlogram(d):
    cols = ["FFMC", "DMC", "DC", "ISI", "temp", "RH", "wind", "rain", "log_area"]
    c = d[cols].corr()
    m = np.triu(np.ones_like(c, dtype=bool), k=0)
    z = c.mask(m).iloc[1:, :-1]
    fig = go.Figure(go.Heatmap(z=z.values, x=list(z.columns), y=list(z.index), zmin=-1, zmax=1, colorscale=DIVERGING,
                               xgap=2, ygap=2, texttemplate="%{z:.2f}", hovertemplate="%{y} × %{x}: r = %{z:.2f}<extra></extra>",
                               colorbar=dict(title="r")))
    fig.update_yaxes(autorange="reversed", showgrid=False); fig.update_xaxes(showgrid=False)
    return _style(fig, "Correlogram of weather variables and log(area)")


def parallel_sets(d):
    if d.empty:
        return _style(go.Figure(), "Parallel sets")
    code = d["size_class"].cat.codes
    dims = [go.parcats.Dimension(values=d["season"].astype(str), label="Season", categoryorder="array", categoryarray=SEASON_ORDER),
            go.parcats.Dimension(values=d["ffmc_band"], label="Fine-fuel dryness"),
            go.parcats.Dimension(values=d["temp_band"].astype(str), label="Temperature", categoryorder="array",
                                 categoryarray=["Cool (<15C)", "Mild (15-22C)", "Hot (>22C)"]),
            go.parcats.Dimension(values=d["size_class"].astype(str), label="Fire outcome", categoryorder="array", categoryarray=SIZE_ORDER)]
    cscale = [[i / 3, SIZE_COLORS[c]] for i, c in enumerate(SIZE_ORDER)]
    fig = go.Figure(go.Parcats(dimensions=dims, line=dict(color=code, colorscale=cscale, cmin=0, cmax=3, shape="hspline"),
                               hoveron="color", arrangement="freeform"))
    fig = _style(fig, "Parallel sets: conditions → fire outcome", height=400)
    fig.update_layout(margin=dict(t=70, l=70, r=130, b=24))
    return fig
