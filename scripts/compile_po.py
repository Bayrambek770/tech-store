import polib, pathlib

base = pathlib.Path(__file__).resolve().parents[1] / 'locale'
for lang in ['ru','uz','en']:
    po_path = base / lang / 'LC_MESSAGES' / 'django.po'
    mo_path = base / lang / 'LC_MESSAGES' / 'django.mo'
    if not po_path.exists():
        print(f'Skip {lang}, no po file')
        continue
    try:
        po = polib.pofile(str(po_path))
        # Optionally remove fuzzy entries for reliability
        removed = 0
        for entry in list(po):
            if 'fuzzy' in entry.flags:
                entry.flags.remove('fuzzy')
        po.save_as_mofile(str(mo_path))
        print(f'Compiled {po_path} -> {mo_path} ({len(po)} entries)')
    except Exception as e:
        print(f'Failed to compile {po_path}: {e}')
print('Done.')
