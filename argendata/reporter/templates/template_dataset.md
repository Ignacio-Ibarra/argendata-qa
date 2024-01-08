<!-- Este template es para cada uno de los datasets, se despliega mucha info de un mismo dataset.
'data' es el input general de este template, un dict que tiene muchos datos complilados de un mismo dataset. 
Posee los siguientes elementos: 

data.nombre (str): contiene el nombre del archivo analizado

data.encoding (str): conteiene el nombre del encoding en el que se encuentra el archivo

data.encoding_resultado (str): 'OK' o 'MAL' 

data.delimiter (str): contiene el delimiter del archivo analizado

data.delimiter_resultado (str): 'OK' o 'MAL' 

data.qa (dict): posee un diccionario con los resultados del anlisis de calidad del dato. Dicho diccionario
contiene las siguientes claves:

    'tidy_data': str # Resultado si el dataset tiene la data en formato tidy. 'OK' o 'MAL'
    'duplicates': str, # Resultado si el dataset contiene o no filas duplicadas. 'OK' o 'MAL'
    'nullity_check': str, # Resultado si el dataset contiene columnas que deberían ser not nullable con nulos. 'OK' o 'MAL'
    'header': str, # Resultado si el dataset posee bien formateado el header. 'OK' o 'MAL'
    'special_characters': str # Resultado si el dataset contiene caracteres especiales. 'OK' o 'MAL'
    'tipo_datos' : pd.DataFrame, columnas: 
                               ['Variable Nombre', 'Tipo de Dato Efectivo', 'Tipo de Dato Declarado']
                Variable Nombre: contiene el nombre de una variable del dataset
                Tipo de Dato Efectivo: contiene el tipo de dato encontrado en el dataset
                Tipo de Dato Declarado: es el dato declarado en la plantilla de metadatos
    'detalle_caracteres_especiales':pd.Dataframe # Contiene una tabla con las columnas:
                    ['Variable Nombre', 'Valor con errores','Filas']
                    Variable Nombre: str nombre de la variable
                    Valor con Errores: str cadena de caracteres que presenta errores
                    Filas: str números de fila donde aparecen los errores. 

-->


#### Dataset {{data.nombre}} 

El `encoding` detectado es {{data.encoding}} ({{data.encoding_resultado}}). 
El `delimiter` encontrado es {{data.delimiter}} ({{data.delimiter_resultado}}). 

- Formato `long` {{data.qa['tidy_data']}}
- Filas duplicadas: {{data.qa['duplicates']}}
- Columnas con nulos: {{data.qa['nullity_check']}}
- Nombres columnas: {{data.qa['header']}}
- Caracteres raros: {{data.qa['special_characters']}}

**Tipos de Datos** 

A continuación se presenta un detalle por variable de los controles realizados. 

{{data.qa['tipo_datos'].to_markdown()}}


**Caracteres especiales** 

En la siguiente tabla se detallan las variables que contienen en sus datos cadenas con caracteres especiales. 

{{data.qa['detalle_caracteres_especiales'].to_markdown()}}


