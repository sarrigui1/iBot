# -*- mode: python ; coding: utf-8 -*-
"""
Build specification for PyInstaller.

Genera un ejecutable Windows independiente que incluye:
- Código Python compilado
- Todas las dependencias
- archivos de datos (config.ini, data/, etc.)

Uso:
  pyinstaller build_exe.spec
"""

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.ini', '.'),
        ('README.txt', '.'),
        ('data/', 'data/'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.logger',
        'streamlit.web.server',
        'MetaTrader5',
        'anthropic',
        'gspread',
        'google.auth',
        'google.auth.transport.requests',
        'pandas_ta',
        'pandas',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=['pytest', 'unittest'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ibot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
