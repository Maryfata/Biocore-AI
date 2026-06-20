#!/usr/bin/env python
import py_compile
import sys

files = [
    'app/supermodules/home/pages.py',
    'app/supermodules/ecg_monitor/pages.py',
    'app/supermodules/academia_inteligente/pages.py',
    'app/supermodules/digital_twin_profesional/pages.py',
    'app/supermodules/specialties/pages.py'
]

errors = 0
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f'✅ {f}')
    except Exception as e:
        print(f'❌ {f}: {e}')
        errors += 1

sys.exit(errors)
