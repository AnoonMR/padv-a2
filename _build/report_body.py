# Report body — exec()'d by build_report.py after the cover & certificate pages (shares its helpers/variables).
# Compulsory sections (user's notes, a2/dataset explaination.txt): Table of Contents, Problem Statement Explanation,
# Dataset Explanation, Solution Explanation, Screenshots, Conclusion, References.
import pandas as pd

J = WD_ALIGN_PARAGRAPH.JUSTIFY
clean = pd.read_csv(A2 / "data" / "forestfires_clean.csv")
sw = clean[(clean.season == "Summer") & (clean.day_type == "Weekend")]
raw = pd.read_csv(A2 / "data" / "forestfires.csv")
num_cols = ["FFMC", "DMC", "DC", "ISI", "temp", "RH", "wind", "rain", "area"]
q1, q3 = raw[num_cols].quantile(0.25), raw[num_cols].quantile(0.75)
iqr_out = ((raw[num_cols] < q1 - 1.5 * (q3 - q1)) | (raw[num_cols] > q3 + 1.5 * (q3 - q1))).sum().sort_values(ascending=False)
n_months_sparse = int((clean.groupby("month").size() < 5).sum())


def two_pictures(left, right, cap, width_cm=7.9):
    t = doc.add_table(rows=1, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell, name in zip(t.rows[0].cells, (left, right)):
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].add_run().add_picture(str(FIG / name), width=Cm(width_cm))
        cell.paragraphs[0].paragraph_format.keep_with_next = True
    fig_no[0] += 1
    para(f"Figure {fig_no[0]}: {cap}", italic=True, size=9.5, color=INK2, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)


# ======================= TABLE OF CONTENTS =======================
para("Table of Contents", bold=True, size=16, color=BROWN)
field(doc.add_paragraph(), 'TOC \\o "1-2" \\h \\z \\u')

# ======================= 1. PROBLEM STATEMENT =======================
doc.add_heading("1. Problem Statement Explanation", 1).paragraph_format.page_break_before = True
doc.add_heading("1.1 Background", 2)
para("Wildfires destroy forests, wildlife habitat and property, and Mediterranean parks such as Montesinho Natural Park "
     "in north-east Portugal burn almost every summer. The agency that manages the park has limited fire crews, "
     "vehicles and surveillance hours. Today these resources are largely deployed reactively — after a fire is "
     "reported. To prevent damage instead of only responding to it, the agency needs to understand the pattern behind "
     "past fires and present it in a form that decision-makers can read at a glance.").alignment = J
doc.add_heading("1.2 Problem statement", 2)
t = doc.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER
c = t.cell(0, 0); shade(c, "FBEFE7"); c.width = Cm(16.2)
c.paragraphs[0].text = ""
add_runs(c.paragraphs[0], "Using historical weather and fire records from Montesinho Natural Park, find out **when**, **why** and "
         "**where** forest fires occur and cause the most damage, communicate these findings through clear "
         "visualizations and an interactive dashboard, and turn them into **actionable recommendations** and an "
         "**early-warning risk indicator** for the forest agency.", size=11.5)
c.paragraphs[0].paragraph_format.space_after = Pt(4); c.paragraphs[0].alignment = J
para()
para("The problem is a **data-storytelling** problem: the numbers already exist, but in raw form (513 rows × 13 "
     "columns) they do not tell an officer what to do. The challenge is to choose visual forms that reveal the "
     "pattern honestly — including what the data **cannot** tell us.").alignment = J
doc.add_heading("1.3 Objectives (from the course handbook, CA3)", 2)
bullets(["Create **at least three visualizations** (Scatter Plot, Treemap, Correlogram, Mosaic Plot, etc.) — this report uses ten.",
         "Design a **simple dashboard** using Tableau / Power BI / Python — this activity uses **Python (Plotly Dash)**.",
         "**Interpret** the visualizations and present **actionable insights**.",
         "Deliverables: **Dashboard, Report and Presentation**."])
doc.add_heading("1.4 The questions the story answers", 2)
table([["Act", "Question", "Visualizations used"],
       ["1. When", "When do fires happen, and when does the damage happen?", "Proportion bar, concentration curve, treemap, mosaic plot, small multiples"],
       ["2. Why", "Which weather conditions travel together with fire?", "Correlogram, scatter plot, PCA biplot (dimension reduction), parallel sets"],
       ["3. Where", "Are some parts of the park hotspots?", "Spatial grid heatmaps"],
       ["4. What next", "Can we turn this into an early-warning tool?", "Model comparison, risk tiers, confusion matrix, feature importance"]],
      [2.4, 6.0, 8.0])

