## Resumen

<!-- data.cant_graficos espera un int -->
- Cantidad de gráficos: {{data["cant_graficos"]}} 

<!-- data.string_errores_graficos espera una string que puede decir "0 errores." o una string que diga "k errores. Graficos 1, 2, 5, 10, ..." -->
- Registros duplicado en plantilla: {{data["string_errores_graficos"]}}

## Sistema de archivos

En la siguiente tabla se resume el contenido encontrado dentro de la carpeta de `GoogleDrive` y lo declarado en la Plantlla de Metadatos.
<!-- data.tabla_resumen espera un pd.DataFrame que tenga la siguiente forma

|               | Datasets | Scripts  | Variables |
| ------------- | -------- | -------- | --------- |
| Declarados    | 0        | 10       | 137       |
| Efectivos     | 10       | 8        | 140       |
| No cargados   | 5        | 4        | 0         |
| No declarados | 5        | 2        | 3         |

-->
{{data["tabla_resumen"].to_markdown()}}

### Datasets no cargados

Datasets que aparecen en la plantilla de metadatos, pero no se encuentran en `GoogleDrive`.
<!--  data.tabla_datasets_no_cargados debe ser un pd.DataFrame con una columna "Datasets no cargados"-->
{{data["tabla_datasets_no_cargados"].to_markdown()}}

### Datasets no declarados

Datasets que se encuentran en `GoogleDrive` pero no en la plantilla de metadatos.
<!--  data.tabla_datasets_no_declarados debe ser un pd.DataFrame con una columna "Datasets no declarados"-->
{{data["tabla_datasets_no_declarados"].to_markdown()}}

### Scripts no cargados

Scripts que aparecen en la plantilla de metadatos, pero no se encuentran en `GoogleDrive`
<!--  data.tabla_scripts_no_cargados debe ser un pd.DataFrame con una columna "Scripts no cargados"-->
{{data["tabla_scripts_no_cargados"].to_markdown()}}

### Scripts no declarados

Scripts que se encuentran en `GoogleDrive` pero no en la plantilla de metadatos
<!--  data.tabla_scripts_no_declarados debe ser un pd.DataFrame con una columna "Scripts no declarados"-->
{{data["tabla_scripts_no_declarados"].to_markdown()}}

<!-- ### Variables no cargadas -->

<!-- Variables que se encuentran en en la plantilla de metadatos pero no en los archivos almacenados en `GoogleDrive`. -->
<!--  data.tabla_variables_no_cargadas debe ser un pd.DataFrame con dos columnas ["Dataset Nombre", "Variable Nombre"] -->
<!-- data["tabla_variables_no_cargadas"].to_markdown() -->

<!-- ### Variables no declaradas -->

<!-- Variables que se encuentran en archivos almacenados en `GoogleDrive` pero no en la plantilla de metadatos -->
<!--  data.tabla_variables_no_declaradas debe ser un pd.DataFrame con dos columnas ["Dataset Nombre", "Variable Nombre"] -->
<!-- data["tabla_variables_no_declaradas"].to_markdown() -->
