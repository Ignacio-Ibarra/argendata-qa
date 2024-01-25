

# Controles en datasets

En esta sección se detallan los controles realizados sobre los datasets. 
Dichos controles verifican el cumplimiento de los estándares determinados en la documentación: 
[Estándar para elaboración de datasets](https://docs.google.com/document/d/1vH59Akk1eZTb0m4wIyEdhyVV_rx2q8lg4bG5k2tJP20/edit?usp=sharing). 

La lista de datasets provista a continuación corresponde con la intersección entre el conjunto de 
datasets efectivos y el conjunto de datasets declarados. En caso de que la lista se enecuentre vacía
significa que los conjuntos no tienen ningún elemento en común.   

{{data.to_markdown(index=False)}}


## Acerca de los controles realizados

Comentamos brevemente los controles realizados. 

*   **Codificación del archivo**: se hacen controles de `encoding` y `delimiter`. En caso de que alguno de los dos no pueda ser detectado el informe reporta `Error`

*   **Formato del dataset**: 
    *   Formato `long` o `wide`: se verifica que el dataset se encuentre en formato `long`. Es importante que los datos se presenten de manera `long` para que el dataset tenga una estructura normalizada y en un futuro podamos relacionar datos entre distintos datasets. Por el momento la implementación de éste control es en cierto modo probabilística: no podemos asegurar cual es el formato, pero sí nos interesa mostrar un `warning`. El `warning` es bastante estricto, puesto que se activa cuando la cantidad de columnas declaradas como `claves` es menos que el 50% de las columnas. 
    *   Nombres columnas: se verifica que las columnas estén formateados de acuerdo a la [documentación]((https://docs.google.com/document/d/1vH59Akk1eZTb0m4wIyEdhyVV_rx2q8lg4bG5k2tJP20/edit?usp=sharing)). 


*   **Controles filas duplicadas**: se verifica si se encontraron filas con valores duplicados tomando en cuenta unicamente los columnas claves definidas en la plantilla de metadata  en el campo `primary_key`. 

*   **Controles valore nulos**: para las columnas definidas como `nullable == FALSE` en la Plantilla de Metadatos se verifica que no existan nulos. 

*   **Caracteres raros**: para todas las columnas cuyo tipo de dato sea una cadena de carcteres se verifica que no se encuentren caracteres raros. 

### Fallo de Reporte

Los casos en que el reporte falla y no se puede realizar son: 

*   Cuando no es posible encontrar un `encoding` o cuando no es posible detectar un `delimiter`, en esos casos todos los controles no se realizan y devuelven `Error`. 

*   Puede existir el caso en que los `encoding` y `delimiter` sean detectados, pero que por algún problema el dataset es leído de manera defectuosa, en ese caso los demás controles no se realizan y devuelven `Error`.

En dichos casos se requiere trabajar sobre los archivos para modificarlos de modo tal de que puedan ser correctamente leídos. 




