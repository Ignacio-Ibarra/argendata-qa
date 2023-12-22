<div align="center">
<img src="assets/argendata-logo.png" alt=""></img>
<h4>Branch Experimental</h4>
</div>

La idea de esta repo es continuar con el desarrollo de ArgenData (por ahora, la parte de QA) de manera más ordenada. En síntesis, tiene como objetivo principal dar estructura al proyecto para simplificar los procesos de creación y ejecución de controles sobre los datasets, haciendo que el código escale más y mejor.

## QA

La sección de QA (Quality Assurance), que actualmente es la única, debe ejecutar una seria de controles para todos sus datasets. Los controles están estructurados de manera jerárquica, de forma tal que existen algunos de nivel superior que llaman a otros de nivel inferior.

Por ejemplo, los `Controles` de `Subtopicos`, llaman a `Controles` de `Archivo` para analizar `.csv`s (Encoding, delimiter), y `Controles` de `Consistencia` (Diferencias entre lo declarado en la plantilla y lo efectivo en un dataset).
Etc.

```
Subtopico
|
|\_Archivo
|
 \_Consistencia
 
 ...

```

El entry point del programa de QA es 'main.py'. Ejecuta primero los tests unitarios y después el código (debug. después hay que sacarlo; los tests podrían ser un workflow con e.g. GitHub Actions y que se ejecuten cada vez que pusheemos).

## Google Drive

[(Ver gwrappers/)](./src/gwrappers/)

Como los datos se bajan desde Google Drive, usamos `pydrive` para interactuar con la correspondiente API. El programa espera que en `/.auth/` haya un archivo `client_secrets.json` para autenticar la sesión. Una vez autenticada, los datos de la sesión se guardan en `client_creds.json` en la misma carpeta.

Para simplificar (aún más) las interacciones que provee `pydrive`, [gwrappers](./src/gwrappers/) provee clases para manipular los recursos de Google Drive como objetos.
 
## Tests

Los tests unitarios están para asegurar que el código siga funcionando después de cualquier cambio. Las carpetas `src/` y `test/` deberían compartir la misma estructura, para que así los tests de una clase estén en la misma ruta relativa dentro de test (y viceversa con su implementación).

## To-Do

- [ ] Agregar verificaciones para que la funcionalidad sea igual o superior a la de la [_branch_ funcional.](https://github.com/datos-Fundar/argendata). En particular, lo que queda es:
    - Establecer qué controles deben ser `Verificadores` (y cuales pueden ser simplemente funciones).
    - Crear los verificadores necesarios.
    - En particular, cumplir con los siguientes controles:
        - [ ] Verificación datasets (declarados/efectivos)
        - [ ] Verifiación tipos de dato (declarados/efectivos)
        - [ ] Verificación scripts (declarados/efectivos)
        - [ ] Inspección de fuentes
        - [ ] Completitud
        - [ ] Verificación variables (declaradas/efectivas)
        - [ ] Cardinalidad
        - [ ] Nivel de registro
        - [ ] Nulos (existencia/conteo)
        - [ ] Nombres de columnas
        - [ ] Caracteres especiales
        - [ ] Long/Wide
 
- [ ] Pensar y escribir más testeos (unitarios o de integración), ya sea de los componentes que existen, o de los que se vayan a crear nuevos para:
    - Tener una especificación de _cómo_ debería funcionar el código. (Aunque sea laxa)
    - Poder medir y asegurar la calidad del código.

- [ ] Tener 'gwrappers' y 'utils' como globales y al resto de partes del proyecto como submódulos. (En principio, de Python, pero pueden ser de git)

- [ ] Buscar algunos archivos/carpetas automáticamente para no tener problemas con la ruta al working directory y las rutas relativas.

- [ ] Generar un arbol de sistema de archivos (con IDs de GoogleDrive) para tener una copia local del estado del Drive. Actualizar el árbol con cada solicitud, sólo en la rama correspondiente y sólo aquello que haya cambiado.

- [ ] Tener los submódulos o el proyecto entero como aplicación/es de consola parametrizadas, de forma tal que se pueda llamar a los programas desde un proceso externo. Eso implica que:
    - Los módulos ya sean objetos parametrizados que generen un resultado a través de instanciarlo con ciertos parámetros.
    - La forma de llamar a esos módulos es simplemente instanciarlos con los parámetros que se pasan por consola.

    - Nota: ésto también puede ayudar a futuro a que se cree un endpoint para subir archivos y generar el reporte de manera autónoma. (Aunque sea de un sólo dataset+plantilla).


- [ ] Usar `pydoc` o similares para documentar automáticamente el código.