# -*- mode: python ; coding: utf-8 -*-

import os
import runpy

__version__ = runpy.run_path(os.path.join(SPECPATH, 'version.py'))['__version__']

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icons', 'icons'), ('config.json', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SpacePP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SpacePP',
)
app = BUNDLE(
    coll,
    name='SpacePP.app',
    icon='icons/SpacePP.icns',
    bundle_identifier='com.local.spacepp',
    info_plist={
        'CFBundleShortVersionString': __version__,
        'CFBundleVersion': __version__,
    },
)
