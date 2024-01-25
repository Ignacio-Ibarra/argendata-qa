
***
#### _Nota inicial:_

Para que el reporte pueda realizarse de manera acabada, es necesario que se cumpla con los criterios detallados [Estándares ArgenData para Analistas](https://docs.google.com/document/d/1JZm8BAnqNqzOITUNJi4sdjYePDHEY3nZI712BwUwAes/edit?usp=sharing). Asimismo, es de suma relevancia el guardado de los  datasets y los scripts en las carpetas correspondientes del sistema de archivos y completar de forma correcta La plantilla de metadatos, es decir que no queden registros que tengan campos incompletos.

***

# Control del sistema de archivos

En esta sección se detalla la verificación de la carga en el sistema de archivos, 
contrastando lo que efectivamente fue cargado en él con lo declarado en la Plantilla de Metadatos.

## Resumen


- Cantidad de gráficos ingresados en la plantilla de metadatos: {{cant_graficos}} 


- Registros duplicado en plantilla: {{string_errores_graficos}}

En la siguiente tabla se resume el contenido encontrado dentro de la carpeta de `GoogleDrive` y lo declarado en la Plantlla de Metadatos.


{{tabla_resumen.to_markdown()}}


*   **Cargados**: datasets o scripts que se encontraron en GoogleDrive.
*   **Declarados**: datasets o scripts  declarados en la plantilla de metadatos
*   **Intersección**: datasets o scripts que estaban en la plantilla de metadatos y en GoogleDrive
*   **No cargados**: datasets o scripts que estaban en la plantilla de metadatos pero no en GoogleDrive
*   **No declarados**: datasets o scripts que estaban en GoogleDrive pero no en la plantilla de metadatos

## Errores

Aquí se detallan los datasets/scripts no cargados o no declarados. 

### Datasets no cargados

En la tabla a continuación se detallan los datasets que aparecen en la plantilla de metadatos, pero no se encuentran en `GoogleDrive`.
Si la tabla se encuentra vacía significa que no se han encontrado errores. 


{{tabla_datasets_no_cargados.to_markdown(index = False)}}


### Datasets no declarados

Datasets que se encuentran en `GoogleDrive` pero no en la plantilla de metadatos.
Si la tabla se encuentra vacía significa que no se han encontrado errores.


{{tabla_datasets_no_declarados.to_markdown(index = False)}}


### Scripts no cargados

Scripts que aparecen en la plantilla de metadatos, pero no se encuentran en `GoogleDrive`. Si la tabla
se encuentra vacía significa que no se han encontrado errores.


{{tabla_scripts_no_cargados.to_markdown(index = False)}}


### Scripts no declarados

Scripts que se encuentran en `GoogleDrive` pero no en la plantilla de metadatos. Si la tabla
se encuentra vacía significa que no se han encontrado errores.


{{tabla_scripts_no_declarados.to_markdown(index = False)}}


