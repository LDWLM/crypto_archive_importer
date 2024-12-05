# %%
import hashlib
import json
import shutil
from typing import List
import time
from pathlib import Path
from zipfile import ZipFile

import archive

BASEDIR = Path(__file__).parent.absolute()
TEMPDIR = BASEDIR / "temp"

PDF2DOCXAPP = "/home/atlas/PDF2Word_libs/Pdf2DocxApp"
ASSETS_DIR = f"{PDF2DOCXAPP}/libpdf2docx/src/main/assets"
PYTHON_ARCHIVES_DIR = (TEMPDIR / "outputs").as_posix()
ARCHES = {"arm64-v8a", "armeabi-v7a"}
SONAMES = {"libconvert.so", "libpreloader.so"}


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
    apk = (
        pdf2docxapp
        / "app"
        / "build"
        / "outputs"
        / "apk"
        / "release"
        / "app-release.apk"
    )
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
            return [file for file in files if file != "python"]

        def copy_function(src: str, dst: str):
            digest = md5sum(src)
            rel = Path(src).relative_to(assets / "python").as_posix()
            checksums[rel] = digest
            return shutil.copy2(src, dst)

        # copy python tree
        shutil.copytree(
            src=assets,
            dst=archivebase,
            ignore=ignore,
            copy_function=copy_function,
            dirs_exist_ok=True
        )

        def ignore(d: str, files: List[str]) -> List[str]:
            if not assets.samefile(d):
                return []
            return [file for file in files if file != arch]

        def copy_function(src: str, dst: str):
            digest = md5sum(src)
            rel = Path(src).relative_to(assets).as_posix()
            checksums[rel] = digest
            return shutil.copy2(src, dst)

        # copy libs into python root
        shutil.copytree(
            src=assets,
            dst=archivebase / "python",
            ignore=ignore,
            copy_function=copy_function,
            dirs_exist_ok=True
        )
        archive.compress(dstzip=archivebase / "python.zip", srcdir=archivebase / "python", with_root=True)
        shutil.rmtree(archivebase / "python")

        with open(dstchecksum, "w") as o:
            json.dump(checksums, o, indent=2)


def export_convert_core(pdf2docxapp: Path, output_dir: Path):
    convert_core_path = pdf2docxapp / 'libpdf2docx/src/main/java/androidx/appcompat/libconvert/ConvertCore.java'
    shutil.copy2(convert_core_path, output_dir)
    print(f'exported {convert_core_path} -> {output_dir}')

def export_readme(pdf2docxapp: Path, output_dir: Path):
    readme_path = pdf2docxapp / 'libpdf2docx/README.md'
    shutil.copy2(readme_path, output_dir)
    print(f'exported {readme_path} -> {output_dir}')


# %%
if __name__ == "__main__":
    shutil.rmtree(TEMPDIR, ignore_errors=True)
    TEMPDIR.mkdir(exist_ok=True)

    beg = time.perf_counter()
    update_libconvert(Path(PDF2DOCXAPP), Path(ASSETS_DIR))
    end = time.perf_counter()
    print(f"更新libconvert耗时: {end-beg:.3f} s")

    beg = time.perf_counter()
    archive_python(Path(PYTHON_ARCHIVES_DIR), Path(ASSETS_DIR))
    end = time.perf_counter()
    print(f"压缩python耗时: {end-beg:.3f} s")

    export_convert_core(Path(PDF2DOCXAPP), Path(PYTHON_ARCHIVES_DIR))
    export_readme(Path(PDF2DOCXAPP), Path(PYTHON_ARCHIVES_DIR))