# ======================= 2. DATASET =======================
doc.add_heading("2. Dataset Explanation", 1)
doc.add_heading("2.1 Source and collection", 2)
para(f"The data is the **Forest Fires dataset** from the UCI Machine Learning Repository, published by Cortez & Morais "
     f"(2007). It was collected in **Montesinho Natural Park** (Trás-os-Montes, north-east Portugal) between January 2000 "
     f"and December 2003. Each row is one **day-and-location observation**: the park map is divided into a 9 × 9 grid, "
     f"and for each recorded event the grid cell, date, weather readings, Fire Weather Index (FWI) codes and the burned "
     f"area were stored. The raw file has **{M['rows_raw']} rows and 13 columns**. It is an open dataset in the "
     f"climate / environment domain, as required by the activity.").alignment = J
doc.add_heading("2.2 Attributes", 2)
table([["Attribute", "Meaning", "Type", "Range in data"],
       ["X, Y", "Grid coordinates inside the park map (9 × 9 grid)", "Spatial (integer)", "X 1–9, Y 2–9"],
       ["month, day", "Month of the year and day of the week", "Categorical", "jan–dec, mon–sun"],
       ["FFMC", "Fine Fuel Moisture Code (FWI system) — dryness of surface litter", "Numeric index", "18.7 – 96.2"],
       ["DMC", "Duff Moisture Code — dryness of loosely compacted organic layers", "Numeric index", "1.1 – 291.3"],
       ["DC", "Drought Code — long-term dryness of deep organic layers", "Numeric index", "7.9 – 860.6"],
       ["ISI", "Initial Spread Index — expected rate of fire spread", "Numeric index", "0 – 56.1"],
       ["temp", "Temperature (°C)", "Numeric", "2.2 – 33.3"],
       ["RH", "Relative humidity (%)", "Numeric", "15 – 100"],
       ["wind", "Wind speed (km/h)", "Numeric", "0.4 – 9.4"],
       ["rain", "Outside rain (mm/m²)", "Numeric", "0 – 6.4"],
       ["area", "Burned area of the forest (hectares) — the outcome", "Numeric (target)", "0 – 1090.8"]],
      [2.2, 8.0, 2.9, 3.3])
doc.add_heading("2.3 Key characteristics", 2)
bullets([f"**Outcome:** {M['fires']} of {M['rows_clean']} clean observations ({M['fire_rate']}%) had a fire (area > 0); the rest burned nothing.",
         f"**Extremely skewed area:** median fire {M['median_fire_area']} ha but maximum {M['max_area']:,} ha — a few fires dominate the total of {M['total_area']:,.0f} ha.",
         f"**Uneven sampling over the year:** August and September alone hold {aug_sep_obs:.0f}% of the rows, while {n_months_sparse} months have fewer than 5 observations.",
         "**Correlated inputs:** the four FWI codes are computed from the same weather history, so they move together (see the correlogram in Section 3.4).",
         "**Clean structure:** no missing values; only 4 exact duplicate rows."])
doc.add_heading("2.4 Why this dataset fits the problem", 2)
para("It contains exactly the three ingredients the story needs — **time** (month, day), **conditions** (weather and FWI "
     "codes) and **place** (grid cell) — together with a measurable outcome (burned area). It mixes categorical, "
     "numeric and spatial variables, which allows every visualization family in Module 5 of the syllabus: proportions, "
     "nested proportions, associations and dimension reduction. The same dataset was used in Activity 1, which allowed "
     "Activity 2 to go deeper into storytelling rather than starting from scratch (reuse was approved by the faculty).").alignment = J

# ======================= 3. SOLUTION =======================
doc.add_heading("3. Solution Explanation", 1)
doc.add_heading("3.1 Solution overview", 2)
para("The solution is a five-step pipeline implemented in Python. Every number in this report is produced by the "
     "notebook and saved to outputs/metrics.json, so the report, dashboard and presentation always agree.").alignment = J
