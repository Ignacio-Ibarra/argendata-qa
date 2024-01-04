import pandas as pd
import json
import os
import numpy as np
from pandas import DataFrame
from jinja2 import Environment, FileSystemLoader, Template
from typing import Literal, Callable

Integer = int|np.int64

# Esto falta corregir. 
# Hay que tener un dict que no haya que procesar datos para incrustarlos en el markdown. 
# Así como está no sirve. 
expected_dtypes= {
    'subtopico' : str,                                  # Corregido - datos a incrustar en tamplate GUTTER
    'fecha_verificacion' : str,                         # Corregido - datos a incrustar en tamplate GUTTER
    "string_errores_graficos" : str,                    # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_resumen" : DataFrame,                        # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_datasets_no_cargados" : DataFrame,           # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_datasets_no_declarados" : DataFrame,         # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_scripts_no_declarados" : DataFrame,          # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_scripts_no_cargados" : DataFrame,            # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_variables_no_declaradas" : DataFrame,        # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_variables_no_cargadas" : DataFrame,          # Corregido - datos a incrustar en tamplate RESUMEN
    "tabla_inspeccion_fuentes" : DataFrame,             # Corregido - datos a incrustar en tamplate INSPECCION FUENTES
    'tabla_metadatos_incompletos' : DataFrame,          # Corregido - datos a incrustar en tamplate METADATOS INCOMPLETOS
    'cant_variables_no_cargadas' : Integer,             # falta corregir
    'cant_variables_no_declaradas' : Integer,           # falta corregir
    'variables_no_cargadas' : list,                     # falta corregir
    'variables_no_declaradas' : list,                   # falta corregir
    'cant_scripts_efvos' : Integer,                     # falta corregir
    'cant_scripts_decl' : Integer,                      # falta corregir
    'scripts_declarados_no_cargados' : list,            # falta corregir
    'cant_scripts_declarados_no_cargados' : Integer,    # falta corregir
    'scripts_efectivos_no_declarados' : list,           # falta corregir
    'cant_scripts_efectivos_no_declarados' : Integer,   # falta corregir
    'variables_tipo_dato_verificar' : dict,             # falta corregir
    'columnas_con_nulos' : dict,                        # falta corregir
    'insepccion_fuentes' : dict,                        # falta corregir
    'encoding_delimiter_df' : dict,                     # falta corregir
    'control_calidad' : dict                            # falta corregir 
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
    results_to_report : dict|str
    transform_list : list[str]

    def __init__(self, results_to_report : dict|str): 
        """Esta función obtiene un diccionario o un path a un JSON que contenga
        los datos listos para incrustar en un tamplate

        Args:
            results_to_report (dict | str): diccionario con los datos o str path-like
        """
        
        try: 
            results_dict = load_results(results_to_report=results_to_report)
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
    
    template_path : str,
    data : dict

    def __init__(self, template_path:str, data:dict):
        """Toma un path y datos y genera un template

        Args:
            template_path (str): _description_
            data (dict): _description_
        """

        self.template : Template =  JinjaEnv(template_path=template_path).template
        self.data = data
        
    def render(self)->str|None:
        """
        Toma un Template de Jinja y data en un dict y devuelve una string
        """ 
        try: 
            # Renderizar el template con los datos del usuario
            string_rendered = self.template.render(data=self.data)
            return string_rendered
        
        except Exception as e:
            print(e)
            return None


def template_factory(template_path:str)->Callable[[dict], str]:
    return lambda data: MDTemplate(template_path=template_path, data=data).render() 

    
    
    
    
    







