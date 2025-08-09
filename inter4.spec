# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# ============== CONFIGURAÇÕES PERSONALIZÁVEIS ==============
APP_NAME = "PhotoResizer by Hélio Tomé"
ICONE_PATH = "shark.ico"
SCRIPT_MAIN = "inter4.py"
# ===========================================================

a = Analysis(
    [SCRIPT_MAIN],
    pathex=[],
    binaries=[],
    datas=[
        ('shark.png', '.'),       # Formato CORRETO: (arquivo_origem, pasta_destino)
        #=====('background.jpg', '.')  # Cada arquivo em uma tupla separada===
    ],
    hiddenimports=['PIL', 'PyQt5'],  # Dependências comuns para PyQt5
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)