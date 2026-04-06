"""
Build Simple Installer - Empaqueta TODOS los archivos necesarios
Uso: python build_simple_installer.py

Genera: dist/iBot_Enterprise_Setup_COMPLETO.exe
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, desc):
    """Ejecuta comando y reporta"""
    print(f"\n{'='*70}")
    print(f"[{desc}]")
    print(f"{'='*70}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"\n❌ ERROR en: {desc}")
        sys.exit(1)
    print(f"✅ {desc} completado")

def main():
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("\n" + "="*70)
    print("[BUILD] INSTALADOR COMPLETO")
    print("="*70)

    # PASO 1: Limpiar builds previos
    print("\n[1/5] Limpiando builds previos...")
    for dirname in ['build', 'dist']:
        if os.path.exists(dirname):
            print(f"  Eliminando {dirname}/...")
            shutil.rmtree(dirname)

    # PASO 2: Crear carpeta para empacar
    print("\n[2/5] Preparando archivos para empacar...")

    package_dir = Path("_package_temp")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()

    # Copiar TODOS los archivos necesarios
    dirs_to_copy = ['src', 'core', 'config', 'data', 'docs']
    files_to_copy = ['app_main.py']

    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            dst = package_dir / dir_name
            print(f"  Copiando {dir_name}/...")
            shutil.copytree(dir_name, dst)

    for file_name in files_to_copy:
        if os.path.exists(file_name):
            print(f"  Copiando {file_name}...")
            shutil.copy(file_name, package_dir / file_name)

    # Copiar installer.py modificado para instalar completo
    print(f"  Copiando installer.py...")
    shutil.copy("tools/installer.py", package_dir / "installer.py")

    print("✅ Archivos preparados")

    # PASO 3: Crear spec para PyInstaller
    print("\n[3/5] Creando configuración PyInstaller...")

    spec_content = """# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app_main.py', '.'),
        ('src', 'src'),
        ('core', 'core'),
        ('config', 'config'),
        ('data', 'data'),
        ('docs', 'docs'),
    ],
    hiddenimports=['win32com.client'],
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
    a.binaries,
    a.datas,
    [],
    name='iBot_Enterprise_Setup_COMPLETO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    spec_path = package_dir / "build_temp.spec"
    with open(spec_path, 'w') as f:
        f.write(spec_content)

    print(f"✅ Especificación creada")

    # PASO 4: Compilar con PyInstaller
    print("\n[4/5] Compilando instalador...")

    os.chdir(package_dir)

    cmd = (
        f'pyinstaller build_temp.spec '
        f'--distpath ../dist '
        f'--specpath ../build '
        f'--buildpath ../build/work '
        f'--clean'
    )

    run_cmd(cmd, "PyInstaller")

    os.chdir(project_root)

    # PASO 5: Renombrar y verificar
    print("\n[5/5] Finalizando...")

    src_exe = Path("dist/iBot_Enterprise_Setup_COMPLETO.exe")

    if src_exe.exists():
        size_mb = src_exe.stat().st_size / (1024 * 1024)
        print(f"✅ Instalador creado: {size_mb:.1f} MB")
        print(f"   Ubicación: {src_exe.absolute()}")
    else:
        print("❌ ERROR: Instalador no se creó")
        sys.exit(1)

    # Limpiar temporales
    print("\n[LIMPIEZA] Eliminando archivos temporales...")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    print("✅ Limpieza completada")

    # Resumen final
    print("\n" + "="*70)
    print("[OK] BUILD COMPLETADO EXITOSAMENTE")
    print("="*70)
    print(f"\n[ARCHIVO] Instalador disponible en:")
    print(f"   dist/iBot_Enterprise_Setup_COMPLETO.exe ({size_mb:.1f} MB)")
    print(f"\n[CONTENIDO] El instalador incluye:")
    print(f"   [OK] Codigo fuente (src/, core/)")
    print(f"   [OK] Configuracion (config/)")
    print(f"   [OK] Datos (data/)")
    print(f"   [OK] Documentacion (docs/)")
    print(f"   [OK] app_main.py")
    print(f"   [OK] installer.py")
    print(f"\n[DISTRIBUCION] Para distribuir:")
    print(f"   1. Envia: dist/iBot_Enterprise_Setup_COMPLETO.exe")
    print(f"   2. Cliente ejecuta el .exe")
    print(f"   3. Listo para usar!")
    print(f"\n[TAMAÑO] Ocupara aproximadamente: ~{size_mb:.0f} MB despues de instalar")

if __name__ == '__main__':
    main()
