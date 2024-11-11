import pdf2docx, os, sys

sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/pymupdf.zip')

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
