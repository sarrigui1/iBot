#!/usr/bin/env python
"""Verificación de imports - Simula la ejecución desde streamlit run src/app.py"""
import sys
import os

# Simular lo que streamlit hace
root_dir = os.getcwd()
src_dir = os.path.join(root_dir, 'src')

# Agregar directorios a sys.path (como lo hace Streamlit)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

print("=" * 70)
print("VERIFICACION DE IMPORTS (simulando streamlit run src/app.py)")
print("=" * 70)
print(f"Root dir: {root_dir}")
print(f"src.path[0]: {sys.path[0]}")
print(f"sys.path[1]: {sys.path[1]}")
print()

# Test de imports
tests = [
    ("i18n", "from i18n import get_translations"),
    ("core.config_loader", "from core.config_loader import ConfigLoader"),
    ("core.license_manager", "from core.license_manager import LicenseManager"),
    ("mt5_service", "from mt5_service import MT5Service"),
    ("indicators_service", "from indicators_service import IndicatorsService"),
    ("anthropic_service", "from anthropic_service import AnthropicService"),
    ("smc_service", "from smc_service import SMCService"),
    ("risk_manager", "from risk_manager import RiskManager"),
    ("ui_components", "from ui_components import render_metrics"),
    ("logger_service", "from logger_service import LoggerService"),
    ("feedback_service", "from feedback_service import FeedbackService"),
    ("news_service", "from news_service import NewsService"),
    ("config", "from config import SYMBOLS, AUTONOMOUS_CONFIDENCE_THRESHOLD"),
]

passed = 0
failed = 0

for mod_name, stmt in tests:
    try:
        exec(stmt)
        print(f"[OK] {mod_name:35} SUCCESS")
        passed += 1
    except ModuleNotFoundError as e:
        print(f"[FAIL] {mod_name:35} NOT FOUND: {str(e)[:40]}")
        failed += 1
    except ImportError as e:
        print(f"[FAIL] {mod_name:35} IMPORT ERROR: {str(e)[:40]}")
        failed += 1
    except Exception as e:
        print(f"[ERROR] {mod_name:35} {type(e).__name__}: {str(e)[:30]}")
        failed += 1

print()
print("=" * 70)
print(f"RESULTADO: {passed} OK, {failed} FAILED")
print("=" * 70)

sys.exit(0 if failed == 0 else 1)
