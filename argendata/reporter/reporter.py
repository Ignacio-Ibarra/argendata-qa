import json
import os
import numpy as np
from pandas import DataFrame
from jinja2 import Environment, FileSystemLoader, Template
from typing import Literal, Callable
from .constants import *

# Acá está la clase de Template. 
#============================================================

class JinjaEnv: 

    template_path:str

    def __init__(self, template_path:str):
        """Genera Environment de Jinja y toma el template_path para
        retornar un objeto template de Jinja2

        Args:
            template_path (str): ruta relativa del template a utilizar
        """
        
        # Cargar el entorno de Jinja2 desde el directorio actual
        self.env = Environment(loader=FileSystemLoader("."))
        
        # Cargar el template de Markdown
        self.template = self.env.get_template(template_path)


class MDTemplate:
    
    template_path : str
    data : dict

    def __init__(self, template_path:str, data:dict):
        """Toma un path y datos y genera un template

        Args:
            template_path (str): _description_
            data (dict): _description_

        """

        self.template : Template =  JinjaEnv(template_path=template_path).template
        self.data = data
       
        
    def render_and_save_to_file(self, output_path:str, mode:Literal["w", "a", "w+"]='w+')->str|None:
        """Toma un Template de Jinja y data en un dict, guarda un archivo de texto
        (soporta html, md, txt) en el `output_path` y devuelve la ruta en la que se
        ha guardado

       Args:
            output_path (str): path-like
            mode (Literal['w', 'a', 'w+']) el valor por default es 'w+' (re-escribe) 

        Returns:
            str|None: devuelve path en donde se guardó el render o None en caso de error. 

        """
        try: 
            # Renderizar el template con los datos del usuario
            string_rendered = self.template.render(data=self.data)
            
            # Guarda a archivo, acepta html, md, txt...
            with open(output_path, mode=mode) as f: 
                f.write(string_rendered)
            return output_path
        
        except Exception as e:
            print(e)
            return None
        
def template_factory(template_path:str)->Callable[[dict], str]:
    """Función currificada que permite pasar un path y data

    Args:
        template_path (str): path en el cual se aloja el tempalte utilizado

    Returns:
        Callable[[dict], str]: diccionario que contiene datos necesarios para incrustar en el template. 
    """
    return lambda data: MDTemplate(template_path=template_path, data=data).render_and_save_to_file()


#==================================================================

class Gutter:

    template_path : str
    nombre_subtopico : str
    fecha_reporte : str
    
    def __init__(self, template_path, nombre_subtopico:str, fecha_reporte:str): 

        self.template_path = template_path
        self.nombre_subtopico = nombre_subtopico
        self.fecha_reporte = fecha_reporte
        
        self.data : dict = {
            'fecha_reporte': self.fecha_reporte,
            'nombre_subtopico': self.nombre_subtopico
            }
        
        self.data_templated = MDTemplate(template_path=self.template_path, data=self.data)

    def save_gutter_to_file(self, output_path:str, mode:Literal["w", "a", "w+"]='w+')->str|None:
        """Guarda el Gutter lleno a un archivo de texto (soporta html, md, txt) en el `output_path` y devuelve la ruta en la que se
        ha guardado. Por default re-escribe los archivos. 

       Args:
            output_path (str): path-like
            mode (Literal['w', 'a', 'w+']) el valor por default es 'w+' (re-escribe) 

        Returns:
            str|None: devuelve path en donde se guardó el render o None en caso de error. 
        """
        return self.data_templated.render_and_save_to_file(output_path=output_path, mode=mode)


#===============================================================================

class Resumen:

    template_path : str
    cant_graficos : int
    string_registro_duplicados : str
    tabla_resumen : DataFrame
    tabla_datasets_no_cargados: DataFrame
    tabla_datasets_no_declarados: DataFrame
    tabla_scripts_no_cargados: DataFrame
    tabla_scripts_no_declarados:DataFrame
    
    def __init__(self, 
                 template_path:str, 
                 cant_graficos:str,
                 string_errores_graficos:str,
                 tabla_resumen : DataFrame,
                 tabla_datasets_no_cargados : DataFrame,
                 tabla_datasets_no_declarados : DataFrame,
                 tabla_scripts_no_cargados : DataFrame,
                 tabla_scripts_no_declarados : DataFrame): 

        self.data : dict = {   
            'template_path' : template_path,
            'cant_graficos' : cant_graficos,
            'string_errores_graficos' : string_errores_graficos,
            'tabla_resumen' : tabla_resumen,
            'tabla_datasets_no_cargados' : tabla_datasets_no_cargados,
            'tabla_datasets_no_declarados' : tabla_datasets_no_declarados,
            'tabla_scripts_no_cargados' : tabla_scripts_no_cargados,
            'tabla_scripts_no_declarados' : tabla_scripts_no_declarados
            }
        
        self.data_templated = MDTemplate(template_path=self.template_path, data=self.data)

    def save_resumen_to_file(self, output_path:str, mode:Literal["w", "a", "w+"]='w+')->str|None:
        """Guarda el Gutter lleno a un archivo de texto (soporta html, md, txt) en el `output_path` y devuelve la ruta en la que se
        ha guardado. Por default re-escribe los archivos. 

       Args:
            output_path (str): path-like
            mode (Literal['w', 'a', 'w+']) el valor por default es 'w+' (re-escribe) 

        Returns:
            str|None: devuelve path en donde se guardó el render o None en caso de error. 
        """
        return self.data_templated.render_and_save_to_file(output_path=output_path, mode=mode)


