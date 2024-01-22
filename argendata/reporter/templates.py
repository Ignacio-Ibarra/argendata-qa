from pandas import DataFrame
from .abstracto import AbstractTemplate, template

# [gutter, resumen, fuentes_df, metadatos_incompletos, datasest_verificados_df, *resumenes_ds]

@template('./argendata/reporter/templates/template_gutter.md')
class Gutter:
    subtopico: str
    fecha_verificacion: str # Formato: dd/mm/aaaa

@template('./argendata/reporter/templates/template_resumen.md')
class Resumen:
    cant_graficos: int

    string_errores_graficos: str
    """
    '0 errores gráficos' | Gráficos a, b, c [...]
    """

    tabla_resumen: DataFrame
    """
    |               |   **Datasets** |   **Scripts** |
    |:--------------|---------------:|--------------:|
    | Declarados    |              A |             F |
    | Efectivos     |              B |             G |
    | Interseccion  |              C |             H |
    | No declarados |              D |             I |
    | No cargados   |              E |             J |
    """

    # Tiene una sola columna '**Datasets no cargados**' con los nombres de los datasets no cargados
    tabla_datasets_no_cargados: DataFrame

    # Tiene una sola columna '**Datasets no declarados**' con los nombres de los datasets no declarados
    tabla_datasets_no_declarados: DataFrame

    """
    TODO: Se puede pensar como una sóla tabla:

    | Declarados Faltantes | Sin Declarar |
    |:---------------------|-------------:|

    """

    # Tiene una sola columna '**Scripts no cargados**' con los nombres de los scripts no cargados
    tabla_scripts_no_cargados: DataFrame

    # Tiene una sola columna '**Scripts no declarados**' con los nombres de los scripts no declarados
    tabla_scripts_no_declarados: DataFrame

    """
    TODO: Se puede pensar como una sóla tabla:
    
    | Declarados Faltantes | Sin Declarar |
    |:---------------------|-------------:|

    """

@template('./argendata/reporter/templates/template_inspeccion_fuentes.md')
class InspeccionFuentes:
    data: DataFrame

    """
    | **Fuente** | **Institución** |
    |:-----------|----------------:|
    | A          |               C |
    | B          |               D |

    """

@template('./argendata/reporter/templates/template_metadatos_incompletos.md')
class MetadatosIncompletos:
    data: DataFrame
    """
    | **dataset_archivo**   | **columna_plantilla**   |   **filas_incompletas** |
    |:----------------------|:------------------------|------------------------:|
    | A.csv                 | foo                     |                       X |
    | B.csv                 | bar                     |                       Y |
    """

@template('./argendata/reporter/templates/template_dataset_titulo.md')
class DatasetTitulo:
    """
    TODO: Esto es confuso, pues no son los datasets que se *verificaron*, son los de la intersección, indicando que
    se intentó verificar a los mismos (pues no tiene sentido verificar los que no estuvieran declarados, ni se pueden verificar
    los que no son efectivos).

    El tema es que puede haber datasets que no se hayan podido verificar por algún error. Por ende, habría que removerlos de esta lista,
    o bien, agregar una columna que indique aquellos que tuvieron errores.
    """
    
    # Tiene una sola columna '**Datasets Verificados**' con los nombres de los datasets de la intersección
    data: DataFrame

@template('./argendata/reporter/templates/template_dataset.md')
class ReporteDataset:
    nombre: str
    columnas_errores: DataFrame
    """
    | Declaradas Faltantes   | Sin Declarar   |
    |:-----------------------|:---------------|
    | A                      | X              |
    | B                      | Y              |
    """

    # Literalmente el encoding detectado
    # TODO: Hay que agrupar encodings con distinto nombre bajo el mismo, asi no es confuso.
    encoding: str
    encoding_resultado: str
    """
    Encoding 'válido'/'inválido, debería ser UTF-8'
    """

    # Literalmente el delimiter detectado
    delimiter: str
    delimiter_resultado: str
    """
    Delimiter 'válido'/"inválido, debería siempre ser ','"
    """

    # Strings formateadas con texto para display
    tidy_data: str
    """
    OK / "Posiblemente no sea wide, pues [...]"
    """

    header: str
    """
    OK / Algunas columnas tienen nombres inválidos: a, b, c, [...]
    """

    duplicates: str
    """
    OK / Se encontraron filas duplicadas en el dataset para las variables definidas como claves.
    """

    nullity_check: str
    """
    OK / Se encontraron valores nulos definidas para las variables not-nullable.
    """

    special_characters: str
    """
    OK / Se encontraron caracteres especiales, debajo se muestra la tabla [...]
    """

    tipo_datos: DataFrame
    """
    | **Variable Nombre**   | **Tipo de Dato Efectivo**   | **Tipo de Dato Declarado**   |
    |:----------------------|:----------------------------|:-----------------------------|
    | a                     | float64                     | int64                        |
    """

    detalle_caracteres_especiales: DataFrame
    """
    | **Variable Nombre**   | **Cadena con caracteres especiales**   | **Filas**                   |
    |:----------------------|:---------------------------------------|:----------------------------|
    | a                     | ábc                                    | [1, 2, 3 | Desde 1 hasta n] |
    """
