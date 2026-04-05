"""
Generador de License Keys para iBot

Genera claves de licencia en formato: IBOT-YYYY-NNN

Uso:
  python generate_licenses.py 5

Genera 5 license keys para copiar manualmente a Google Sheets.
"""

import sys
from datetime import datetime, timedelta


def generate_licenses(count: int = 5) -> list:
    """
    Genera license keys en formato IBOT-YYYY-NNN.

    Args:
        count: Número de licenses a generar

    Returns:
        Lista de diccionarios con license_key y datos asociados
    """
    year = datetime.now().year
    licenses = []

    for i in range(1, count + 1):
        license_key = f"IBOT-{year}-{i:03d}"
        expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        licenses.append({
            "license_key": license_key,
            "active_status": "TRUE",
            "expiry_date": expiry_date,
            "customer_name": f"Cliente {i}",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
        })

    return licenses


def print_csv_format(licenses: list):
    """Imprime las licencias en formato CSV para copiar a Google Sheets."""
    print("\n" + "=" * 80)
    print("COPIAR Y PEGAR EN GOOGLE SHEETS")
    print("=" * 80)
    print("\nCopyea el siguiente bloque directamente en tu Google Sheet:")
    print("(Columnas: A=license_key, B=active_status, C=expiry_date, D=customer_name, E=created_date)\n")

    for lic in licenses:
        line = (
            f"{lic['license_key']}\t"
            f"{lic['active_status']}\t"
            f"{lic['expiry_date']}\t"
            f"{lic['customer_name']}\t"
            f"{lic['created_date']}"
        )
        print(line)

    print("\n" + "=" * 80)


def print_table_format(licenses: list):
    """Imprime las licencias en formato tabla."""
    print("\n" + "=" * 80)
    print("RESUMEN DE LICENSES GENERADAS")
    print("=" * 80)
    print()

    # Encabezado
    print(f"{'License Key':20} {'Status':10} {'Expiry':12} {'Customer':25} {'Created':12}")
    print("-" * 80)

    # Filas
    for lic in licenses:
        print(
            f"{lic['license_key']:20} "
            f"{lic['active_status']:10} "
            f"{lic['expiry_date']:12} "
            f"{lic['customer_name']:25} "
            f"{lic['created_date']:12}"
        )

    print()


def main():
    # Leer argumento: cantidad de licenses a generar
    count = 5  # default
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print(f"ERROR: '{sys.argv[1]}' no es un numero")
            sys.exit(1)

    # Generar
    print(f"\nGenerando {count} license keys...")
    licenses = generate_licenses(count)

    # Mostrar en tabla
    print_table_format(licenses)

    # Mostrar en CSV para copiar a Google Sheets
    print_csv_format(licenses)

    print("\nINSTRUCCIONES:")
    print("1. Abre: https://docs.google.com/spreadsheets/d/18XG3FveuWFjC7cfDmQCWmN47gScD_rLOs47OcdQ6G7E/edit")
    print("2. Haz clic en la celda A2 (primera fila vacia)")
    print("3. Pega (Ctrl+V) el bloque anterior")
    print("4. LISTO! Las licencias estan activas")
    print("\n")


if __name__ == '__main__':
    main()
