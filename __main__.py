# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['__main__.py'],
    pathex=['/usr/local/lib/python3.7/dist-packages','/opt/AutoshopRefactor','/opt/AutoshopRefactor/TpvYsolveMqtt','/opt/AutoshopRefactor/Model/TPVCommunication/Request/Request','/opt/AutoshopRefactor/Model/TPVCommunication/Request/PayRequest','/opt/AutoshopRefactor/Model/TPVCommunication/Request/CancelRequest','/opt/AutoshopRefactor/Model/TPVCommunication/Request/ConfigStackRequest','/opt/AutoshopRefactor/Controller/RequestController','/opt/AutoshopRefactor/Router/RouterRequest','/opt/AutoshopRefactor/*'],
    binaries=[],
    datas=[],
    hiddenimports=[],
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='options',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='options',
)


