

### Dataset {{data.nombre}} 

#### Controles de codificación

*   **Encoding**: el detectado es `{{data.encoding}}`. {{data.encoding_resultado}}. 
*   **Delimiter**: el detectado es "{{data.delimiter}}". {{data.delimiter_resultado}}. 

#### Controles de formateo del dataset

- **Formato long**: {{data.qa['tidy_data']}}
- **Filas duplicadas**: {{data.qa['duplicates']}}
- **Columnas con nulos**: {{data.qa['nullity_check']}}
- **Nombres columnas**: {{data.qa['header']}}
- **Caracteres raros**: {{data.qa['special_characters']}}

#### Tipos de Datos 

A continuación se presenta un detalle por variable de los controles realizados. 
Si la tabla se encuentra vacía singifica que no se han registrado errores. 

{{data.qa['tipo_datos'].to_markdown(index=False)}}


#### Caracteres especiales 

En la siguiente tabla se detallan las variables que contienen en sus datos cadenas con caracteres especiales.
Si la tabla se encuentra vacía singifica que no se han registrado errores.  

{{data.qa['detalle_caracteres_especiales'].to_markdown(index=False)}}


