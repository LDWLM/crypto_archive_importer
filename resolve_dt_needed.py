# %%
from elftools.elf.elffile import ELFFile
from elftools.elf.dynamic import DynamicSection
from pathlib import Path
import os

PATCH_LIBS = {
    "libjpeg_chaquopy.so": "libjpeg.so",
}


def patchelf_libs(dir):
    for so in list(Path(dir).iterdir()):
        # if should patch soname
        if so.name in PATCH_LIBS:
            dstso = PATCH_LIBS[so.name]

            # patchelf --set-soname {dstso} {so}
            cmd = f"patchelf --set-soname {dstso} {so}"
            print(f" {cmd}")
            assert os.system(cmd) == 0

            # # replace os.system with ELFFile
            # with open(so, 'rb') as f:
            #     elf = ELFFile(f)

            # mv {so} {dir/dstso}
            newso = dir / dstso
            cmd = f"mv {so} {newso}"
            print(f" {cmd}")
            assert os.system(cmd) == 0

            so = newso

        # if should patch needed
        for srcso, dstso in PATCH_LIBS.items():
            neededs = get_needed_libraries(so)
            if srcso in neededs:
                # patchelf --replace-needed {srcso} {dstso} {so}
                cmd = f"patchelf --replace-needed {srcso} {dstso} {so}"
                print(f" {cmd}")
                assert os.system(cmd) == 0


def get_needed_libraries(so_file):
    with open(so_file, "rb") as f:
        elf = ELFFile(f)

        needed_libraries = []

        # 遍历动态段中的所有条目
        for section in elf.iter_sections():
            if isinstance(section, DynamicSection):
                for tag in section.iter_tags():
                    if tag.entry.d_tag == "DT_NEEDED":
                        needed_libraries.append(tag.needed)

        return needed_libraries
