# %%
from pathlib import Path
import shutil

import convert_importer_into_cheader, time
from importer import ZipFile, ZIP_DEFLATED, CryptoZipFile

BASEDIR = Path(__file__).parent.absolute()
TEMPDIR = BASEDIR / "temp"

PDF2DOCXAPP = "/home/atlas/PDF2Word_libs/Pdf2DocxApp"
CHEADER = f"{PDF2DOCXAPP}/libpdf2docx/src/main/cpp/importer.h"
SITE_PACKAGES_DIR = f"/home/atlas/Projects/Bin/pdf2docxapp-bin"
SITE_PACKAGES_CRYPT_ARCHIVE = f"{PDF2DOCXAPP}/libpdf2docx/src/main/assets/python/lib/python3.8/site-packages/libalgorithms.so"
SITE_PACKAGES_ARCHIVE = (TEMPDIR / "site-packages.zip").as_posix()
SITE_PACKAGES_TEMP_DIR = (TEMPDIR / "site-packages").as_posix()
IMPORTER = (BASEDIR / "importer.py").as_posix()
SITE_PACKAGES_PASSWD = b"atlas"


# %%
# 压缩
def compress(dstzip: Path, srcdir: Path, with_root: bool = False):
    dstzip.parent.mkdir(exist_ok=True)
    with ZipFile(dstzip.as_posix(), mode="w") as zip:
        for file in srcdir.rglob("*"):
            if not file.is_file():
                continue
            if with_root:
                zip.write(file, file.relative_to(srcdir.parent))
            else:
                zip.write(file, file.relative_to(srcdir))


# 解压
def decompress(dstdir: Path, srczip: Path):
    dstdir.parent.mkdir(exist_ok=True)
    with ZipFile(srczip.as_posix(), mode="r", compression=ZIP_DEFLATED) as zip:
        zip.extractall(dstdir.as_posix())


# 加密
def encrypt(dst: Path, srczip: Path, pwd: bytes):
    dst.parent.mkdir(exist_ok=True)
    czf = CryptoZipFile(dst.as_posix(), pwd)
    czf.encrypt(srczip.as_posix())


# 解密
def decrypt(dstzip: Path, src: Path, pwd: bytes):
    dstzip.parent.mkdir(exist_ok=True)
    czf = CryptoZipFile(src.as_posix(), pwd)
    czf.decrypt(dstzip.as_posix())


# %%

if __name__ == "__main__":
    shutil.rmtree(TEMPDIR, ignore_errors=True)
    TEMPDIR.mkdir(exist_ok=True)

    beg = time.perf_counter()
    compress(dstzip=Path(SITE_PACKAGES_ARCHIVE), srcdir=Path(SITE_PACKAGES_DIR))
    end = time.perf_counter()
    print(f"压缩耗时: {end-beg:.3f} s")

    # 把普通zip文件再通过密码打包，防止普通zip包内部的文件列表泄漏
    beg = time.perf_counter()
    encrypt(
        dst=Path(SITE_PACKAGES_CRYPT_ARCHIVE),
        srczip=Path(SITE_PACKAGES_ARCHIVE),
        pwd=SITE_PACKAGES_PASSWD,
    )
    end = time.perf_counter()
    print(f"加密耗时: {end-beg:.3f} s")

    beg = time.perf_counter()
    decrypt(
        dstzip=Path(SITE_PACKAGES_ARCHIVE),
        src=Path(SITE_PACKAGES_CRYPT_ARCHIVE),
        pwd=SITE_PACKAGES_PASSWD,
    )
    end = time.perf_counter()
    print(f"解密耗时: {end-beg:.3f} s")

    beg = time.perf_counter()
    decompress(dstdir=Path(SITE_PACKAGES_TEMP_DIR), srczip=Path(SITE_PACKAGES_ARCHIVE))
    end = time.perf_counter()
    print(f"解压耗时: {end-beg:.3f} s")

    beg = time.perf_counter()
    convert_importer_into_cheader.convert(importer=IMPORTER, cheader=CHEADER)
    end = time.perf_counter()
    print(f"导入器转c代码耗时: {end-beg:.3f} s")
