

### Dataset {{data.nombre}} 

#### Controles de codificación

*   **Encoding**: el detectado es `{{data.encoding}}`. {{data.encoding_resultado}}. 
*   **Delimiter**: el detectado es "{{data.delimiter}}". {{data.delimiter_resultado}}. 

#### Controles de formateo del dataset

El primer control realizado es si los datos se presentan en formato `long` o `wide`. Es importante
que los datos se presenten de manera `long` para que el dataset tenga una estructura normalizada y en un 
futuro podamos relacionar datos entre distintos datasets.

Por el momento la implementación de éste control es en cierto modo probabilística: no podemos asegurar 
cual es el formato, pero sí nos interesa mostrar un `warning`. El `warning` es bastante estricto, puesto 
que se activa cuando la cantidad de columnas declaradas como `claves` es menos que el 50% de las columnas. 

*   **Resultado de Control Formato Long**: {{data.qa['tidy_data']}}

El segundo resultado es observar la **presencia de caracteres raros en los nombres de las columnas**. 

*   **Nombres columnas**: {{data.qa['header']}}

#### Duplicados, nulos y caracteres raros. 

*   **Filas duplicadas**: {{data.qa['duplicates']}}
*   **Columnas con nulos**: {{data.qa['nullity_check']}}
*   **Caracteres raros**: {{data.qa['special_characters']}}

#### Tipos de Datos 

A continuación se presenta un detalle por variable de los controles realizados. 
Si la tabla se encuentra vacía singifica que no se han registrado errores. 

{{data.qa['tipo_datos'].to_markdown(index=False)}}


#### Caracteres especiales 

En la siguiente tabla se detallan las variables que contienen en sus datos cadenas con caracteres especiales.
Si la tabla se encuentra vacía singifica que no se han registrado errores.  

{{data.qa['detalle_caracteres_especiales'].to_markdown(index=False)}}


