import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

print("=" * 70)
print("VERIFICACION DE IMPORTS")
print("=" * 70)
print("ROOT_DIR: " + ROOT_DIR)
print("sys.path[0]: " + sys.path[0])
print()

# List actual files
print("ARCHIVOS ENCONTRADOS:")
print("\nENsrc/:")
for f in os.listdir(os.path.join(ROOT_DIR, 'src')):
    if f.endswith('.py'):
        print("  - " + f)

print("\nEN core/:")
for f in os.listdir(os.path.join(ROOT_DIR, 'core')):
    if f.endswith('.py'):
        print("  - " + f)

print("\nEN raiz/:")
for f in os.listdir(ROOT_DIR):
    if f.endswith('.py') and os.path.isfile(os.path.join(ROOT_DIR, f)):
        print("  - " + f)

# Test imports
print("\n" + "=" * 70)
print("PRUEBA DE IMPORTS (como se ejecutaria desde src/app.py):")
print("=" * 70)

tests = [
    ("i18n", "from i18n"),
    ("core.config_loader", "from core.config_loader"),
    ("core.mt5_service", "from core.mt5_service"),
    ("indicators_service", "from indicators_service"),
    ("config", "from config"),
]

for mod_path, stmt in tests:
    file_check = ""
    if "core." in mod_path:
        fname = mod_path.split(".")[1] + ".py"
        fpath = os.path.join(ROOT_DIR, "core", fname)
        file_check = " (EXISTS)" if os.path.exists(fpath) else " (NOT FOUND)"
    elif "." not in mod_path:
        fpath = os.path.join(ROOT_DIR, "src", mod_path + ".py")
        file_check = " (EXISTS)" if os.path.exists(fpath) else " (NOT FOUND)"
    else:
        fpath = os.path.join(ROOT_DIR, mod_path.replace(".", os.sep) + ".py")
        file_check = " (EXISTS)" if os.path.exists(fpath) else " (NOT FOUND)"
    
    print("[TEST] " + mod_path.ljust(30) + file_check)