#======================================================================
class InspeccionFuentes:

    template_path : str
    tabla_inspeccion_fuentes:DataFrame
    
    def __init__(self, 
                 template_path:str, 
                 tabla_inspeccion_fuentes : DataFrame): 

        self.data : dict = {
            'template_path' : template_path,
            'tabla_inspeccion_fuentes' : tabla_inspeccion_fuentes 
            }
        
        self.data_templated = MDTemplate(template_path=self.template_path, data=self.data)

    def save_inspeccion_fuentes_to_file(self, output_path:str, mode:Literal["w", "a", "w+"]='w+')->str|None:
        """Guarda el Gutter lleno a un archivo de texto (soporta html, md, txt) en el `output_path` y devuelve la ruta en la que se
        ha guardado. Por default re-escribe los archivos. 

       Args:
            output_path (str): path-like
            mode (Literal['w', 'a', 'w+']) el valor por default es 'w+' (re-escribe) 

        Returns:
            str|None: devuelve path en donde se guardó el render o None en caso de error. 
        """
        return self.data_templated.render_and_save_to_file(output_path=output_path, mode=mode)


#===========================================================================
class MetadatosIncompletos:

    template_path : str
    tabla_metadatos_incompletos:DataFrame
    
    def __init__(self, 
                 template_path:str, 
                 tabla_metadatos_incompletos : DataFrame): 
        
        self.template_path = template_path
        self.data : dict = {
           'tabla_inspeccion_fuentes' : tabla_metadatos_incompletos 
            }
        
        self.data_templated = MDTemplate(template_path=self.template_path, data=self.data)

    def save_metadatos_incompletos_to_file(self, output_path:str, mode:Literal["w", "a", "w+"]='w+')->str|None:
        """Guarda el Gutter lleno a un archivo de texto (soporta html, md, txt) en el `output_path` y devuelve la ruta en la que se
        ha guardado. Por default re-escribe los archivos. 

       Args:
            output_path (str): path-like
            mode (Literal['w', 'a', 'w+']) el valor por default es 'w+' (re-escribe) 

        Returns:
            str|None: devuelve path en donde se guardó el render o None en caso de error. 
        """
        return self.data_templated.render_and_save_to_file(output_path=output_path, mode=mode)


class DetallesDataset: 

    template_path : str
    nombre_archivo : str
    encoding_archivo : str
    encoding_resultado : str
    delimiter_archivo : str
    delimiter_archivo_resultado : str
    qa : dict

    def __init__(self, 
                 template_path:str, 
                 tabla_metadatos_incompletos : DataFrame): 

        self.data : dict = {
            'template_path' : template_path,
            'tabla_inspeccion_fuentes' : tabla_metadatos_incompletos 
            }
        
        self.data_templated = MDTemplate(template_path=self.template_path, data=self.data)

    def save_control_dataset_to_file(self, output_path:str, mode:Literal["w", "a", "w+"]='w+')->str|None:
        """Guarda el Gutter lleno a un archivo de texto (soporta html, md, txt) en el `output_path` y devuelve la ruta en la que se
        ha guardado. Por default re-escribe los archivos. 

       Args:
            output_path (str): path-like
            mode (Literal['w', 'a', 'w+']) el valor por default es 'w+' (re-escribe) 

        Returns:
            str|None: devuelve path en donde se guardó el render o None en caso de error. 
        """
        return self.data_templated.render_and_save_to_file(output_path=output_path, mode=mode)


Integer = int|np.int64

# Esto falta corregir. 
# Hay que tener un dict que no haya que procesar datos para incrustarlos en el markdown. 
# Así como está no sirve. 
expected_gutter = {
    'subtopico' : str,                                  # Corregido - datos a incrustar en tamplate GUTTER
    'fecha_verificacion' : str                          # Corregido - datos a incrustar en tamplate GUTTER
    }                         

expected_resumen = {
    "string_errores_graficos" : str,                    # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_resumen" : DataFrame,                        # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_datasets_no_cargados" : DataFrame,           # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_datasets_no_declarados" : DataFrame,         # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_scripts_no_declarados" : DataFrame,          # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_scripts_no_cargados" : DataFrame,            # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_variables_no_declaradas" : DataFrame,        # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_variables_no_cargadas" : DataFrame          # Corregido - datos a incrustar en tamplate RESUMEN
    }

