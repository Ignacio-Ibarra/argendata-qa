"""
Necesita: 
    - client_creds.json: Archivo de credenciales de la API de Google Drive.
    - datasets_definitivos.csv: Una tabla que tiene dos columnas, una con el nombre del archivo y otra con el id del archivo en Google Drive.

Este script descarga los archivos de Google Drive y los guarda en "subtop_files/". (Ver move_files.py)
"""



from pandas import read_csv
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

gauth = GoogleAuth()
gauth.LoadCredentialsFile("./client_creds.json")

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

drive = GoogleDrive(gauth)


if __name__ == '__main__':
    df = read_csv('./datasets_definitivos.csv')

    for nombre, id in df.iloc:
        nombre_lower = nombre[:6].lower()
        folder = nombre_lower + '_files'
        os.makedirs(folder, exist_ok=True)

        folder = os.path.abspath(folder)
        
        
        print(f'Descargando {nombre} en {folder}.')
        file = drive.CreateFile({'id': id})
        file.GetContentFile(os.path.join(folder, file['title']))