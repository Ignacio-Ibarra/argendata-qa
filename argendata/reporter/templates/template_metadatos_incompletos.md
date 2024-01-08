## Plantilla de metados: datos faltantes

En la siguiente tabla se detallan para cada dataset las columnas que poseen
datos faltantes y la cantidad. Recordamos que no puede haber datos faltantes en ninnguna columna
de la plantilla de metadatos. 

<!-- data.tabla_metadatos_incompletos espera un pd.DataFrame de la siguiente forma: 
|dataset_archivo	                                                    |columna_plantilla  |filas_incompletas  |
|-----------------------------------------------------------------------|-------------------|-------------------|
|composicion_exportaciones_servicios_EBOPS_2digitos_agrupado.csv        |fecha_fuente       |10                 |
|exportaciones_bienes_servicios_millones_usd_constantes_2015.csv        |fecha_fuente       |10                 |
|exportaciones_servicios_top_20_destinos.csv                            |fecha_fuente       |14                 |
|indice_apertura_comercial.csv                                          |fecha_fuente       |8                  |
|indice_valores_unitarios_exportacion_bienes_2000.csv                   |fecha_fuente       |8                  |    
|indice_volumen_exportaciones_bienes_2000.csv                           |fecha_fuente       |8                  |
|participacion_exportaciones_bienes_servicios_porcentaje_pib.csv        |fecha_fuente       |8                  |
|participacion_exportaciones_servicios_porcentaje_exportaciones.csv     |fecha_fuente       |8                  | 
-->


{{data.tabla_metadatos_incompletos.to_markdown()}}
