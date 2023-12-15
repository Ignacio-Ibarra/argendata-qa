import json
from typing import Literal

from pydrive.files import GoogleDriveFile
from utils.files import file
from utils.files.mime import extensions
from gwrappers import GDrive
from logger import inject_logger
from utils import keys_included, now, stopwatch, json_to_file, MethodMapping


@inject_logger('gresources')
class GResource:
    """
    Recurso de Google Drive. Un recurso puede ser un archivo o una carpeta.
    Es una interfaz entre un recurso local y un recurso en la nube.
    Da utilidades para el manejo de recursos.
    """

    FOLDER_MIMETYPE = "application/vnd.google-apps.folder"

    @property
    def extension(self, priority: Literal['title'] | Literal['mime'] | Literal['mimeType'] = 'title'):
        index = self.title.rfind('.')

        title_extension: None | str = None
        if index != -1:
            title_extension = self.title[index:]

        mime_extension: None | str
        if self.mimeType == GResource.FOLDER_MIMETYPE:
            mime_extension = ''  # folders don't have extensions
        else:
            mime_extension = extensions.get(self.mimeType, None)

        if priority == 'title' and title_extension is not None:
            return title_extension
        elif mime_extension is not None:
            return mime_extension
        else:
            raise ValueError("Couldn't deduce extension from name nor from mimeType.")

    @property
    def clean_title(self):
        index = self.title.rfind('.')

        if index == -1:
            return self.title

        return self.title[:index]

    @property
    def DEFAULT_FILENAME(self):
        """Devuelve el nombre de archivo (con extensión y fecha-hora actual) del recurso."""
        return f'{self.clean_title}_{now.string}{self.extension}'

    __fields__: list[str]
    """Tiene una lista de todos los campos permitidos en un pydrive.drive.GoogleDriveFile.
       Para mejorar la lectura, deben estar en orden alfabetico, y de menor a mayor largo.
       Son también campos de un GResource, se aplican en __init__."""

    __fields__ = [
        "appDataContents",  # bool
        "capabilities"  # str
        "copyRequiresWriterPermission",  # str
        "copyable",  # bool
        "editable",  # bool
        "embedLink",  # str
        "etag", "alternateLink",  # str
        "explicitlyTrashed", "createdDate",  # dict
        "iconLink",  # str
        "id",  # str
        "kind",  # str
        "labels",  # str
        "lastModifyingUser",  # dict
        "lastModifyingUserName",  # str
        "lastViewedByMeDate",  # str
        "markedViewedByMeDate",  # str
        "mimeType",  # str
        "modifiedDate",  # bool
        "ownerNames",  # list
        "owners",  # list
        "parents",  # list
        "quotaBytesUsed",  # str
        "selfLink",  # str
        "shared",  # bool
        "spaces",  # bool
        "title",  # list
        "userPermission",  # dict
        "version",  # str
        "writersCanShare",  # bool
    ]

    def __init__(self, data: dict):
        for field in GResource.__fields__:
            setattr(self, field, data.get(field, None))

    @staticmethod
    def get_if_exists(parent_id: str, title: str, mimeType: str) -> tuple[bool, None | GoogleDriveFile]:
        """
        Busca un recurso en una carpeta. Si existe, lo devuelve.
        :param parent_id: ID de la carpeta donde se va a buscar el archivo.
        :param title: Título del recurso a ser buscado.
        :param mimeType: mimeType del recurso a ser buscado.
        :return: Tupla (bool, archivo). Si la primer coordenada es False, la segunda es None.
        """
        q = f"mimeType='{mimeType}' and title='{title}' and '{parent_id}' in parents and trashed=false"
        gfile_list = GDrive.instance.ListFile(param={'q': q}).GetList()

        if len(gfile_list) > 0:
            return True, gfile_list[0]['id']
        else:
            return False, None

    @staticmethod
    def exists(parent_id: str, title: str, mimeType: str) -> bool:
        """
        Busca un recurso en una carpeta. Si existe, devuelve True.
        :param parent_id: ID de la carpeta donde se va a buscar el archivo.
        :param title: Título del recurso a ser buscado.
        :param mimeType: mimeType del recurso a ser buscado.
        :return: True si existe el archivo. False, sino.
        """
        return GResource.get_if_exists(parent_id, title, mimeType)[0]

    @staticmethod
    def create_and_upload(target_id: str, data: dict) -> 'GResource':
        """
        Crea un recurso de GoogleDrive y lo sube a la carpeta especificada.
        :param target_id: ID de la carpeta a la que se va a subir el recurso.
        :param data: Diccionario tipo pydrive.ApiResource. *Debe* contener las claves
        'mimeType' y 'title' y, si no es una carpeta, una clave 'contents'.

        Por ejemplo:
        {
            'title': 'example.csv',
            'mimeType': 'text/csv',
            'contents': {
                "str": \\
                    "Nombre, Edad, Ciudad\\nJuan, 25, Buenos Aires\\nAna, 30, Córdoba\\nMiguel, 22, Rosario"
                }
        }

        O, tambien, 'contents' puede ser: { "file": "/path/to/file.csv" }

        :return: El GResource vinculado al GoogleDriveFile creado.
        """

        if not keys_included(['mimeType', 'title'], data):
            raise KeyError("Parameter 'data' must have 'mimeType' and 'title' as keys.")

        resource_data = {
            'title': data['title'],
            'mimeType': data['mimeType'],
            'parents': [{'id': target_id}]
        }

        resource: GoogleDriveFile = GDrive.instance.CreateFile(resource_data)

        if GResource.exists(target_id, data['title'], data['mimeType']):
            GResource.log.debug(f'Resource already exists in {target_id}.')
            return GResource(resource)

        if data['mimeType'] != GResource.FOLDER_MIMETYPE:
            if 'content' not in data.keys():
                raise KeyError("File resource has to have 'content' as a dict key.")

            content_type: list[str] = list(data['content'].keys())

            if len(content_type) > 1:
                raise KeyError("'content' has to have only one key.")

            type_mapping = {
                'file': resource.SetContentFile,
                'str': resource.SetContentString
            }

            set_content_method = type_mapping.get(content_type[0], None)

            if set_content_method is None:
                raise KeyError("'content' key has to be either 'file' or 'str'.")

            set_content_method(data['content'][content_type[0]])

        resource = GDrive.instance.CreateFile(resource_data)
        resource.Upload()
        GResource.log.info(f"Resource {resource['id']} successfully created.")
        return GResource(resource)

    @staticmethod
    def build_subclass(gresource: dict) -> 'GFolder | GFile':
        """
        Construye un GResource válido (GFolder o GFile).
        :param gresource: Diccionario tipo pydrive.ApiResource.
        :return: GFolder o GFile dependiendo del mimeType de 'gresource'.
        """
        subclass = GFolder if gresource['mimeType'] == GResource.FOLDER_MIMETYPE else GFile
        return subclass(gresource)

    @staticmethod
    def from_id(_id: str, metadata: str = 'all') -> 'GFile | GFolder':
        """
        Trae un archivo de Google Drive con la ID especificada y genera un GResource correspondiente.
        :param _id: ID del archivo de Google Drive.
        :param metadata: Valor predeterminado: 'all'. Los metadatos que tiene que traer en la solicitud. Si no es
        el valor predeterminado, trae siempre 'title', 'id' y 'mimeType'. Tiene que ser una str con una lista de
        palabras separadas por comas. Pueden ser cualquiera de los campos de GResource.
        :return: GFile o GFolder correspondientemente.
        """
        drive = GDrive.instance
        file_obj = drive.CreateFile({'id': _id})
        GResource.log.debug(f'Resource instance created with id {_id}. Fetching metadata...')
        if metadata == 'all':
            file_obj.FetchMetadata()
        else:
            metadata: list[str] = metadata.replace(' ', '').split(',')
            metadata: set[str] = set(metadata)
            metadata: set[str] = metadata.union({'id', 'title', 'mimeType'})
            metadata: str = ','.join(metadata)
            file_obj.FetchMetadata(fields=metadata)

        result = GResource.build_subclass(file_obj)
        GResource.log.debug(f'Successfully instantiated locally {str(result)}.')
        return result

    def download(self, path='') -> str:  # typing.Self existe a partir de Python 3.11
        """
        Descarga el recurso a un archivo local.
        :param path: Ruta completa al archivo local. Por ejemplo '/path/to/file.csv'.
        Valor predeterminado: './{titulo}_{%d-%m-%y_%H%M%S}{extension deducida con el mimeType}'
        :return Devuelve una referencia al recurso (No al archivo).
        """
        GResource.log.debug(f"Downloading {str(self)}.")
        if not path:
            path = f'./{self.DEFAULT_FILENAME}'

        path = file(path)

        try:
            GDrive.instance.CreateFile({'id': self.id}).GetContentFile(path)
        except Exception as e:
            raise RuntimeError(f"There was an error downloading {str(self)}.\nHere are the details: {e}.")

        GResource.log.debug(f"Successfully downloaded {str(self)} to {path}")
        return path


    def copy_to(self, other: 'str | GFolder', force=False, title_dest=None):
        if not title_dest:
            title_dest = self.title

        if isinstance(other, str):
            return self.copy_to(GResource.from_id(other), force=force, title_dest=title_dest)
        
        if not force:
            if other.has(self) or other.has(GResource({'title': f'Copy of {self.title}', 'mimeType': self.mimeType})):
                GResource.log.debug(f'Cannot copy {title_dest} to {other.title}: File already exists.')
                return
            
        GDrive.instance.auth.service.files().copy(fileId=self.id, 
                                                  body={'parents': [{'kind': 'drive#fileLink',
                                                                     'id': other.id}]}).execute()
        
        GResource.log.debug(f'Successfully copied {title_dest} to {other.title}')
        return

    def __str__(self):
        return f'{self.__class__.__name__}({self.title} : {self.id})'

    def __repr__(self):
        return str(self)

    # TODO: Portar display_str(rich: bool) para imprimir los recursos de manera más visual y compatible con
    #   todas las consolas. (ASCII compatible / UNICODE+ANSI compatible)