table([["Step", "What was done", "Tools", "Output"],
       ["1. Prepare", "Quality checks, duplicate removal, feature engineering", "pandas, NumPy", "forestfires_clean.csv"],
       ["2. Visualize", "Ten charts in three acts (When / Why / Where)", "Matplotlib, Plotly", "figures/*.png"],
       ["3. Dashboard", "Interactive dashboard with filters, KPIs, six charts and a risk check", "Plotly Dash", "dashboard/app.py, Wildfire_Dashboard.html"],
       ["4. Model", "Compare four classifiers with cross-validation; build risk tiers", "scikit-learn", "Random Forest risk tiers"],
       ["5. Act", "Translate findings into recommendations", "—", "Section 3.8"]],
      [2.3, 6.4, 3.3, 4.4])
para("A single visual identity is used throughout: a grey-to-dark-orange ordered ramp for fire size, blue vs orange for "
     "two-group comparisons, and a blue–grey–red diverging scale for correlations. The palette was checked with a "
     "colour-blindness validator so that every chart remains readable for colour-vision-deficient readers.",
     italic=True, color=INK2).alignment = J

doc.add_heading("3.2 Data preparation", 2)
doc.add_heading("3.2.1 Data-quality checks", 3)
table([["Check", "Result", "Decision"],
       ["Missing values", "0 in every column", "No imputation needed"],
       ["Exact duplicate rows", f"{M['duplicates_removed']} duplicates", f"Removed → {M['rows_clean']} rows remain"],
       ["Domain/range checks (RH 0–100, FFMC 0–101, area ≥ 0, valid grid, valid month/day labels)", "All PASS", "No corrections needed"],
       ["Outliers (IQR rule)", "In every numeric column — most in " + ", ".join(f"{k} ({v})" for k, v in iqr_out.head(3).items()),
        "Kept — they are real events (rainy days, windy days, catastrophic fires), not recording errors"],
       ["Skewness of area", f"Median fire {M['median_fire_area']} ha, maximum {M['max_area']:,} ha", "Added log(1 + area) for plotting and correlation"]],
      [5.4, 5.4, 5.6])
doc.add_heading("3.2.2 Feature engineering", 3)
bullets(["**season** — Winter (Dec–Feb), Spring (Mar–May), Summer (Jun–Aug), Autumn (Sep–Nov).",
         "**month_num, day_num** — calendar-ordered numeric codes (not alphabetical).",
         "**fire** — 1 if any area burned, else 0 (the model target).",
         "**size_class** — No fire, Small (< 1 ha), Medium (1–10 ha), Large (> 10 ha).",
         "**ffmc_band** — Dry fuel (FFMC ≥ 90) vs Moist fuel; **temp_band** — Cool (< 15 °C), Mild (15–22 °C), Hot (> 22 °C).",
         "**period** — Peak (Aug–Sep) vs Rest of year; **day_type** — Weekday vs Weekend; **log_area** = log(1 + area)."])
para(f"After cleaning: **{M['rows_clean']} observations**, of which **{M['fires']} ({M['fire_rate']}%) had a fire**, "
     f"burning **{M['total_area']:,.0f} hectares** in total.").alignment = J

doc.add_heading("3.3 Act 1 — WHEN: the calendar of fire", 2)
doc.add_heading("3.3.1 Proportions as parts of the total", 3)
figure("fig01_proportions.png", "Share of observations vs share of burned area by month (100% stacked bars)")
para(f"**Interpretation:** August and September together account for **{aug_sep_obs:.0f}% of all observations** but "
     f"**{aug_sep_area:.0f}% of all burned hectares**. September alone holds {st_['September']['% of observations']:.0f}% of "
     f"the observations yet {st_['September']['% of burned area']:.0f}% of the damage — fires in September are larger "
     f"than their share of days would suggest. March has {st_['March']['% of observations']:.0f}% of observations but only "
     f"{st_['March']['% of burned area']:.0f}% of the burned area.").alignment = J
doc.add_heading("3.3.2 Concentration of damage", 3)
figure("fig02_concentration.png", "Cumulative share of burned area, fires ranked from largest to smallest")
para(f"**Interpretation:** the damage is extremely concentrated. The **10 largest fires cause {M['top10_share']:.0f}%** of "
     f"all burned area, and the top {M['n_fires_for_80']} fires (only {M['pct_fires_for_80']:.0f}% of all fires) cause "
     f"80%. The typical (median) fire burns just {M['median_fire_area']} ha. The practical goal is therefore to stop the "
     f"few fires that grow large.").alignment = J
