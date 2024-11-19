from pathlib import Path

IMPORTER = "site-packages/importer.py"
CHEADER = "/home/atlas/PDF2Word_libs/Pdf2DocxApp/libpdf2docx/src/main/cpp/importer.h"


def convert(importer: Path, cheader: Path):
    with open(importer, "r") as sfile, open(cheader, "w") as dfile:
        dfile.write(f"#ifndef CONVERT_IMPORTER_INTO_CHEADER\n")
        dfile.write(f"#define CONVERT_IMPORTER_INTO_CHEADER\n")
        dfile.write("\n")
        dfile.write("const char IMPORTER[] = {\n")
        for line in sfile:
            dfile.write("    ")
            for char in line:
                if char == "\n":
                    dfile.write("'\\n',")
                elif char == "\\":
                    dfile.write("'\\\\',")
                elif char == "'":
                    dfile.write("'\\'',")
                else:
                    dfile.write(f"'{char}',")
            dfile.write("\n")
        dfile.write("    0,\n")
        dfile.write("};\n")
        dfile.write("\n")
        dfile.write(f"#endif /* CONVERT_IMPORTER_INTO_CHEADER */\n")


if __name__ == "__main__":
    convert(Path(IMPORTER), Path(CHEADER))
