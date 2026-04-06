"""
iBot Enterprise - Application Entry Point

Este archivo es el punto de entrada para Streamlit.
Agrega los directorios src/ y core/ al path y luego ejecuta la app.

Uso: streamlit run app_main.py
"""

import sys
import os

# Agregar src/ y core/ al path de Python para que los imports funcionen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

# Ahora importar y ejecutar la app desde src/
from src.app import *  # noqa: F401, F403