doc.add_heading("3.3.3 Treemap — nested proportions (season → month)", 3)
figure("fig03_treemap.png", "Treemap: rectangle size = hectares burned, colour = fire rate (share of observations with a fire)")
para("**Interpretation:** the nested view shows that Autumn and Summer hold almost all of the burned area, and inside "
     "them a single month dominates each season — September (3,086 ha) and August (2,298 ha). Spring and Winter are "
     "small rectangles. The colour shows fire rates between about 33% and 56% in most months; the darkest cell (December) is "
     "based on only 9 observations, so it should not be over-interpreted.").alignment = J
doc.add_heading("3.3.4 Mosaic plot — season × fire-size class", 3)
figure("fig04_mosaic.png", "Mosaic plot: column width = share of observations per season; segment height = share of each fire-size class")
sp = M["season_props"]
para(f"**Interpretation:** the wide Summer and Autumn columns show that most of the record comes from those seasons. "
     f"Within each season, Autumn has the highest share of large fires among the well-sampled seasons "
     f"({sp['Autumn']['Large (>10 ha)']:.0f}% vs {sp['Summer']['Large (>10 ha)']:.0f}% in Summer), and Spring has the "
     f"most no-fire observations ({sp['Spring']['No fire']:.0f}%). Winter is a thin column (only 31 observations), but "
     f"none of its fires were small — when they happen they reach medium or large size.").alignment = J
doc.add_heading("3.3.5 Small multiples — the dry-season build-up", 3)
figure("fig05_seasonal_small_multiples.png", "Monthly medians of temperature, humidity, Drought Code and the fire rate (faded points: < 5 observations)")
para("**Interpretation:** each variable gets its own panel and its own scale (no misleading dual axis). Temperature "
     "peaks in July (≈ 23 °C) while the Drought Code keeps rising until September (median ≈ 730), because drought "
     "accumulates over weeks. Humidity changes much less (around 40% through the summer). Among the well-sampled "
     "months, the fire rate is highest from July to September (about 55%).").alignment = J

doc.add_heading("3.4 Act 2 — WHY: associations among the weather variables", 2)
doc.add_heading("3.4.1 Correlogram", 3)
figure("fig06_correlogram.png", "Correlogram (Pearson r) of the weather variables and log(1 + area)", width_cm=12.5)
mx = max(abs(v) for v in M["corr_with_log_area"].values())
para(f"**Interpretation:** the weather variables are strongly related to each other — DMC and DC (r = 0.68), "
     f"temperature and humidity (r = −0.53), FFMC and ISI (r = 0.53). However, **no variable is meaningfully correlated "
     f"with fire size — the strongest is only |r| = {mx:.2f}**. Weather sets the stage, but on its own it does not decide "
     f"how big a fire becomes.").alignment = J
doc.add_heading("3.4.2 Scatter plot — temperature vs humidity", 3)
figure("fig07_scatter_temp_rh.png", "Scatter plot of temperature vs relative humidity; colour = fire-size class, marker size ∝ log(burned area)")
para(f"**Interpretation:** fires of every size appear across the whole range of conditions, so there is no clean "
     f"boundary. But the shaded **hot & dry corner (> 22 °C and RH < 35%)** stands out: its {hd['n']} observations "
     f"have a fire rate of {hd['fire_rate']:.0f}% and an **average fire of {hd['mean_area']:.0f} ha**, against "
     f"{rest['fire_rate']:.0f}% and {rest['mean_area']:.0f} ha on all other days.").alignment = J
doc.add_heading("3.4.3 Dimension reduction — PCA", 3)
figure("fig08_pca.png", "PCA biplot of the 8 standardized weather variables (left) and scree plot (right)")
evr = M["pca_evr"]
para(f"**Interpretation:** the first principal component explains {evr[0]:.0f}% of the variance and loads on "
     f"temperature, FFMC, ISI, DMC and DC — a 'dryness & heat' axis — while humidity points the opposite way. Peak-season "
     f"observations (orange) sit on the dry/hot side, and the rest of the year (blue) on the cool/humid side. Three "
     f"components keep about {sum(evr):.0f}% of the information, so eight variables can be summarised by three.").alignment = J
