import sys
import os

# 1. Definimos la raíz del proyecto de forma absoluta
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Agregamos SOLAMENTE src y core al path (config NO debe estar aquí)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# 3. Importamos la aplicación desde la carpeta src
# Esto obliga a Python a buscar dentro de src/app.py
try:
    from src.app import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error de importación: {e}")
    print("Asegúrate de que existan los archivos __init__.py en src/ y core/")