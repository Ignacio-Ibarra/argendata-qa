import os

import pydrive, pydrive.auth, pydrive.drive
import requests

from logger import inject_logger
from utils import staticproperty, Singleton
from utils.files import file


@inject_logger('google_authentication')
class GAuth(metaclass=Singleton):
    """Singleton global de autenticación"""
    def __init__(self):
        self.gauth = None

    @classmethod
    def authenticate(cls, stored_creds="./.auth/client_creds.json") -> 'GAuth':
        """
        Autentica al usuario en Google Drive.
        Asume que existe un archivo ./.auth/client_secrets.json

        Ver: https://pythonhosted.org/PyDrive/quickstart.html

        :param stored_creds: Ruta al archivo donde se guardan las credenciales de la sesión.
        :return: Monoinstancia de GAuth.
        """
        result = cls()
        result.gauth = pydrive.auth.GoogleAuth()

        stored_creds = file(stored_creds)
        pydrive.auth.GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = file('./.auth/client_secrets.json')

        # Try to load saved client credentials
        if os.path.exists(stored_creds):
            GAuth.log.info('Found credentials, authenticating...')
            result.gauth.LoadCredentialsFile(stored_creds)
        else:
            # Authenticate if they're not there
            GAuth.log.info('Credentials not found, authenticating using webserver.')
            result.gauth.GetFlow()
            result.gauth.flow.params.update({'access_type': 'offline'})
            result.gauth.flow.params.update({'approval_prompt': 'force'})
            result.gauth.LocalWebserverAuth()

        if result.gauth.access_token_expired:
            # Refresh them if expired
            result.gauth.Refresh()
        else:
            # Initialize the saved creds
            result.gauth.Authorize()

        # Save the current credentials to a file
        result.gauth.SaveCredentialsFile(stored_creds)

        # drive = pydrive.drive.GoogleDrive(gauth)
        GAuth.log.info('Authenticated successfully.')
        return result

    # noinspection PyMethodParameters
    @staticproperty
    def instance():
        return GAuth.get_instance().gauth


@inject_logger('google_drive')
class GDrive(metaclass=Singleton):
    """Singleton global de GoogleDrive"""
    def __init__(self, gauth: GAuth | pydrive.auth.GoogleAuth):
        if gauth is None:
            raise ValueError("Authentication missing or incomplete.")
        elif isinstance(gauth, GAuth):
            self.__init__(gauth.gauth)
            return
        elif isinstance(gauth, pydrive.auth.GoogleAuth):
            self.gdrive = pydrive.drive.GoogleDrive(gauth)
        GDrive.log.info('Drive authenticated successfully.')

    # noinspection PyMethodParameters
    @staticproperty
    def instance():
        """
        Propiedad estática. Reemplazo sintáctico para obtener la instancia global de GDrive.


        Por ejemplo:


            `GDrive.instance.ListFile(param={'q': q}).GetList()`


        En vez de:


            `GDrive.get_instance().gdrive.ListFile(param={'q': q}).GetList()`


        :return: Monoinstancia de GDrive.
        """
        return GDrive.get_instance().gdrive

    @staticmethod
    def download_xlsx(id: str, outfile=None) -> str:
        url = f"https://docs.google.com/spreadsheets/export?id={id}&exportFormat=xlsx"
        r = requests.get(url, headers={"Authorization": "Bearer " + GAuth.instance.attr['credentials'].access_token})

        if not outfile:
            deduced_name = r.headers['Content-Disposition']
            index = deduced_name.find('filename=')
            deduced_name = deduced_name[index + 9:]
            deduced_name = deduced_name.split(';')[0]
            deduced_name = deduced_name.replace('"', '').replace("'", "")
            index = deduced_name.rfind('.')
            deduced_name, filename_extension = deduced_name[:index], deduced_name[index:]
            outfile = f'./tmp/{deduced_name}{filename_extension}'

        outfile = file(outfile)

        with open(outfile, 'wb') as fp:
            fp.write(r.content)

        return outfile
