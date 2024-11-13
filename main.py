import os, sys
from pathlib import Path

# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp/pymupdf.zip')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp/lxml.zip')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/temp/a.zip')
# sys.path.append('/home/atlas/Projects/Python/archive/.venv/lib/python3.8/site-packages/libs')

# %%
import secretzipimport as importer

ARCHIVE_FOLDER = "site-packages/temp"
ARCHIVE_INTERNAL = "_internal.so"
ARCHIVE_CRYPTO = "archive.zip"
ARCHIVE_PASSED = b'a\0t\0l\0a\0s\0'

# %%
def archive_zip(dstzip: Path, srcdir: Path):
    with importer.ZipFile(dstzip.as_posix(), mode="w", compression=importer.ZIP_DEFLATED) as zip:
        for file in srcdir.rglob("*"):
            if not file.is_file():
                continue
            zip.write(file, file.relative_to(srcdir))


def archive_wrap_with_pwd(dstzip: Path, srczip: Path, pwd: bytes):
    # # Write a zip file
    with importer.AESZipFile(dstzip, "w", encryption=importer.WZ_AES) as fp:
        fp.setpassword(pwd)
        fp.write(srczip.as_posix(), srczip.name)


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

beg = time.perf_counter()
imp = importer.ZipImporterWrapper(ARCHIVE_CRYPTO, ARCHIVE_PASSED)
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
    os.remove(OUTPUT)
    print(f"done")
except Exception as e:
    pass
finally:
    cv.close()
end = time.perf_counter()
print(f'转文件耗时: {end-beg} s')
