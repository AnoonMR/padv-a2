"""Build Activity2_Presentation.pptx (16:9) from the notebook figures and metrics."""
import json
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

A2 = Path(__file__).resolve().parent.parent
FIG = A2 / "figures"
M = json.loads((A2 / "outputs" / "metrics.json").read_text())

# ---- palette: ember / charcoal ----
DARK = RGBColor(0x24, 0x17, 0x11)       # dominant dark (title/closing)
EMBER = RGBColor(0xEB, 0x68, 0x34)      # accent
BROWN = RGBColor(0x7A, 0x2A, 0x0E)
INK = RGBColor(0x1B, 0x1B, 0x1B)
INK2 = RGBColor(0x52, 0x51, 0x4E)
SOFT = RGBColor(0xFB, 0xEF, 0xE7)       # card tint
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SAND = RGBColor(0xE9, 0xD9, 0xCE)
HEAD, BODY = "Cambria", "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = 13.333, 7.5
slide_no = [0]

st_ = {r["grp"]: r for r in M["share_table"]}
aug_sep_obs = st_["August"]["% of observations"] + st_["September"]["% of observations"]
aug_sep_area = st_["August"]["% of burned area"] + st_["September"]["% of burned area"]
cv = M["cv_auc"]; tiers = {t["risk_tier"]: t for t in M["tiers"]}
hd, rest = M["hot_dry"], M["rest"]; cells = M["top_cells"]
two_cells = (cells[0]["burned_ha"] + cells[1]["burned_ha"]) / M["total_area"] * 100


def bg(slide, color):
    f = slide.background.fill; f.solid(); f.fore_color.rgb = color


