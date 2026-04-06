"""
Generador de Licencias para iBot Trading

Genera licencias únicas para cada cliente con:
- Validación segura contra Google Apps Script endpoint
- Formatos personalizables (días, tier de características)
- Soporte para múltiples instancias
- Integración con Google Sheets

Uso:
  # Generar 5 licencias estándar
  python tools/generate_licenses.py 5

  # Generar licencia específica para cliente
  python tools/generate_licenses.py --customer "Acme Corp" --days 365 --features standard

  # Generar licencia premium para múltiples instancias
  python tools/generate_licenses.py --customer "Enterprise" --features premium --instances 5
"""

import sys
import argparse
import secrets
import hashlib
import urllib.request
import json
from datetime import datetime, timedelta


def generate_license_key(customer_name: str) -> str:
    """
    Genera una licencia única basada en:
    - Hash del nombre del cliente
    - Random token

    Formato: IBOT-XXXXXX-XXXXXX (18 caracteres)
    """
    random_part = secrets.token_hex(6).upper()
    customer_hash = hashlib.sha256(customer_name.encode()).hexdigest()[:6].upper()
    license_key = f"IBOT-{customer_hash}-{random_part}"
    return license_key


def generate_licenses(
    count: int = 5,
    customer_prefix: str = "Cliente",
    days: int = 365,
    features: str = "standard",
    max_instances: int = 1
) -> list:
    """
    Genera license keys con parámetros personalizables.

    Args:
        count: Número de licenses a generar
        customer_prefix: Prefijo para nombre del cliente
        days: Días de validez
        features: Tier (basic, standard, premium)
        max_instances: Máximo número de instancias

    Returns:
        Lista de diccionarios con datos de licencia
    """
    licenses = []
    today = datetime.now()

    for i in range(1, count + 1):
        customer_name = f"{customer_prefix} {i}"
        license_key = generate_license_key(customer_name)
        expiry_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")

        licenses.append({
            "license_key": license_key,
            "active_status": "TRUE",
            "expiry_date": expiry_date,
            "customer_name": customer_name,
            "created_date": today.strftime("%Y-%m-%d"),
            "features": features,
            "max_instances": max_instances,
        })

    return licenses


def validate_license_online(license_key: str) -> tuple:
    """Valida que una licencia existe en el endpoint."""
    try:
        endpoint = "https://script.google.com/macros/s/AKfycbwl-fdkWihZ58NT3y8SVUfQVJ9H_kYr8vrehjpYwR2t_zYSfcS-YmOBCPXVUrjKpl17/exec"

        with urllib.request.urlopen(endpoint, timeout=5) as response:
            data = response.read().decode("utf-8")

        licenses = json.loads(data)

        for lic in licenses:
            if str(lic.get("license_key")).strip() == license_key.strip():
                return True, f"Encontrada - Cliente: {lic.get('customer_name')}"

        return False, "No encontrada en Google Sheets"

    except Exception as e:
        return None, f"Error de validación: {str(e)[:50]}"


def print_csv_format(licenses: list):
    """Imprime las licencias en formato CSV para copiar a Google Sheets."""
    print("\n" + "=" * 100)
    print("COPIAR Y PEGAR EN GOOGLE SHEETS")
    print("=" * 100)
    print("\nCopia el siguiente bloque directamente en tu Google Sheet:")
    print("(Columnas: license_key | active_status | expiry_date | customer_name | created_date | features | max_instances)\n")

    for lic in licenses:
        line = (
            f"{lic['license_key']}\t"
            f"{lic['active_status']}\t"
            f"{lic['expiry_date']}\t"
            f"{lic['customer_name']}\t"
            f"{lic['created_date']}\t"
            f"{lic['features']}\t"
            f"{lic['max_instances']}"
        )
        print(line)

    print("\n" + "=" * 100)


