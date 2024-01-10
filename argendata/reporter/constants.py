import numpy as  np
from pandas import DataFrame

# Acá esta la clase de resultados

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