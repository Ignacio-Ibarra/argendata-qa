from data_transformers.utils import callstack_to_program, callstack_to_str
from os import rename, makedirs
import urllib.request
import pandas as pd
import shutil
import re
import os

def gsheet_download(id: str, 
                    target: str,
                    format: str, 
                    url_template="https://docs.google.com/spreadsheets/d/{id}/export?format={format}"):
    url = url_template.format(id=id, format=format)
    return urllib.request.urlretrieve(url, target)


def gsheet_download_csv(id: str, 
                        target: str):
    return gsheet_download(id=id, target=target, format="csv")

def gsheet_download_xlsx(id: str, 
                        target: str):
    return gsheet_download(id=id, target=target, format="xlsx")

def match_relocate(src, target, pattern, file_list=None):
    files_to_move = file_list or os.listdir(src)

    pattern = re.compile(pattern)

    if not os.path.exists(target):
        makedirs(target)

    for filename in files_to_move:
        if pattern.match(filename):
            src_path = os.path.join(src, filename)
            dest_path = os.path.join(target, filename)

            shutil.move(src_path, dest_path)

    print(f"Files matching the pattern '{pattern}' moved to '{target}'.")

GEONOMENCLADOR_ID = "1744VS5xENUg1JRCaKr1dGUr73jgP-wz27guIhHvYGbQ"

def get_geonomenclador():
    gsheet_download_csv(GEONOMENCLADOR_ID, "geonomenclador.csv")
    return pd.read_csv("geonomenclador.csv")

def exportar_definitivo(archivo: str, folder:str, df: pd.DataFrame, nuevo_nombre=None):
    if not nuevo_nombre:
        nuevo_nombre = f"{folder}/definitivos/{archivo}_old.csv"

    original_file = f'{folder}/definitivos/{archivo}.csv'

    rename(original_file, nuevo_nombre)

    df.to_csv(original_file, 
              encoding='utf-8', 
              sep=',', 
              quoting=1, # csv.QUOTE_ALL
              quotechar='"', 
              lineterminator='\n', 
              decimal='.', 
              index=False)
    
    return original_file, nuevo_nombre

def exportar_transformador(grafico_id, pipeline, callstack):
    imports = 'from pandas import DataFrame\nfrom data_transformers import chain, transformer\n\n'
    definitions = '\n'.join(pipeline.transformers_source())
    chain_prog = callstack_to_program(callstack)
    chain_log = '\n'.join(f'#  {line}' for line in callstack_to_str(callstack).split('\n'))

    filename = f'{grafico_id}_transformer.py'
    with open(filename, 'w') as f:
        f.write(imports)
        f.write('\n')
        f.write('#  DEFINITIONS_START\n')
        f.write(definitions)
        f.write('#  DEFINITIONS_END\n')
        f.write('\n\n')
        f.write('#  PIPELINE_START\n')
        f.write(chain_prog)
        f.write('\n')
        f.write('#  PIPELINE_END\n')
        f.write('\n\n')
        f.write(chain_log)
    
    return filename