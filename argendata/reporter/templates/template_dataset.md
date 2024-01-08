<!-- Este template es para cada uno de los datasets, se despliega mucha info de un mismo dataset.
'data' es el input general de este template un diccionario que tiene muchos datos complilados de un mismo dataset. 
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
    'otros_resultados' : pd.DataFrame, columnas: 
                               ['Variable Nombre', 'Tipo de Dato Efectivo', 'Tipo de Dato Declarado','Formato Columna','Caracteres Especiales']
    'variables': pd.Dataframe, columnas 
    
    'nullity_check': not_nullable,
    'header': str,
    'special_characters': ...

-->


#### Dataset {{data.nombre}} 

