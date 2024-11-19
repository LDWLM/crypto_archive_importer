import hashlib
import json
import shutil
from typing import List
import convert_importer_into_cheader, sys, time
from pathlib import Path

sys.path.append("./site-packages")
sys.path.append("./site-packages/libs")

# %%
from importer import ZipFile, ZIP_DEFLATED, CryptoZipFile

BASEDIR = Path(__file__).parent.absolute()
TEMPDIR = BASEDIR / "temp"
TEMPDIR.mkdir(exist_ok=True)

PYTHON_DIR = "/home/atlas/PDF2Word_libs/Pdf2DocxApp/libpdf2docx/src/main/assets/python"
CHEADER = "/home/atlas/PDF2Word_libs/Pdf2DocxApp/libpdf2docx/src/main/cpp/importer.h"
SITE_PACKAGES_DIR = "/home/atlas/PDF2Word_libs/Pdf2DocxApp/libpdf2docx/src/main/python/lib/python3.8/site-packages"
SITE_PACKAGES_CRYPT_ARCHIVE = "/home/atlas/PDF2Word_libs/Pdf2DocxApp/libpdf2docx/src/main/assets/python/lib/python3.8/site-packages/_pdf2docx.so"
SITE_PACKAGES_ARCHIVE = (TEMPDIR / "site-packages.zip").as_posix()
SITE_PACKAGES_TEMP_DIR = (TEMPDIR / "site-packages").as_posix()
IMPORTER = (BASEDIR / "importer.py").as_posix()
SITE_PACKAGES_PASSWD = b"atlas"
PYTHON_ARCHIVES_DIR = (TEMPDIR / "outputs").as_posix()
ARCHES = {"arm64-v8a", "armeabi-v7a", "x86_64"}


# %%
# 压缩
def compress(dstzip: Path, srcdir: Path):
    dstzip.parent.mkdir(exist_ok=True)
    with ZipFile(dstzip.as_posix(), mode="w", compression=ZIP_DEFLATED) as zip:
        for file in srcdir.rglob("*"):
            if not file.is_file():
                continue
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


def md5sum(path):
    hash = hashlib.md5()
    with open(path, "rb") as file:
        hash.update(file.read())
    return hash.hexdigest()


def archive_python(dstdir: Path, srcpydir: Path):
    if (srcpydir / "python").exists():
        srcpydir /= "python"

    assert srcpydir.exists() and (srcpydir / "lib").exists()

    dstdir.mkdir(exist_ok=True)
    for arch in ARCHES:
        archpath = srcpydir / arch
        if not archpath.exists():
            continue

        archivebase = dstdir / f"python-{arch}"
        dstzip = dstdir / f"python-{arch}.zip"
        dstchecksum = dstdir / f"checksum-{arch}.json"

        checksums = {}

        print(f" 正在生成{dstzip.name}和{dstchecksum.name}")

        def ignore(d: str, files: List[str]) -> List[str]:
            if not srcpydir.samefile(d):
                return []
            return [file for file in files if file != arch and file != "lib"]

        def copy_function(src: str, dst: str):
            digest = md5sum(src)
            rel = Path(src).relative_to(srcpydir).as_posix()
            checksums[rel] = digest
            return shutil.copy2(src, dst)

        shutil.copytree(
            src=srcpydir,
            dst=archivebase,
            ignore=ignore,
            copy_function=copy_function,
            dirs_exist_ok=True,
        )

        compress(dstzip=dstzip, srcdir=archivebase)

        with open(dstchecksum, "w") as o:
            json.dump(checksums, o, indent=2)


# %%

if __name__ == "__main__":
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

    beg = time.perf_counter()
    archive_python(Path(PYTHON_ARCHIVES_DIR), Path(PYTHON_DIR))
    end = time.perf_counter()
    print(f"压缩python耗时: {end-beg:.3f} s")
