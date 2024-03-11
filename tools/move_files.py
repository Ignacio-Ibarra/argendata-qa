"""
Necesita:
    - subtop_files/: Directorio con los archivos .csv descargados de Google Drive.

Este script mueve los archivos .csv de subtop_files/ a SUBTOP/SUBTOP_gX/data/SUBTOP_gX.csv, creando los directorios necesarios.
"""

import argparse
import re
import os

def main(subtopico: str):
    folder = subtopico.lower() + '_files'
    
    if os.path.exists(folder) and os.path.isdir(folder):
        folder = os.path.abspath(folder)
        print(f"Directorio {folder} OK.")
    else:
        print(f"Directorio {folder} no existe.")
        exit(1)

    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    print(f"Encontrados {len(files)} archivos .csv en {folder}.")

    for file in files:
        nombre_limpio = os.path.splitext(file)[0]
        target_directory = f'./{subtopico}/{nombre_limpio}/data/{nombre_limpio}.csv'
        os.makedirs(os.path.dirname(target_directory), exist_ok=True)
        os.rename(f'{folder}/{file}', target_directory)
        print(f"Archivo {file} movido a {target_directory}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('subtopico', type=str, nargs='?', help='Subtopico valido')
    args = parser.parse_args()

    subtopico = args.subtopico

    if subtopico is None:
        parser.error("Argumento vacio, por favor ingresar un subtopico valido.")
    else:
        if not re.match("^[A-Z]{6}$", subtopico):
            parser.error("Subtopico invalido.")
        else:
            main(subtopico)     