import os, sys

# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp/pymupdf.zip')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp/lxml.zip')
sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp/a.zip')
sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/libs')

import pdf2docx

PDF = "/home/atlas/Downloads/test/bug/3-字体变黑黑框.pdf"
OUTPUT = "output.docx"

cv = pdf2docx.Converter(PDF)
try:
    cv.convert(OUTPUT)
    os.remove(OUTPUT)
    print(f"done")
except Exception as e:
    pass
finally:
    cv.close()
