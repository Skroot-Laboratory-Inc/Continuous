# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
app_name = "SkrootReadersFoaming"


a = Analysis(
    ['../main_foaming.py'],
    pathex=[],
    binaries=[],
    datas=[('../algorithms.py', '.'), ('../analysis.py', '.'), ('../aws.py', '.'), ('../buttons.py', '.'), ('../colors.py', '.'), ('../dac.py', '.'), ('../dev.py', '.'), ('../emailer.py', '.'), ('../exceptions.py', '.'), ('../guided_setup.py', '.'), ('../indicator.py', '.'), ('../initialization.py', '.'), ('../logger.py', '.'), ('../main_foaming.py', '.'), ('../main_shared.py', '.'), ('../notes.py', '.'), ('../pdf.py', '.'), ('../plotting.py', '.'), ('../readers.py', '.'), ('../server.py', '.'), ('../settings.py', '.'), ('../setup.py', '.'), ('../text_notification.py', '.'), ('../timer.py', '.'), ('../vna.py', '.')],
    hiddenimports=['sklearn.utils._weight_vector'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
splash = Splash(
    'logoRectangle.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=False,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash,
    splash.binaries,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Logo.ico'],
)