doc.add_heading("3.4.4 Parallel sets — conditions flowing into outcomes", 3)
figure("fig09_parallel_sets.png", "Parallel sets: Season → fine-fuel dryness → temperature band → fire outcome")
para(f"**Interpretation:** {M['ffmc_dry_share']:.0f}% of observations already have dry fine fuel (FFMC ≥ 90), and "
     f"ribbons from the dry-fuel bar flow into every outcome, including 'No fire'. Dry fuel is the **backdrop** of the "
     f"fire season rather than the trigger: an ignition (often human) is still needed.").alignment = J

doc.add_heading("3.5 Act 3 — WHERE: hotspots on the park map", 2)
figure("fig10_spatial_grid.png", "Park grid (X west→east, Y north→south): observations, fire rate and total hectares burned per cell")
para(f"**Interpretation:** two cells — **(X=6, Y=5)** with {cells[0]['burned_ha']:,.0f} ha and **(X=8, Y=6)** with "
     f"{cells[1]['burned_ha']:,.0f} ha — account for **{two_cells:.0f}% of all hectares burned**. They are also two "
     f"of the most frequently observed cells, so they are persistent problem areas.").alignment = J

doc.add_heading("3.6 Interactive dashboard (Python — Plotly Dash)", 2)
para("The dashboard brings the main charts together in one screen so that a forest officer can explore the data "
     "without writing code. Screenshots are given in Section 4.").alignment = J
bullets(["**One filter row** (season, month range, weekday/weekend) that updates every chart and KPI together.",
         "**KPI tiles:** observations, fire rate, hectares burned, largest fire, median temperature.",
         "**Six linked charts:** monthly stacked bars, treemap, scatter plot, park-grid heatmap, parallel sets and correlogram — all with hover tooltips.",
         "**Early-warning risk check:** choose month, grid cell and weather values; the Random Forest returns a Low / Moderate / High tier and the historical fire rate of that tier.",
         "**Shareable views:** filters can be set from the link, e.g. …/?season=Summer&day=Weekend.",
         "**Offline copy:** dashboard/Wildfire_Dashboard.html opens in any browser without Python."])
para("**How to run:**", space_after=2)
for line in ["pip install dash plotly pandas scikit-learn", "python dashboard/app.py", "Open http://127.0.0.1:8050 in a browser"]:
    p = para(line, size=10); p.runs[0].font.name = "Consolas"; p.paragraph_format.left_indent = Cm(1); p.paragraph_format.space_after = Pt(1)
para()

doc.add_heading("3.7 Predictive model — early-warning risk tiers", 2)
doc.add_heading("3.7.1 Setup", 3)
bullets(["**Target:** fire = 1 if any area burned (52% of observations — balanced classes).",
         "**Features (12):** X, Y, month, day, FFMC, DMC, DC, ISI, temperature, RH, wind, rain.",
         "**Models compared:** majority-class baseline, Logistic Regression, Decision Tree (depth 4), Random Forest (300 trees, min_samples_leaf = 5, balanced class weights).",
         "**Evaluation:** 5 × repeated stratified 5-fold cross-validation (25 fits per model) with ROC-AUC, so the result does not depend on one lucky train/test split; plus a 25% hold-out set for the confusion matrix."])
doc.add_heading("3.7.2 Results", 3)
table([["Model", "CV ROC-AUC (mean ± sd)"]] + [[k, f"{v[0]:.3f} ± {v[1]:.3f}"] for k, v in cv.items()], [9.0, 6.0])
figure("fig11_model_comparison.png", "Cross-validated ROC-AUC of the four models (0.5 = coin flip)")
para(f"The **Random Forest is the best model (ROC-AUC {cv['Random Forest (300 trees)'][0]:.2f})**. On the single "
     f"hold-out split it scores {M['holdout_auc']:.2f}, which shows how much one split can flatter a model — the "
     f"cross-validated figure is the honest one.").alignment = J
table([["Hold-out metric", "No fire", "Fire"],
       ["Precision", f"{rep['No fire']['precision']*100:.0f}%", f"{rep['Fire']['precision']*100:.0f}%"],
       ["Recall", f"{rep['No fire']['recall']*100:.0f}%", f"{rep['Fire']['recall']*100:.0f}%"],
       ["F1-score", f"{rep['No fire']['f1-score']:.2f}", f"{rep['Fire']['f1-score']:.2f}"],
       ["Accuracy", f"{rep['accuracy']*100:.1f}%", ""]], [6.0, 4.0, 4.0])
