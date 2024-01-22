

## Dataset {{nombre}} 

### Control de formato -- Columnas


A continuación se encuentra un detalle de las columnas que fueron declaradas en la plantilla y las que efectivamente
se encontraron en el dataset. Si la tabla está vacía, entonces no hubo diferencias.
Si hubo diferencias, es probable que el resto del reporte no haya podido completarse.

{{columnas_errores.to_markdown(index=False)}}

### Controles de codificación

*   **Encoding**: el detectado es `{{encoding}}`. {{encoding_resultado}}. 
*   **Delimiter**: el detectado es "{{delimiter}}". {{delimiter_resultado}}. 

### Controles de formateo del dataset

*   **Control Formato Long**: {{tidy_data}}

*   **Nombres columnas**: {{header}}

### Duplicados, nulos y caracteres raros. 

*   **Filas duplicadas**: {{duplicates}}
*   **Columnas con nulos**: {{nullity_check}}
*   **Caracteres raros**: {{special_characters}}

### Tipos de Datos 

A continuación se presenta un detalle por variable de los controles realizados. 
Si la tabla se encuentra vacía significa que no se han registrado errores. 

{{tipo_datos.to_markdown(index=False)}}


### Caracteres especiales 

En la siguiente tabla se detallan las variables que contienen en sus datos cadenas con caracteres especiales.
Si la tabla se encuentra vacía significa que no se han registrado errores.  

{{detalle_caracteres_especiales.to_markdown(index=False)}}