expected_insepeccion_fuentes = {
    "tabla_inspeccion_fuentes" : DataFrame             # Corregido - datos a incrustar en tamplate INSPECCION FUENTES
    }

expected_metadatos_incompletos = {
    'tabla_metadatos_incompletos' : DataFrame|None          # Corregido - datos a incrustar en tamplate METADATOS INCOMPLETOS
    }


expected_desglose_dataset = {
    'dataset_verificados' : dict|None 
}



def unexpected_types(key:str, expected_typename: str, got_typename: str) -> str:
    return f"Tipo de dato incorrecto para la clave '{key}'. \nSe esperaba '{expected_typename}', pero se encontró '{got_typename}'."

def dict_from_json(path:str): 
    extension = path.split(".")[-1].lower()
    if extension!='json':
        raise ValueError(f"The file in {path} is not a json file")
    elif not os.path.exists(path):
        raise FileNotFoundError(f"The file in {path} was not founded")
    else:
        try:
            with open(path, 'r') as json_file:
                json_data = json_file.read()
            returned_dict = json.loads(json_data)
            return returned_dict
        except (ValueError, TypeError) as e:
            print(e)
            return None

def load_results(results_to_report:dict|str):
    """Carga el diccionario de resultados desde un diccionario de python o 
    desde un JSON

    Args:
        results_to_report (dict | str): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if isinstance(results_to_report, dict):
        results_dict = results_to_report
        
    elif isinstance(results_to_report, str):
        results_dict = dict_from_json(results_to_report)
        print(f"JSON file: {results_to_report} was loaded into a dict object")
    else: 
        raise ValueError(f"'results_to_report' must be dict or str")
    return results_dict

def check_dict_keys(true_dict:dict, expected_dtypes:dict):

    # Chequeo si al menos todas las key de expected_dtypes están en test_dict
    # Lo hago así para no depender del orden en el que venga el dict
    return len(np.setdiff1d(expected_dtypes.keys(), true_dict.keys())) == 0



def check_dict_dtypes(true_dict:dict, expected_dtypes:dict) -> tuple[bool, str]:
    for key, expected_type in expected_dtypes.items():
       # Verifica si el tipo de dato es el esperado
        if not isinstance(true_dict[key], expected_type):
            error_string = unexpected_types(key, expected_type.__name__, type(true_dict[key].__name__))
            return False, error_string
    # Si todas las claves y tipos de datos coinciden, devuelve True
    return True, ''

def get_result_dict(true_dict:dict, expected_dtypes:dict)->dict|ValueError:

    a = check_dict_keys(true_dict=true_dict, expected_dtypes=expected_dtypes)
    b, err_string = check_dict_dtypes(true_dict=true_dict, expected_dtypes=expected_dtypes)
    # Si cumple con los dos obtengo intersección
    if all([a,b]):
        result_dict : dict = {k:true_dict[k] for k in expected_dtypes.keys()}
        return result_dict
    else: 
        raise ValueError(err_string)
        
separator_dict = {
    'template_cutter.md': ['subtopico','fecha'],
    'template_resumen.md': ["cant_graficos", "string_errores_graficos", "tabla_resumen","tabla_controles_datasets"],
    'template_inspeccion_fuentes.md': ["tabla_inspeccion_fuentes"],
    'template_metadatos_incompletos.md': ["tabla_metadatos_incompletos"]
}


    
class Results:
    template_results : dict|str
    transform_list : list[str]

    def __init__(self, template_results : dict): 
        """Esta función obtiene un diccionario o un path a un JSON que contenga
        los datos listos para incrustar en un tamplate

        Args:
            results_to_report (dict | str): diccionario con los datos o str path-like
        """
        
        try: 
            results_dict = load_results(results_to_report=template_results)
            self.results_dict = get_result_dict(true_dict=results_dict, expected_dtypes=expected_dtypes)
            
            print("Result dict already loaded!!!")
        except Exception as e:
            print(e)
            return None
    
    def assign_keywords_to_templates(self, separator_dict : dict[str,str])->dict[dict]:
        """El objetivo de la func  es asignar algunas clave,valor a una nueva clave que corresponda
        a un template. 

        Args:
            result_dict (dict): contiene las claves y el valor de un análisis realizado sobre un subtopico. 
            separator_dict (dict[str,str]): contiene como claves los templates y los valores son las claves de result_dict

        Returns:
            dict[dict]: _description_
        """
        rearranged_dict = dict()

        for templ_key in separator_dict.keys():
            inner_keys = separator_dict[templ_key]
            inner_dict = {k:v for k,v in self.result_dict if k in inner_keys}
            rearranged_dict[templ_key] = inner_dict

        return rearranged_dict







    
    
    
    
    







