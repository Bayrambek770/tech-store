import polib, pathlib

base = pathlib.Path(__file__).resolve().parents[1] / 'locale'
for lang in ['ru','uz']:
    po_path = base / lang / 'LC_MESSAGES' / 'django.po'
    mo_path = base / lang / 'LC_MESSAGES' / 'django.mo'
    if not po_path.exists():
        print(f'Skip {lang}, no po file')
        continue
    po = polib.pofile(str(po_path))
    po.save_as_mofile(str(mo_path))
    print(f'Compiled {po_path} -> {mo_path} ({len(po)} entries)')
print('Done.')
