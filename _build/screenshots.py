"""Capture the screenshots used in the report's 'Screenshots' section.

Starts the Dash app, screenshots it with headless Chrome (default, filtered, Low-risk views), stops it,
then renders selected notebook cells (code + output) to HTML and screenshots those too.
Output: figures/dashboard/*.png and figures/notebook/*.png
"""
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from PIL import Image, ImageChops

A2 = Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DASH_DIR, NB_DIR = A2 / "figures" / "dashboard", A2 / "figures" / "notebook"
DASH_DIR.mkdir(parents=True, exist_ok=True); NB_DIR.mkdir(parents=True, exist_ok=True)
TMP = Path(tempfile.gettempdir()) / "a2_screens"; TMP.mkdir(exist_ok=True)   # intermediates (never deleted by us)
URL = "http://127.0.0.1:8050/"
LOW_RISK = "?p_month=3&p_cell=2,2&p_temp=8&p_rh=75&p_wind=4&p_ffmc=85&p_dmc=20&p_dc=60&p_isi=3"
PREDICTOR_BOX = (720, 1510, 1410, 2065)        # predictor card inside a 1440 x 2120 page


def shoot(url, out, w=1440, h=2120):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
                    "--virtual-time-budget=20000", f"--screenshot={out}", url],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def trim(path, pad=24):
    im = Image.open(path).convert("RGB")
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if bbox:
        l, t, r, b = bbox
        im.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, im.width), min(b + pad, im.height))).save(path)


# ---------------- dashboard ----------------
app = subprocess.Popen([sys.executable, str(A2 / "dashboard" / "app.py")], cwd=A2 / "dashboard",
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(60):
        try:
            urllib.request.urlopen(URL, timeout=2); break
        except OSError:
            time.sleep(1)
    full = DASH_DIR / "dash_full.png"
    shoot(URL, full)
    im = Image.open(full)
    im.crop((0, 0, 1440, 1080)).save(DASH_DIR / "dash_top.png")
    im.crop((0, 1080, 1440, 2100)).save(DASH_DIR / "dash_bottom.png")
    im.crop(PREDICTOR_BOX).save(DASH_DIR / "risk_high.png")

    shoot(URL + "?season=Summer&day=Weekend", TMP / "dash_filtered_full.png")
    Image.open(TMP / "dash_filtered_full.png").crop((0, 0, 1440, 1080)).save(DASH_DIR / "dash_filtered.png")

    shoot(URL + LOW_RISK, TMP / "dash_lowrisk_full.png")
    Image.open(TMP / "dash_lowrisk_full.png").crop(PREDICTOR_BOX).save(DASH_DIR / "risk_low.png")
finally:
    app.terminate()

# ---------------- notebook excerpts ----------------
nb = nbformat.read(A2 / "Activity2_Data_Storytelling.ipynb", as_version=4)
EXCERPTS = {
    "nb_quality_checks": ["Missing values per column", "Range checks against"],
    "nb_cleaning": ["df = raw.drop_duplicates()", "summary = {"],
    "nb_model_cv": ["rcv = RepeatedStratifiedKFold", "Out-of-fold ROC-AUC"],
}
exporter = HTMLExporter(template_name="lab")
for name, needles in EXCERPTS.items():
    cells = []
    for c in nb.cells:
        if c.cell_type == "code" and any(n in c.source for n in needles):
            c = nbformat.from_dict(c)
            c.outputs = [o for o in c.outputs if "image/png" not in o.get("data", {})]   # keep text/table outputs only
            cells.append(c)
    sub = nbformat.v4.new_notebook(cells=cells, metadata=nb.metadata)
    html, _ = exporter.from_notebook_node(sub)
    page = TMP / f"{name}.html"
    page.write_text(html, encoding="utf-8")
    out = NB_DIR / f"{name}.png"
    shoot(page.as_uri(), str(out), w=1150, h=3200)
    trim(out)
    print("captured", out.name, Image.open(out).size)
print("dashboard + notebook screenshots done")