def text(slide, x, y, w, h, runs, size=16, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, italic=False, name=None, spacing=None):
    """runs: str, or list of paragraphs; each paragraph a str or list of (text, {opts})."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name: tb.name = name
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.02); tf.margin_top = tf.margin_bottom = Inches(0.02)
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if spacing: p.space_after = Pt(spacing)
        segs = para if isinstance(para, list) else [(para, {})]
        for seg, o in segs:
            r = p.add_run(); r.text = seg
            r.font.size = Pt(o.get("size", size)); r.font.name = o.get("font", font)
            r.font.bold = o.get("bold", bold); r.font.italic = o.get("italic", italic)
            r.font.color.rgb = o.get("color", color)
    return tb


def bullets(slide, x, y, w, h, items, size=15, color=INK, gap=8):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        parts = it.split("**")
        r0 = p.add_run(); r0.text = "▸  "; r0.font.color.rgb = EMBER; r0.font.size = Pt(size); r0.font.bold = True; r0.font.name = BODY
        for k, part in enumerate(parts):
            if not part: continue
            r = p.add_run(); r.text = part; r.font.size = Pt(size); r.font.name = BODY
            r.font.bold = k % 2 == 1; r.font.color.rgb = color
    return tb


def box(slide, x, y, w, h, fill, radius=True, name=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid(); shp.fill.fore_color.rgb = fill; shp.line.fill.background(); shp.shadow.inherit = False
    if radius: shp.adjustments[0] = 0.08
    if name: shp.name = name
    return shp


def circle_num(slide, x, y, d, label, fill=EMBER, fg=WHITE, size=16):
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    c.fill.solid(); c.fill.fore_color.rgb = fill; c.line.fill.background(); c.shadow.inherit = False
    tf = c.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label; r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = fg; r.font.name = BODY


def picture(slide, name, x, y, w, h):
    """Fit image inside the box, centered, keeping aspect ratio."""
    path = FIG / name
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    return slide.shapes.add_picture(str(path), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))


def footer(slide, dark=False):
    slide_no[0] += 1
    col = SAND if dark else INK2
    text(slide, 0.6, 7.05, 9, 0.3, "Activity 2 · Data Storytelling Through Visualization · 25MCAAI302", size=10, color=col)
    text(slide, SW - 1.6, 7.05, 1.0, 0.3, str(slide_no[0]), size=10, color=col, align=PP_ALIGN.RIGHT)


def content_slide(title, kicker=None, notes=""):
    s = prs.slides.add_slide(BLANK); bg(s, WHITE)
    if kicker:
        text(s, 0.6, 0.32, 10, 0.35, kicker.upper(), size=12, color=EMBER, bold=True)
    text(s, 0.6, 0.62, SW - 1.2, 0.9, title, size=28, font=HEAD, bold=True, color=INK, name="Title")
    footer(s)
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s


def takeaway_panel(s, x, y, w, h, heading, items, stat=None, stat_label=None):
    box(s, x, y, w, h, SOFT)
    yy = y + 0.3
    if stat:
        text(s, x + 0.3, yy, w - 0.6, 0.9, stat, size=46, font=HEAD, bold=True, color=BROWN)
        text(s, x + 0.3, yy + 0.92, w - 0.6, 0.6, stat_label, size=13, color=INK2)
        yy += 1.75
    text(s, x + 0.3, yy, w - 0.6, 0.4, heading, size=15, bold=True, color=INK)
    bullets(s, x + 0.3, yy + 0.45, w - 0.6, h - (yy - y) - 0.6, items, size=14, gap=6)


# ============ 1. TITLE ============
s = prs.slides.add_slide(BLANK); bg(s, DARK)
text(s, 0.8, 0.7, 11, 0.4, "PREDICTIVE ANALYTICS AND DATA VISUALIZATION · 25MCAAI302 · ACTIVITY 2", size=13, color=EMBER, bold=True)
text(s, 0.8, 1.6, 11.5, 1.9, "When does Montesinho burn — and what can a forest agency do about it?",
     size=44, font=HEAD, bold=True, color=WHITE)
text(s, 0.8, 3.75, 11, 0.5, "Data Storytelling Through Visualization  ·  UCI Forest Fires dataset, Portugal", size=19, color=SAND, italic=True)
for i, (big, small) in enumerate([(f"{M['rows_clean']}", "observations"), (f"{M['total_area']:,.0f} ha", "burned"),
                                  ("10", "visualizations"), ("1", "interactive dashboard")]):
    x = 0.8 + i * 2.9
    text(s, x, 4.75, 2.7, 0.7, big, size=30, font=HEAD, bold=True, color=EMBER)
    text(s, x, 5.4, 2.7, 0.4, small, size=14, color=SAND)
text(s, 0.8, 6.35, 12, 0.5, [[("Anoon M R", {"bold": True, "color": WHITE}), ("  ·  25MCAR0179  ·  MCA AIML, Sem III  ·  Faculty: Prof. Rahul Pawar", {"color": SAND})]], size=14)
slide_no[0] += 1
s.notes_slide.notes_text_frame.text = ("Introduce the question: a forest agency has limited crews and needs to know when, why and where "
                                       "fire danger is highest. This deck tells that story with ten visualizations, a dashboard and a model.")

# ============ 2. DATA ============
s = content_slide("513 days of park weather — when is fire danger highest?", "The data",
                  "Explain the dataset: each row is a day and a grid cell in Montesinho Park, 2000-2003, with Fire Weather Index codes, weather and burned area.")
stats = [(f"{M['rows_clean']}", "clean observations\n(517 raw, 4 duplicates removed)"), (f"{M['fire_rate']:.0f}%", "of observations had a fire"),
         (f"{M['total_area']:,.0f} ha", "total area burned"), (f"{M['max_area']:,.0f} ha", "largest single fire")]
for i, (big, small) in enumerate(stats):
    x = 0.6 + i * 3.08
    box(s, x, 1.75, 2.85, 1.9, SOFT)
    text(s, x + 0.25, 1.95, 2.4, 0.8, big, size=36, font=HEAD, bold=True, color=BROWN)
    text(s, x + 0.25, 2.8, 2.4, 0.8, small, size=13, color=INK2)
text(s, 0.6, 4.0, 6, 0.4, "13 attributes", size=17, bold=True)
bullets(s, 0.6, 4.45, 6.0, 2.5, ["**Where:** X, Y position on a 9 × 9 park grid",
                                 "**When:** month and day of week",
                                 "**Weather:** temperature, humidity, wind, rain",
                                 "**Fire Weather Index codes:** FFMC, DMC, DC, ISI",
                                 "**Outcome:** burned area in hectares"], size=15)
text(s, 7.0, 4.0, 5.7, 0.4, "Source", size=17, bold=True)
text(s, 7.0, 4.45, 5.7, 2.2, ["UCI Machine Learning Repository — Forest Fires",
                              "Cortez & Morais (2007), Montesinho Natural Park, north-east Portugal",
                              "Open dataset · climate / environment domain"], size=15, color=INK2, spacing=8)

# ============ 3. DATA PREP ============
s = content_slide("Clean, check, and keep the extreme fires — they are the story", "Data preparation",
                  "No missing values. 4 duplicate rows removed. Range checks passed. Outliers were kept because they are real events, not errors. Engineered season, size class, dryness and temperature bands.")
steps = [("1", "Quality checks", "0 missing values · all range checks pass · 4 exact duplicates removed"),
         ("2", "Outliers kept", "Rainy days, windy days and fires up to 1,091 ha are real events, not errors"),
         ("3", "Skew handled", f"Median fire only {M['median_fire_area']} ha → plot log(1 + area)"),
         ("4", "New features", "season · fire-size class · fuel-dryness band · temperature band · peak period · weekday/weekend")]
for i, (n, h, d) in enumerate(steps):
    y = 1.75 + i * 1.25
    circle_num(s, 0.6, y, 0.7, n)
    text(s, 1.55, y - 0.02, 5.2, 0.4, h, size=18, bold=True)
    text(s, 1.55, y + 0.38, 5.4, 0.8, d, size=14, color=INK2)
box(s, 7.4, 1.75, 5.3, 4.9, SOFT)
text(s, 7.7, 1.95, 4.8, 0.4, "Fire-size classes used in every chart", size=16, bold=True)
for i, (lbl, col, n) in enumerate([("No fire", RGBColor(0xB9, 0xB7, 0xAE), 244), ("Small  < 1 ha", RGBColor(0xF0, 0x91, 0x5C), 27),
                                   ("Medium  1–10 ha", RGBColor(0xC9, 0x50, 0x1F), 148), ("Large  > 10 ha", BROWN, 94)]):
    y = 2.6 + i * 0.95
    box(s, 7.7, y, 0.55, 0.55, col)
    text(s, 8.45, y + 0.05, 2.8, 0.5, lbl, size=16)
    text(s, 11.3, y + 0.05, 1.1, 0.5, f"n = {n}", size=15, color=INK2, align=PP_ALIGN.RIGHT)

# ============ ACT 1 ============
s = content_slide(f"August + September: {aug_sep_obs:.0f}% of the days, {aug_sep_area:.0f}% of the hectares burned", "Act 1 · When — proportions",
                  "Read the two bars: top is share of observations, bottom is share of burned area. September punches above its weight: 34% of days but 47% of damage.")
picture(s, "fig01_proportions.png", 0.6, 1.65, 8.4, 4.0)
takeaway_panel(s, 9.3, 1.65, 3.45, 5.1, "What it means", ["Two months decide the fire year", "September fires are larger than their share of days", "March: 10% of days, only 3% of damage"],
               stat=f"{aug_sep_area:.0f}%", stat_label="of burned hectares fall in Aug–Sep")

s = content_slide("A handful of large fires cause most of the damage", "Act 1 · When — concentration",
                  "Rank the fires from largest to smallest and accumulate their area. Ten fires make half the damage; 50 fires (19%) make 80%.")
picture(s, "fig02_concentration.png", 0.6, 1.65, 8.4, 4.9)
takeaway_panel(s, 9.3, 1.65, 3.45, 5.1, "What it means", [f"Top {M['n_fires_for_80']} fires ({M['pct_fires_for_80']:.0f}%) = 80% of area", f"Median fire is just {M['median_fire_area']} ha", "Goal: stop the few that grow large"],
               stat=f"{M['top10_share']:.0f}%", stat_label="of all burned area comes from the 10 largest fires")

s = content_slide("Treemap: September and August drive almost all burned hectares", "Act 1 · When — nested proportions",
                  "Treemap: rectangle size is hectares burned, nested season then month. Colour is fire rate. December is dark but based on only 9 observations.")
picture(s, "fig03_treemap.png", 0.6, 1.6, 8.6, 5.25)
takeaway_panel(s, 9.5, 1.65, 3.25, 5.1, "Reading the treemap", ["**Size** = hectares burned", "**Colour** = share of observations with a fire", "Sep 3,086 ha · Aug 2,298 ha", "Spring & Winter are small slivers", "Dec is dark but n = 9 only"])

s = content_slide("Mosaic plot: Autumn has the most large fires", "Act 1 · When — mosaic plot",
                  "Column width = share of observations in each season; segment height = share of each fire-size class within that season.")
picture(s, "fig04_mosaic.png", 0.6, 1.6, 8.6, 5.25)
sp = M["season_props"]
takeaway_panel(s, 9.5, 1.65, 3.25, 5.1, "Reading the mosaic", ["**Width** = how many observations", "**Height** = mix of fire sizes", f"Large fires: Autumn {sp['Autumn']['Large (>10 ha)']:.0f}% vs Summer {sp['Summer']['Large (>10 ha)']:.0f}%",
                                                              f"Spring: {sp['Spring']['No fire']:.0f}% no-fire days", "Winter (n = 31): 0% small fires"])

s = content_slide("Heat peaks in July, but drought keeps building until September", "Act 1 · When — small multiples",
                  "Four panels, each on its own scale, no dual axis. Drought Code is cumulative, so it keeps rising after temperature has peaked. Faded points have fewer than 5 observations.")
picture(s, "fig05_seasonal_small_multiples.png", 0.6, 1.75, 12.1, 3.3)
for i, (h, d) in enumerate([("Temperature", "Peaks in July at ≈ 23 °C"), ("Humidity", "Barely moves — around 40% all summer"),
                            ("Drought Code", "Rises to ≈ 730 in September"), ("Fire rate", "≈ 55% in July–September")]):
    x = 0.6 + i * 3.08
    box(s, x, 5.3, 2.85, 1.45, SOFT)
    text(s, x + 0.22, 5.42, 2.4, 0.4, h, size=15, bold=True, color=BROWN)
    text(s, x + 0.22, 5.85, 2.45, 0.8, d, size=14, color=INK)

# ============ ACT 2 ============
mx = max(abs(v) for v in M["corr_with_log_area"].values())
s = content_slide("Weather variables move together — but none tracks fire size", "Act 2 · Why — correlogram",
                  f"Strong pairs: DMC-DC 0.68, temperature-humidity -0.53, FFMC-ISI 0.53. But the bottom row, log(area), never exceeds |r| = {mx:.2f}.")
picture(s, "fig06_correlogram.png", 0.6, 1.55, 6.6, 5.35)
takeaway_panel(s, 7.6, 1.65, 5.15, 5.1, "What it means", ["**DMC ↔ DC  r = 0.68** — both measure accumulated dryness", "**Temp ↔ RH  r = −0.53** — hot days are dry days", "**FFMC ↔ ISI  r = 0.53**",
                                                         "Weather sets the stage, but alone it does not decide how big a fire gets"],
               stat=f"|r| ≤ {mx:.2f}", stat_label="strongest correlation of any weather variable with fire size")

s = content_slide("Scatter: the hot & dry corner produces the biggest fires on average", "Act 2 · Why — scatter plot",
                  "Fires of every size appear everywhere, so there is no clean boundary. But in the shaded corner (above 22 C, RH below 35%) the average fire is three times larger.")
picture(s, "fig07_scatter_temp_rh.png", 0.6, 1.6, 8.4, 5.3)
box(s, 9.3, 1.65, 3.45, 5.1, SOFT)
text(s, 9.6, 1.9, 3.0, 0.4, "Hot & dry  vs  other days", size=15, bold=True)
for i, (lbl, a, b) in enumerate([("Average fire", f"{hd['mean_area']:.0f} ha", f"{rest['mean_area']:.0f} ha"),
                                 ("Fire rate", f"{hd['fire_rate']:.0f}%", f"{rest['fire_rate']:.0f}%"),
                                 ("Large-fire rate", f"{hd['large_rate']:.0f}%", f"{rest['large_rate']:.0f}%")]):
    y = 2.5 + i * 1.3
    text(s, 9.6, y, 3.0, 0.35, lbl, size=13, color=INK2)
    text(s, 9.6, y + 0.32, 1.5, 0.7, a, size=28, font=HEAD, bold=True, color=BROWN)
    text(s, 11.1, y + 0.42, 1.5, 0.6, f"vs {b}", size=17, color=INK2)
text(s, 9.6, 6.25, 3.0, 0.4, f"n = {hd['n']} hot & dry days", size=12, color=INK2, italic=True)

s = content_slide("PCA: eight weather variables collapse onto one 'dryness & heat' axis", "Act 2 · Why — dimension reduction",
                  "PCA on 8 standardized variables. PC1 (36%) loads on temperature, FFMC, ISI, DMC, DC; humidity points the other way. Peak season sits on the dry side.")
picture(s, "fig08_pca.png", 0.6, 1.6, 12.1, 4.6)
evr = M["pca_evr"]
text(s, 0.6, 6.3, 12.1, 0.6, [[("PC1 = ", {}), (f"{evr[0]:.0f}% ", {"bold": True, "color": BROWN}), ("of variance  ·  peak-season days (orange) sit on the hot/dry side  ·  3 components keep ", {}),
                               (f"{sum(evr):.0f}%", {"bold": True, "color": BROWN}), (" of the information", {})]], size=15, color=INK)

s = content_slide("Parallel sets: dry fuel is the backdrop of the season, not the trigger", "Act 2 · Why — parallel sets",
                  "Follow the ribbons left to right: season, fine-fuel dryness, temperature band, outcome. Most observations are dry-fuel days, and they flow into every outcome including No fire.")
picture(s, "fig09_parallel_sets.png", 0.6, 1.6, 8.9, 5.3)
takeaway_panel(s, 9.8, 1.65, 2.95, 5.1, "What it means", ["Dry-fuel ribbons reach every outcome", "An ignition is still needed — often human", "Combine weather with ignition data"],
               stat=f"{M['ffmc_dry_share']:.0f}%", stat_label="of observations already have dry fine fuel (FFMC ≥ 90)")

# ============ ACT 3 ============
s = content_slide(f"Two grid cells hold {two_cells:.0f}% of all hectares burned", "Act 3 · Where — spatial hotspots",
                  "Three heatmaps of the 9 x 9 park grid: observations, fire rate (cells with at least 5 observations) and total hectares. Cells (6,5) and (8,6) stand out.")
picture(s, "fig10_spatial_grid.png", 0.6, 1.6, 12.1, 4.5)
for i, c in enumerate(cells[:2]):
    x = 0.6 + i * 6.15
    box(s, x, 6.15, 5.95, 0.75, SOFT)
    text(s, x + 0.25, 6.22, 5.5, 0.6, [[(f"Cell (X={c['X']}, Y={c['Y']})   ", {"bold": True}), (f"{c['burned_ha']:,.0f} ha burned · {c['fires']} fires in {c['obs']} observations", {"color": INK2})]],
         size=15, anchor=MSO_ANCHOR.MIDDLE)

# ============ DASHBOARD ============
s = content_slide("The dashboard: one filter row drives every chart and KPI", "Interactive dashboard · Plotly Dash",
                  "Demo: change the season or month range and every KPI and chart updates. Hover any mark for details. Run with: python dashboard/app.py, then open localhost:8050.")
picture(s, "dashboard/dash_top.png", 0.6, 1.55, 8.3, 5.4)
takeaway_panel(s, 9.2, 1.65, 3.55, 5.1, "Built with Python", ["**Filters:** season, months, weekday / weekend", "**KPIs:** observations, fire rate, hectares, largest fire, temperature",
                                                             "**6 linked charts** with hover tooltips", "Offline copy: Wildfire_Dashboard.html"])

s = content_slide("Early-warning risk check: from weather inputs to a risk tier", "Interactive dashboard · risk predictor",
                  "Demo the risk check: pick August, cell (6,5), 22 C, 40% humidity. The model returns a tier and how often days in that tier burned historically.")
picture(s, "dashboard/dash_bottom.png", 0.6, 1.55, 8.3, 5.4)
takeaway_panel(s, 9.2, 1.65, 3.55, 5.1, "How officers use it", ["Choose month, grid cell and the day's weather", "Random Forest returns **Low / Moderate / High**", "Shows the historical fire rate of that tier",
                                                               "Used to **rank** days for patrols — not as a yes/no alarm"])

# ============ MODEL ============
rfm = cv["Random Forest (300 trees)"]
s = content_slide("Random Forest wins — weather gives a modest but real signal", "Act 4 · What next — model",
                  "Four models compared with 5x5 repeated stratified cross-validation (25 fits each). Random Forest wins at 0.60. A single hold-out split gave 0.68, which shows why cross-validation matters.")
picture(s, "fig11_model_comparison.png", 0.6, 1.65, 8.4, 3.6)
takeaway_panel(s, 9.3, 1.65, 3.45, 5.1, "Honest evaluation", ["25 cross-validation fits per model", "Baseline = 0.50 (coin flip)", f"Single split said {M['holdout_auc']:.2f} — too optimistic",
                                                             "Top inputs: DMC, temperature, humidity"],
               stat=f"{rfm[0]:.2f}", stat_label=f"cross-validated ROC-AUC (± {rfm[1]:.2f})")
bullets(s, 0.6, 5.45, 8.4, 1.4, ["**Target:** fire (any area burned) · 52% positive — balanced classes",
                                 "**Features:** location, month, day, FFMC, DMC, DC, ISI, temperature, humidity, wind, rain"], size=14, gap=4)

s = content_slide(f"Risk tiers: High-tier days burned {tiers['High']['fire_rate']:.0f}% of the time vs {tiers['Low']['fire_rate']:.0f}% for Low", "Act 4 · What next — risk tiers",
                  "Out-of-fold predictions split into three equal tiers. The fire rate climbs from Low to High, so the ranking works. But the large-fire rate is flat at about 18%, so the model cannot predict size.")
picture(s, "fig12_risk_tiers.png", 0.6, 1.65, 12.1, 3.9)
box(s, 0.6, 5.75, 12.1, 1.1, SOFT)
text(s, 0.9, 5.82, 11.6, 0.95, [[("Useful: ", {"bold": True, "color": BROWN}), ("the model ranks days by how likely a fire is.   ", {}),
                                 ("Limit: ", {"bold": True, "color": BROWN}), (f"large fires are ≈ {tiers['Low']['large_rate']:.0f}% in every tier — it cannot predict how big a fire will grow.", {})]],
     size=16, anchor=MSO_ANCHOR.MIDDLE)

# ============ INSIGHTS ============
s = content_slide("Six actions for the forest agency", "Actionable insights",
                  "Walk through each action and the evidence behind it.")
acts = [("Staff up for Aug–Sep", f"{aug_sep_area:.0f}% of hectares burn in these two months — concentrate crews and aerial patrols"),
        ("Fast initial attack", f"The 10 largest fires = {M['top10_share']:.0f}% of damage — stop fires before they grow"),
        ("DC as readiness trigger", "Raise readiness when the Drought Code passes ≈ 600 (typical of Aug–Sep)"),
        ("Hot & dry day protocol", f"> 22 °C and RH < 35%: average fire {hd['mean_area']:.0f} ha — pre-position tenders, restrict campfires"),
        ("Protect two hotspots", f"Cells (6,5) and (8,6) = {two_cells:.0f}% of hectares — towers, cameras, fuel breaks"),
        ("Rank days with the model", "Use the dashboard risk tier to prioritise patrols — not as a yes/no alarm")]
for i, (h, d) in enumerate(acts):
    col, row = i % 3, i // 3
    x, y = 0.6 + col * 4.1, 1.75 + row * 2.6
    box(s, x, y, 3.85, 2.35, SOFT)
    circle_num(s, x + 0.25, y + 0.25, 0.55, str(i + 1), size=15)
    text(s, x + 0.95, y + 0.28, 2.75, 0.55, h, size=17, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.25, y + 1.0, 3.4, 1.3, d, size=14, color=INK2)

# ============ CONCLUSION ============
s = prs.slides.add_slide(BLANK); bg(s, DARK)
text(s, 0.8, 0.7, 11, 0.4, "CONCLUSION", size=13, color=EMBER, bold=True)
text(s, 0.8, 1.2, 11.8, 1.0, "Seasonal, concentrated, and driven by accumulated dryness", size=36, font=HEAD, bold=True, color=WHITE)
for i, (h, d) in enumerate([("When", f"Aug–Sep = {aug_sep_area:.0f}% of hectares"), ("Why", "Heat + drought build-up; weather sets the stage"),
                            ("Where", f"Two cells = {two_cells:.0f}% of hectares"), ("What next", f"Risk tiers, CV ROC-AUC {rfm[0]:.2f}")]):
    x = 0.8 + i * 3.0
    circle_num(s, x, 2.75, 0.6, str(i + 1), fill=EMBER, size=16)
    text(s, x, 3.5, 2.75, 0.5, h, size=20, bold=True, color=EMBER)
    text(s, x, 4.0, 2.75, 1.1, d, size=15, color=SAND)
text(s, 0.8, 5.35, 11.8, 1.2, [[("Limitation: ", {"bold": True, "color": WHITE}),
                                ("513 observations from one park; weather explains when danger is high, not which exact plot will burn — "
                                 "ignition data (roads, tourism, lightning) is the next step.", {"color": SAND})]], size=15)
footer(s, dark=True)
s.notes_slide.notes_text_frame.text = "Summarise the four acts and be honest about the limitation."

s = prs.slides.add_slide(BLANK); bg(s, DARK)
text(s, 0.8, 2.4, 11.7, 1.2, "Thank you", size=54, font=HEAD, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
text(s, 0.8, 3.65, 11.7, 0.6, "Questions?", size=24, color=EMBER, align=PP_ALIGN.CENTER)
text(s, 0.8, 5.2, 11.7, 0.9, ["Anoon M R · 25MCAR0179 · MCA AIML",
                              "Data: Cortez & Morais (2007), UCI Machine Learning Repository · Tools: Python, pandas, scikit-learn, Matplotlib, Plotly Dash"],
     size=14, color=SAND, align=PP_ALIGN.CENTER, spacing=6)
footer(s, dark=True)

out = A2 / "Activity2_Presentation.pptx"
prs.save(out)
print("Wrote", out, "slides:", len(prs.slides))