figure("fig13_confusion_importance.png", "Hold-out confusion matrix (left) and permutation importance (right)")
para(f"The confusion matrix shows {cm[1][1]} fires correctly flagged and {cm[1][0]} missed, with {cm[0][1]} false "
     f"alarms. Permutation importance ranks **{imp[0][0]}, {imp[1][0]} and {imp[2][0]}** as the most useful inputs — "
     f"the moisture/drought and heat variables, followed by location (X, Y).").alignment = J
doc.add_heading("3.7.3 From probabilities to risk tiers", 3)
figure("fig12_risk_tiers.png", "Observed fire rate and large-fire rate in each predicted risk tier (out-of-fold predictions)")
para(f"Every observation was scored by a model that never saw it in training, then split into three equal tiers. "
     f"The **High tier burned {tiers['High']['fire_rate']:.0f}% of the time vs {tiers['Low']['fire_rate']:.0f}% in the "
     f"Low tier** — a useful ranking for planning patrols. However, the share of large fires is about "
     f"{tiers['Low']['large_rate']:.0f}% in every tier: the model can rank how likely a fire is, but not how big it "
     f"will grow.").alignment = J

doc.add_heading("3.8 Actionable insights", 2)
table([["#", "What the data shows", "Recommended action"],
       ["1", f"Aug–Sep = {aug_sep_obs:.0f}% of observations and {aug_sep_area:.0f}% of burned hectares.", "Concentrate crews, patrols and aerial surveillance in August–September; schedule leave and maintenance outside this window."],
       ["2", f"The 10 largest fires ≈ {M['top10_share']:.0f}% of all burned area.", "Invest in fast initial attack so that the few fires that would become large are stopped early."],
       ["3", "Drought Code keeps building until September (median ≈ 650–730 in Aug–Sep vs < 100 in spring).", "Use the Fire Weather Index codes (DC, DMC) as a seasonal readiness trigger, e.g. raise readiness when DC exceeds about 600."],
       ["4", f"Hot & dry days (> 22 °C, RH < 35%) average {hd['mean_area']:.0f} ha per observation vs {rest['mean_area']:.0f} ha otherwise.", "On hot & dry forecast days pre-position water tenders and restrict campfires and public access."],
       ["5", f"Fine fuel is dry on {M['ffmc_dry_share']:.0f}% of days, yet many of those days have no fire.", "Combine weather with ignition information (roads, tourism, agricultural burning) — dryness alone is not enough."],
       ["6", f"Cells (6,5) and (8,6) hold {two_cells:.0f}% of burned hectares.", "Place watch-towers / cameras and fuel breaks in those cells first."],
       ["7", f"Random Forest risk tiers: High {tiers['High']['fire_rate']:.0f}% vs Low {tiers['Low']['fire_rate']:.0f}% fire rate.", "Use the dashboard's risk check to rank days for patrol priority — not as a yes/no alarm."]],
      [0.8, 7.0, 8.6])

# ======================= 4. SCREENSHOTS =======================
doc.add_heading("4. Screenshots", 1).paragraph_format.page_break_before = True
para("The screenshots below were captured from the running dashboard (Plotly Dash, http://127.0.0.1:8050) and from the "
     "executed Jupyter notebook (Activity2_Data_Storytelling.ipynb).").alignment = J
doc.add_heading("4.1 Dashboard — overview (all data)", 2)
figure("dashboard/dash_top.png", "Dashboard overview — filter row, KPI tiles, monthly bars, treemap, scatter plot and park grid", width_cm=16.4)
figure("dashboard/dash_bottom.png", "Dashboard overview (continued) — parallel sets, correlogram and the early-warning risk check", width_cm=16.4)
doc.add_heading("4.2 Dashboard — filtered view (Summer weekends)", 2)
figure("dashboard/dash_filtered.png", "Season = Summer and Day type = Weekend: every KPI and chart updates to the selected slice", width_cm=16.4)
para(f"With the filter applied, the KPIs change to **{len(sw)} observations**, a **{sw.fire.mean()*100:.0f}% fire rate** "
     f"and **{sw.area.sum():,.0f} ha** burned, and the treemap shows that August dominates summer-weekend damage. This "
     f"demonstrates that the filters drive every chart at once.").alignment = J
doc.add_heading("4.3 Dashboard — early-warning risk check", 2)
two_pictures("dashboard/risk_high.png", "dashboard/risk_low.png",
             "Risk check for a hot, dry August day in hotspot cell (6,5) → High risk (left), and a cool, humid March day in cell (2,2) → Low risk (right)")
