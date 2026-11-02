"""Convert notebook_source.py ('# %%' cell markers) into an executed Jupyter notebook."""
import re
import sys
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

A2 = Path(__file__).resolve().parent.parent
src = (A2 / "_build" / "notebook_source.py").read_text(encoding="utf-8")

cells = []
for block in re.split(r"^# %%", src, flags=re.M)[1:]:
    header, _, body = block.partition("\n")
    body = body.strip("\n")
    if "[markdown]" in header:
        md = "\n".join(line[2:] if line.startswith("# ") else line.lstrip("#") for line in body.splitlines())
        cells.append(nbformat.v4.new_markdown_cell(md))
    else:
        cells.append(nbformat.v4.new_code_cell(body))

nb = nbformat.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
out = A2 / "Activity2_Data_Storytelling.ipynb"
if "--no-exec" not in sys.argv:
    ExecutePreprocessor(timeout=900, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(A2)}})
nbformat.write(nb, out)
print("Wrote", out)
