"""Convert the report (Word) and presentation (PowerPoint) to PDF using the installed Office apps."""
import sys
from pathlib import Path

import win32com.client as win32

A2 = Path(__file__).resolve().parent.parent


def word_to_pdf(docx):
    word = win32.DispatchEx("Word.Application"); word.Visible = False; word.DisplayAlerts = 0
    word.Options.PrintBackgrounds = True           # dark page colour of the handwritten-text copy
    try:
        doc = word.Documents.Open(str(docx))
        for toc in doc.TablesOfContents:
            toc.Update()
        doc.Fields.Update()
        doc.Save()                                   # keep the filled-in TOC in the .docx too
        doc.ExportAsFixedFormat(str(docx.with_suffix(".pdf")), 17)   # 17 = wdExportFormatPDF
        print("PDF:", docx.with_suffix(".pdf"), "| pages:", doc.ComputeStatistics(2))
        doc.Close(False)
    finally:
        word.Quit()


def ppt_to_pdf(pptx):
    app = win32.DispatchEx("PowerPoint.Application")
    try:
        pres = app.Presentations.Open(str(pptx), True, False, False)   # read-only, no window
        pres.SaveAs(str(pptx.with_suffix(".pdf")), 32)                   # 32 = ppSaveAsPDF
        print("PDF:", pptx.with_suffix(".pdf"), "| slides:", pres.Slides.Count)
        pres.Close()
    finally:
        app.Quit()


if __name__ == "__main__":
    what = sys.argv[1:] or ["report", "ppt"]
    if "report" in what:
        word_to_pdf(A2 / "Activity2_Report.docx")
    if "final" in what:
        word_to_pdf(A2 / "final" / "Activity2_Report_Printout.docx")
        word_to_pdf(A2 / "final" / "Activity2_Handwritten_Text.docx")
        word_to_pdf(A2 / "final" / "Activity2_Handwritten_Text_Short.docx")
    if "ppt" in what:
        ppt_to_pdf(A2 / "Activity2_Presentation.pptx")
