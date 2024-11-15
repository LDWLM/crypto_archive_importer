import os, sys
from pathlib import Path

# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp/pymupdf.zip')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp/lxml.zip')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp/a.zip')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/libs')

# %%
import secretzipimport as importer

ARCHIVE_FOLDER = "./site-packages/temp"
ARCHIVE_INTERNAL = "./_internal.zip"
ARCHIVE_CRYPTO = "./_pdf2docx.so"
ARCHIVE_PASSED = b'atlas'

# %%
def archive_zip(dstzip: Path, srcdir: Path):
    with importer.ZipFile(dstzip.as_posix(), mode="w", compression=importer.ZIP_DEFLATED) as zip:
        for file in srcdir.rglob("*"):
            if not file.is_file():
                continue
            zip.write(file, file.relative_to(srcdir))


def archive_wrap_with_pwd(dstzip: Path, srczip: Path, pwd: bytes):
    # # Write a zip file
    czf = importer.CryptoZipFile(dstzip.as_posix(), ARCHIVE_PASSED)
    czf.write(srczip.as_posix())

def strip_wrap_with_pwd(czf: Path, zip: Path, pwd: bytes):
    # # Write a zip file
    czf = importer.CryptoZipFile(czf.as_posix(), ARCHIVE_PASSED)
    czf.read(zip.as_posix())


# %%
# # 打包一个普通zip文件，用作实际导入内容
import time

beg = time.perf_counter()
archive_zip(Path(ARCHIVE_INTERNAL), Path(ARCHIVE_FOLDER))
end = time.perf_counter()
print(f'生成普通zip包耗时: {end-beg} s')

# 把普通zip文件再通过密码打包，防止普通zip包内部的文件列表泄漏
beg = time.perf_counter()
archive_wrap_with_pwd(Path(ARCHIVE_CRYPTO), Path(ARCHIVE_INTERNAL), ARCHIVE_PASSED)
end = time.perf_counter()
print(f'生成加密zip包耗时: {end-beg} s')

# strip_wrap_with_pwd(Path(ARCHIVE_CRYPTO), Path('output.zip'), ARCHIVE_PASSED)

beg = time.perf_counter()
imp = importer.ZipImporterWrapper(ARCHIVE_CRYPTO, ARCHIVE_PASSED)
imp.load()
end = time.perf_counter()
print(f'读取加密zip包耗时: {end-beg} s')

beg = time.perf_counter()
sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/libs')
import pdf2docx
end = time.perf_counter()
print(f'导入普通zip包耗时: {end-beg} s')

beg = time.perf_counter()

PDF = "/home/atlas/Downloads/test/bug/3-字体变黑黑框.pdf"
OUTPUT = "output.docx"

cv = pdf2docx.Converter(PDF)
try:
    cv.convert(OUTPUT)
    print(f"done")
except Exception as e:
    pass
finally:
    cv.close()
end = time.perf_counter()
print(f'转文件耗时: {end-beg} s')
