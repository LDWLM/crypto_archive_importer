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

PDF2DOCXAPP = "/home/atlas/PDF2Word_libs/Pdf2DocxApp"
ASSETS_DIR = f"{PDF2DOCXAPP}/libpdf2docx/src/main/assets"
CHEADER = f"{PDF2DOCXAPP}/libpdf2docx/src/main/cpp/importer.h"
SITE_PACKAGES_DIR = (
    f"{PDF2DOCXAPP}/libpdf2docx/src/main/python/lib/python3.8/site-packages"
)
SITE_PACKAGES_CRYPT_ARCHIVE = f"{PDF2DOCXAPP}/libpdf2docx/src/main/assets/python/lib/python3.8/site-packages/libalgorithms.so"
SITE_PACKAGES_ARCHIVE = (TEMPDIR / "site-packages.zip").as_posix()
SITE_PACKAGES_TEMP_DIR = (TEMPDIR / "site-packages").as_posix()
IMPORTER = (BASEDIR / "importer.py").as_posix()
SITE_PACKAGES_PASSWD = b"atlas"
PYTHON_ARCHIVES_DIR = (TEMPDIR / "outputs").as_posix()
ARCHES = {"arm64-v8a", "armeabi-v7a", "x86_64"}
SONAMES = {"libconvert.so", "libpreloader.so"}


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


def update_libconvert(pdf2docxapp: Path, assets: Path):
    import os, subprocess

    print(f" cleaning {pdf2docxapp}")
    env = os.environ.copy()
    env["JAVA_HOME"] = "/opt/android-studio/jbr"
    subprocess.run(
        args=f"./gradlew clean",
        cwd=pdf2docxapp,
        env=env,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
        check=True,
    )
    print(f" building {pdf2docxapp}")
    subprocess.run(
        args=f"./gradlew assembleRelease",
        cwd=pdf2docxapp,
        env=env,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
        check=True,
    )
    apk = pdf2docxapp / "app" / "build" / "outputs" / "apk" / "release" / "app-release.apk"
    extracted_apk_dir = TEMPDIR / apk.name
    print(f" extracting apk {apk}")
    with ZipFile(apk) as f:
        names = f.namelist()
        for arch in ARCHES:
            for soname in SONAMES:
                relname = f"lib/{arch}/{soname}"
                pyso = assets / arch / soname
                if relname not in names:
                    print(f"ignore {relname}")
                    continue
                f.extract(member=relname, path=extracted_apk_dir)
                extracted_so = extracted_apk_dir / relname
                print(f" extracted {relname} -> {extracted_so}")
                shutil.copy2(extracted_so, pyso)
                print(f" move {extracted_so} -> {pyso}")


def archive_python(dstdir: Path, assets: Path):
    assert assets.exists() and (assets / "python").exists()

    shutil.rmtree(dstdir, ignore_errors=True)
    dstdir.mkdir(exist_ok=True)
    for arch in ARCHES:
        archpath = assets / arch
        if not archpath.exists():
            continue

        archivebase = dstdir / f"python-{arch}"
        dstzip = dstdir / f"python-{arch}.zip"
        dstchecksum = dstdir / f"checksum-{arch}.json"

        checksums = {}

        print(f" 正在生成{dstzip.name}和{dstchecksum.name}")

        def ignore(d: str, files: List[str]) -> List[str]:
            if not assets.samefile(d):
                return []
            return [file for file in files if file != arch and file != "python"]

        def copy_function(src: str, dst: str):
            digest = md5sum(src)
            rel = Path(src).relative_to(assets).as_posix()
            checksums[rel] = digest
            return shutil.copy2(src, dst)

        shutil.copytree(
            src=assets,
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
    update_libconvert(Path(PDF2DOCXAPP), Path(ASSETS_DIR))
    end = time.perf_counter()
    print(f"更新libconvert耗时: {end-beg:.3f} s")

    beg = time.perf_counter()
    archive_python(Path(PYTHON_ARCHIVES_DIR), Path(ASSETS_DIR))
    end = time.perf_counter()
    print(f"压缩python耗时: {end-beg:.3f} s")
