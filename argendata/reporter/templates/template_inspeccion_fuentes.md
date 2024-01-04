## Inspección Fuentes

La siguiente tabla provee una inspección rápida de las fuentes e instituciones
utilizadas en el subtópico. Es importante que las mismas cumplan con: 

* No poseer errores de escritura.
* Estar en idioma español. 
* El nombre de una institució no puede aparecer en el nombre de la fuente. Hay algo mal ahí!!!
* "Elaboración propia en base a... no va, citamos la fuente". 
* No debe haber caracteres raros. Ejemplo: `\+[]=_*#&@|`


<!-- data.tabla_inspeccion_fuentes espera un pd.DataFrame de la siguiente forma: 

|Fuente                                     |Institución    |
|-------------------------------------------|---------------|
|World Population Prospects 2022            |Banco Mundial  |
|International Comparison Program           |Sarasa         |
|UNDP (United Nations Development Programme)|Naciones Unidas|
|Poverty and Inequality Platform            |Sarasas        |


 -->

{{data.tabla_inspeccion_fuentes.to_markdown()}}
