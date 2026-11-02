"""Build Activity2_Report.docx from the notebook outputs (figures/ + outputs/metrics.json)."""
import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

A2 = Path(__file__).resolve().parent.parent
FIG = A2 / "figures"
M = json.loads((A2 / "outputs" / "metrics.json").read_text())

BROWN = RGBColor(0x7A, 0x2A, 0x0E)
INK2 = RGBColor(0x52, 0x51, 0x4E)
FONT = "Calibri"

doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Cm(2.3))
sec.top_margin = sec.bottom_margin = Cm(2.2)

st = doc.styles["Normal"]
st.font.name = FONT; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.15
for lvl, size in [(1, 16), (2, 13), (3, 11.5)]:
    h = doc.styles[f"Heading {lvl}"]
    h.font.name = FONT; h.font.size = Pt(size); h.font.bold = True; h.font.color.rgb = BROWN
    rf = h.element.rPr.rFonts
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), FONT)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    h.paragraph_format.space_before = Pt(16 if lvl == 1 else 10); h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True


# ---------- helpers ----------
def para(text="", bold=False, size=None, align=None, color=None, italic=False, space_after=None, style=None):
    p = doc.add_paragraph(style=style)
    if text:
        add_runs(p, text, bold=bold, size=size, color=color, italic=italic)
    if align: p.alignment = align
    if space_after is not None: p.paragraph_format.space_after = Pt(space_after)
    return p


def add_runs(p, text, bold=False, size=None, color=None, italic=False):
    """Supports **bold** segments inside text."""
    parts = text.split("**")
    for i, part in enumerate(parts):
        if not part: continue
        r = p.add_run(part)
        r.bold = bold or (i % 2 == 1); r.italic = italic
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
    return p


def bullets(items, style="List Bullet"):
    for it in items:
        p = doc.add_paragraph(style=style)
        add_runs(p, it)
        p.paragraph_format.space_after = Pt(3)


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def table(rows, widths, header=True, size=9.5):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j])
            c.paragraphs[0].text = ""
            add_runs(c.paragraphs[0], str(val), bold=(header and i == 0), size=size,
                     color=RGBColor(255, 255, 255) if header and i == 0 else None)
            c.paragraphs[0].paragraph_format.space_after = Pt(0)
            c.paragraphs[0].paragraph_format.keep_with_next = i < len(rows) - 1   # keep table on one page
            if header and i == 0: shade(c, "7A2A0E")
            elif i % 2 == 0: shade(c, "F6F4F0")
    for j, w in enumerate(widths):
        for cell in t.columns[j].cells: cell.width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


fig_no = [0]
def figure(name, caption, width_cm=16.2):
    doc.add_picture(str(FIG / name), width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    fig_no[0] += 1
    p = para(f"Figure {fig_no[0]}: {caption}", italic=True, size=9.5, color=INK2, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
    return p


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def field(p, instr, placeholder="Right-click → Update Field to build the table of contents."):
    r = p.add_run(); b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin"); r._r.append(b)
    r = p.add_run(); t = OxmlElement("w:instrText"); t.set(qn("xml:space"), "preserve"); t.text = instr; r._r.append(t)
    r = p.add_run(); s = OxmlElement("w:fldChar"); s.set(qn("w:fldCharType"), "separate"); r._r.append(s)
    p.add_run(placeholder)
    r = p.add_run(); e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end"); r._r.append(e)


# ---------- numbers ----------
st_ = {r["grp"]: r for r in M["share_table"]}
aug_sep_obs = st_["August"]["% of observations"] + st_["September"]["% of observations"]
aug_sep_area = st_["August"]["% of burned area"] + st_["September"]["% of burned area"]
cv = M["cv_auc"]; rep = M["holdout_report"]; cm = M["confusion"]
tiers = {t["risk_tier"]: t for t in M["tiers"]}
hd, rest = M["hot_dry"], M["rest"]
cells = M["top_cells"]
two_cells = (cells[0]["burned_ha"] + cells[1]["burned_ha"]) / M["total_area"] * 100
imp = list(M["importance"].items())

# ======================= COVER PAGE =======================
for _ in range(2): para()
for t, s, b in [("DEPARTMENT OF COMPUTER SCIENCE AND IT", 15, True), ("MCA PROGRAMME", 13, True), ("ACADEMIC YEAR: 2026-2027", 12, False)]:
    para(t, bold=b, size=s, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
for _ in range(3): para()
para("ACTIVITY – 2", bold=True, size=22, align=WD_ALIGN_PARAGRAPH.CENTER, color=BROWN)
para("Data Storytelling Through Visualization", italic=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, color=INK2)
para("“When does Montesinho burn — and what can a forest agency do about it?”", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, color=INK2)
for _ in range(2): para()
para("PREDICTIVE ANALYTICS AND DATA VISUALIZATION", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
para("25MCAAI302", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
para("SEM: III     SPECIALIZATION: MCA-AIML", size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
for _ in range(6): para()
t = doc.add_table(rows=1, cols=2)
left, right = t.cell(0, 0), t.cell(0, 1)
left.paragraphs[0].text = ""
add_runs(left.paragraphs[0], "FACULTY NAME:", bold=True)
left.add_paragraph("Prof. Rahul Pawar"); left.add_paragraph("Assistant Prof., Dept. of CS & IT.")
right.paragraphs[0].text = ""
add_runs(right.paragraphs[0], "STUDENT NAME: ", bold=True); right.paragraphs[0].add_run("Anoon M R")
p = right.add_paragraph(); add_runs(p, "USN: ", bold=True); p.add_run("25MCAR0179")
for c in (left, right): c.width = Cm(8.2)
right.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
for p in right.paragraphs: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
page_break()

# ======================= CERTIFICATE =======================
for _ in range(3): para()
para("Certificate", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER, color=BROWN)
para()
p = para("This is to certify that **Anoon M R (25MCAR0179)** satisfactorily completed the Activity-2 prescribed by the "
         "Jain (Deemed-to-be University) for the semester III M.C.A course in the year 2026-2027.", size=13)
p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.line_spacing = 1.6
para()
para("Date:      /11/2026", size=12)
for _ in range(8): para()
t = doc.add_table(rows=1, cols=2)
t.cell(0, 0).paragraphs[0].text = "Signature of Student"
t.cell(0, 1).paragraphs[0].text = "Signature of Faculty Incharge"
t.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
page_break()

# ======================= BODY =======================
# Sections live in report_body.py (compulsory: TOC, Problem Statement, Dataset, Solution, Screenshots, Conclusion, References)
exec(compile((Path(__file__).with_name("report_body.py")).read_text(encoding="utf-8"), "report_body.py", "exec"))

# footer page numbers (none on the cover page)
for s in doc.sections:
    s.different_first_page_header_footer = True
    p = s.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Activity 2 · 25MCAAI302 · Anoon M R (25MCAR0179) · Page "); r.font.size = Pt(8.5); r.font.color.rgb = INK2
    field(p, "PAGE", "1")
    for r in p.runs: r.font.size = Pt(8.5)

out = A2 / "Activity2_Report.docx"
doc.save(out)
print("Wrote", out)
