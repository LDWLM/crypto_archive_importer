import pdf2docx, os

PDF = "/home/atlas/Downloads/test/bug/3-字体变黑黑框.pdf"
OUTPUT = "output.docx"

cv = pdf2docx.Converter(PDF)
try:
    cv.convert(OUTPUT)
    # os.remove(OUTPUT)
    print(f"done")
except Exception as e:
    pass
finally:
    cv.close()
