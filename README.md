<div align="left">
 <img src="https://github.com/user-attachments/assets/56e7dede-1614-48c7-91e1-302194cc519d" alt="" width="300"></img>
</div>

&nbsp;


<!--
<div align='center'>
 <img src="./assets/agd-0124.gif" alt=""></img>
</div>
-->

La idea de esta repo es continuar con el desarrollo de ArgenData (por ahora, la parte de QA) de manera más ordenada. En síntesis, tiene como objetivo principal dar estructura al proyecto para simplificar los procesos de creación y ejecución de controles sobre los datasets, haciendo que el código escale más y mejor.

# Uso

El proyecto cuenta con una interfaz mínima de consola con parámetros y ayuda para cambiar la funcionalidad:

![image](./assets/cli.png)

> [!CAUTION]
> Si pasamos `-C` o `--clean-first` se borra TODO el contenido del cache (`tmp/`) y de los resultados (`output/`).
> Es una buena idea usarlo para asegurarse que no haya datos viejos o basura que puedan contaminar el resultado.
> Pero hay que tener cuidado con borrar outputs que ya eran correctos.

## Correr sólo verificaciones

Sólo debe especificarse un subtópico con el número de entrega:
Algunos ejemplos válidos:

```python
python run.py --alias SUBTOP2
```


```python
python run.py -a SUBTOP2
```


```python
python run.py -s SUBTOP -e 2
```


```python
python run.py --subtopico SUBTOP --entrega 2
```

## Generar IDs

El parámetro `--index` genera sólo la tabla de IDs, `--exportar-definitivo` lo hace como uno de sus pasos.

```python
python run.py -a SUBTOP1 -i
```


```python
python run.py -a SUBTOP1 --index
```

## Cerrar un subtópico (pasar a definitivo)

La diferencia con `--index` es que acá remappea los `.csv` con los nombres correspondientes para que matcheen 1:1 gráfico:dataset.

```python
python run.py -a SUBTOP1 -d
```

```python
python run.py -a SUBTOP1 --exportar-definitivo
```

# QA

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

# Google Drive

[(Ver gwrappers/)](./argendata/utils/gwrappers/)

Como los datos se bajan desde Google Drive, usamos `pydrive` para interactuar con la correspondiente API. El programa espera que en `/.auth/` haya un archivo `client_secrets.json` para autenticar la sesión. Una vez autenticada, los datos de la sesión se guardan en `client_creds.json` en la misma carpeta.

Para simplificar (aún más) las interacciones que provee `pydrive`, [gwrappers](./argendata/utils/gwrappers/) provee clases para manipular los recursos de Google Drive como objetos.