doc.add_heading("4.4 Jupyter notebook — data-quality checks", 2)
figure("notebook/nb_quality_checks.png", "Notebook: missing-value count, duplicate rows, range checks (all PASS) and IQR outlier counts", width_cm=14.5)
doc.add_heading("4.5 Jupyter notebook — cleaning and feature engineering", 2)
figure("notebook/nb_cleaning.png", "Notebook: duplicate removal, engineered features and the cleaned-data summary", width_cm=14.5)
doc.add_heading("4.6 Jupyter notebook — model evaluation", 2)
figure("notebook/nb_model_cv.png", "Notebook: cross-validated ROC-AUC of the four models and the out-of-fold risk-tier table", width_cm=14.5)

# ======================= 5. CONCLUSION =======================
doc.add_heading("5. Conclusion", 1)
doc.add_heading("5.1 Summary of findings", 2)
para(f"Visual storytelling turned 513 rows of weather records into a clear picture: Montesinho's fire problem is "
     f"**seasonal** (August–September hold {aug_sep_area:.0f}% of burned hectares), **concentrated** (the 10 largest fires "
     f"cause {M['top10_share']:.0f}% of the damage and two grid cells {two_cells:.0f}%) and **driven by accumulated dryness and "
     f"heat**. The Plotly Dash dashboard lets officers explore these patterns interactively, and the Random Forest risk "
     f"tiers (cross-validated ROC-AUC {cv['Random Forest (300 trees)'][0]:.2f}) give a modest but real way to rank days by "
     f"fire likelihood. Together they support a shift from reactive fire-fighting to planned, data-driven prevention.").alignment = J
doc.add_heading("5.2 Limitations", 2)
bullets([f"Small dataset (513 observations) from one park and four years; {n_months_sparse} months have fewer than 5 observations.",
         "Weather explains **when** danger is high but not **which exact plot** will burn — ignition sources (people, lightning) are not in the data. This matches the original study (Cortez & Morais, 2007).",
         "Burned area is extremely skewed, so averages are pulled up by a few huge fires; medians and log scales are used where appropriate."])
doc.add_heading("5.3 Future scope", 2)
bullets(["Add ignition-related data (distance to roads and villages, tourist counts, lightning strikes) to improve the model.",
         "Connect the dashboard to a live weather feed so the risk check runs automatically every morning.",
         "Extend the analysis to more parks and years to test whether the hotspots and thresholds generalise."])

# ======================= 6. REFERENCES =======================
doc.add_heading("6. References", 1)
bullets(["Cortez, P. & Morais, A. (2007). A Data Mining Approach to Predict Forest Fires using Meteorological Data. "
         "Proc. 13th EPIA – Portuguese Conference on Artificial Intelligence, pp. 512–523.",
         "UCI Machine Learning Repository — Forest Fires dataset: https://archive.ics.uci.edu/dataset/162/forest+fires",
         "Anasse Bari, Mohamed Chaouchi, Tommy Jung — Predictive Analytics For Dummies, 2nd Ed., Wiley, 2016.",
         "Alexandru Telea — Data Visualization: Principles and Practice, 2nd Ed., CRC Press, 2014.",
         "Brett Lantz — Machine Learning with R: Expert techniques for predictive modeling, 3rd Ed., 2019.",
         "Chun-houh Chen, Wolfgang Härdle, Antony Unwin — Handbook of Data Visualization, Springer, 2008.",
         "Plotly Dash documentation: https://dash.plotly.com",
         "scikit-learn documentation: https://scikit-learn.org"], style="List Number")

doc.add_heading("Appendix — Submission files", 1)
table([["File / folder", "Contents"],
       ["Activity2_Data_Storytelling.ipynb", "Full analysis: cleaning, 10 visualizations, model, insights (executed, with outputs)"],
       ["dashboard/app.py, figures.py, assets/", "Interactive Plotly Dash dashboard"],
       ["dashboard/Wildfire_Dashboard.html", "Offline static copy of the dashboard"],
       ["data/", "Raw dataset, attribute description and cleaned CSV"],
       ["figures/", "All charts and screenshots as PNG"],
       ["Activity2_Report.docx / .pdf", "This report"],
       ["Activity2_Presentation.pptx / .pdf", "Presentation slides"]], [6.4, 10.0])