def print_table_format(licenses: list):
    """Imprime las licencias en formato tabla."""
    print("\n" + "=" * 110)
    print("RESUMEN DE LICENCIAS GENERADAS")
    print("=" * 110)
    print()

    # Encabezado
    print(f"{'License Key':23} {'Status':8} {'Expiry':12} {'Cliente':20} {'Features':12} {'Instancias':11}")
    print("-" * 110)

    # Filas
    for lic in licenses:
        print(
            f"{lic['license_key']:23} "
            f"{lic['active_status']:8} "
            f"{lic['expiry_date']:12} "
            f"{lic['customer_name']:20} "
            f"{lic['features']:12} "
            f"{lic['max_instances']:11}"
        )

    print()


def print_installation_guide(licenses: list):
    """Imprime guía de instalación para clientes."""
    print("\n" + "=" * 100)
    print("GUIA DE INSTALACION PARA CLIENTES")
    print("=" * 100)
    print()

    for lic in licenses:
        print(f"CLIENTE: {lic['customer_name']}")
        print(f"License: {lic['license_key']}")
        print()
        print("Pasos de instalación:")
        print("  1. Descargar iBot Trading desde: [URL de descarga]")
        print("  2. Abrir config/config.ini en un editor de texto")
        print("  3. Reemplazar:")
        print(f"     LICENSE_KEY = {lic['license_key']}")
        print("  4. Agregar credenciales de MetaTrader5")
        print("  5. Ejecutar: streamlit run src/app.py")
        print()
        print("-" * 100)
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Generador de licencias para iBot Trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:

  # Generar 5 licencias estándar
  python tools/generate_licenses.py 5

  # Generar 1 licencia premium para cliente específico
  python tools/generate_licenses.py --customer "Acme Corp" --days 365 --features premium

  # Generar 3 licencias básicas para 30 días
  python tools/generate_licenses.py 3 --days 30 --features basic
        """
    )

    # Argumentos posicionales
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        default=1,
        help="Número de licencias a generar (default: 1)"
    )

    # Argumentos opcionales
    parser.add_argument(
        "--customer",
        help="Nombre del cliente (si no se especifica, usa 'Cliente N')"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Días de validez (default: 365)"
    )
    parser.add_argument(
        "--features",
        choices=["basic", "standard", "premium"],
        default="standard",
        help="Tier de características (default: standard)"
    )
    parser.add_argument(
        "--instances",
        type=int,
        default=1,
        help="Máximo número de instancias (default: 1)"
    )

    args = parser.parse_args()

    # Generar
    if args.customer:
        # Si especifica cliente, generar solo 1
        licenses = generate_licenses(
            count=1,
            customer_prefix=args.customer,
            days=args.days,
            features=args.features,
            max_instances=args.instances
        )
        print(f"\nGenerando licencia para: {args.customer}")
    else:
        # Si no, generar múltiples
        licenses = generate_licenses(
            count=args.count,
            days=args.days,
            features=args.features,
            max_instances=args.instances
        )
        print(f"\nGenerando {args.count} licencias...")

    # Mostrar en tabla
    print_table_format(licenses)

    # Mostrar en CSV para copiar a Google Sheets
    print_csv_format(licenses)

    # Mostrar guía de instalación
    print_installation_guide(licenses)

    # Instrucciones finales
    print("\n" + "=" * 100)
    print("PASOS FINALES")
    print("=" * 100)
    print()
    print("1. Abre Google Sheets (PRIVADA):")
    print("   https://docs.google.com/spreadsheets/d/18XG3FveuWFjC7cfDmQCWmN47gScD_rLOs47OcdQ6G7E/edit")
    print()
    print("2. Haz clic en una celda vacía (ej: A2)")
    print()
    print("3. Pega (Ctrl+V) el bloque CSV anterior")
    print()
    print("4. Guarda")
    print()
    print("5. Las licencias estarán activas en 1-2 minutos")
    print()
    print("6. Distribuir a clientes las instrucciones de instalación anterior")
    print()
    print("=" * 100)
    print()


if __name__ == '__main__':
    main()