class GFolder(GResource):
    """Subclase de GResource, provee utilidades específicas para operar con carpetas."""

    # TODO: Cache de IDs para no buscar los recursos de vuelta.
    # TODO: Si las IDs están cacheadas, tiene que haber un método para forzar la actualizaciçon de recursos.
    __resources_ids_: list

    __find_strategies: MethodMapping
    """Contiene las estrategias (métodos) para buscar archivos.
       Deben ser todos métodos de instancia (pues en find() se pasa el puntero a self)."""

    __find_strategies = MethodMapping()

    @property
    def resources(self):
        filelist: list[GoogleDriveFile] = \
            GDrive.instance.ListFile({'q': f"'{self.id}' in parents and trashed=false"}).GetList()

        self.__resources_ids_ = [f['id'] for f in filelist]

        return list(map(GResource.build_subclass, filelist))

    # TODO: Portar peek() y traverse_preorder() para mirar la carpeta normal y recursivamente (respectivamente).

    def as_dict(self, recursive=False):
        resources = self.resources
        files = []
        folders = []
        for resource in resources:
            if isinstance(resource, GFolder):
                if recursive:
                    folders.append(resource.as_dict(True))
                else:
                    folders.append({'title': resource.title, 'id': resource.id, 'mimeType': GResource.FOLDER_MIMETYPE})
            elif isinstance(resource, GFile):
                files.append(resource.as_dict())

        return {
            'title': self.title,
            'id': self.id,
            'mimeType': GResource.FOLDER_MIMETYPE,
            'resources': {
                'files': files,
                'folders': folders,
            }
        }

    def to_json(self, path='', recursive=False):
        if not path:
            path = f"./{self.title}{'-fs' if recursive else ''}.json"

        GResource.log.debug(f"Exporting {str(self)} to json {'recursively' if recursive else ''}.")

        self_as_dict, elapsed_time = stopwatch(self.as_dict, recursive=recursive)
        GResource.log.debug(f'Converted {str(self)} to dict in {elapsed_time}.')

        _, elapsed_time = stopwatch(json_to_file, filepath=file(path), obj=self_as_dict, indent=4)
        GResource.log.debug(f'Written {str(self)} to {path} in {elapsed_time}.')

    @__find_strategies.register('name')
    def find_by_name(self, name: str) -> GResource | None:
        return next(filter(lambda x: x.title == name, self.resources), None)

    @__find_strategies.register('id')
    def find_by_id(self, id: str) -> GResource | None:
        raise NotImplementedError()

    def _find_by_recursion(self, path: list[str]):
        next_ = self.find(path.pop(), by='name')
        if len(path) > 1:
            return next_._find_by_recursion(path)
        else:
            return next_.find(path.pop(), by='name')

    @__find_strategies.register('recursion')
    def find_by_recursion(self, path: str):
        _path = path.split('/')
        _path.reverse()
        return self._find_by_recursion(_path)

    # TODO: Quizá se puede implementar el file-globbing de manera más o menos práctica.
    #  Cada vez que aparece un '*' en paso recursivo puede:
    #  - Si es una carpeta, propagar la búsqueda a todas las subcarpetas
    #  - Si es parte de un archivo, filtrar por match. (Idealmente una funcion aparte)
    #  Sino, de manera más compleja, quizá con una máquina de estados concreta.
    def find(self, value, by, *args, **kwargs) -> GResource | None:
        method = self.__find_strategies.get(by, None)
        if not method:
            raise ValueError(f"Invalid find method '{by}'. "
                             f"It has to be one of these: {', '.join(self.__find_strategies.keys())}")

        return method(self, value, *args, **kwargs)
    

    def has(self, other: GResource):
        return GResource.exists(self.id, other.title, other.mimeType)


class GFile(GResource):
    """TODO: Subclase de GResource, provee utilidades específicas para operar con archivos."""

    def as_dict(self):
        return {
            'title': self.title,
            'id': self.id,
            'mimeType': self.mimeType
        }


# TODO: Terminar el FSTRee.
class FSTree:
    root: GFolder
