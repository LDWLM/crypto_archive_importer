IMPORTER = 'site-packages/secretzipimport.py'
CHEADER = '/home/atlas/PDF2Word_libs/Pdf2DocxApp/libpdf2docx/src/main/cpp/importer.h'

with open(IMPORTER, 'r') as sfile, open(CHEADER, 'w') as dfile:
    dfile.write(f'#ifndef CONVERT_IMPORTER_INTO_CHEADER\n')
    dfile.write(f'#define CONVERT_IMPORTER_INTO_CHEADER\n')
    dfile.write('\n')
    dfile.write('const char IMPORTER[] = {\n')
    for line in sfile:
        dfile.write('    ')
        for char in line:
            if char == '\n':
                dfile.write("'\\n',")
            elif char == '\\':
                dfile.write("'\\\\',")
            elif char == '\'':
                dfile.write("'\\'',")
            else:
                dfile.write(f"'{char}',")
        dfile.write('\n')
    dfile.write('    0,\n')
    dfile.write('};\n')
    dfile.write('\n')
    dfile.write(f'#endif /* CONVERT_IMPORTER_INTO_CHEADER */\n')
