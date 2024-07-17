<div align="left">
<a href="https://fund.ar">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/56e7dede-1614-48c7-91e1-302194cc519d">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/4d21912a-0bdd-4dc0-9b66-caa8082ef91b">
    <img src="fund.ar" width="200"></img>
  </picture>
</a>
</div>

&nbsp;


<!--
<div align='center'>
 <img src="./assets/agd-0124.gif" alt=""></img>
</div>
-->

Esta etapa del proyecto tiene como objetivo validar la calidad de los datos de los analistas. Este repositorio contiene el código utilizado para relizar dicha verificación.
Los datos usados están compuestos por un CSV _crudo_ junto con una plantilla de metadatos, donde se especificaron distintos aspectos de cada dataset (Como por ejemplo,
qué columnas pueden tener nulos y cuales no). Luego, este programa corrobora que los datos cumplan con la especificación de metadatos.

Cada verificación genera un JSON que contiene toda la información técnica para luego mostrar un reporte en PDF utilizando [`pandoc`](https://pandoc.org/) 
en el cual se vuelcan todos los problemas encontrados.

Cuando los datos están correctos, se los puede "exportar como definitivos", eso genera y aplica etiquetas a cada dataset (Cambiando el nombre a un formato estándar: `TOPICO_gXX.csv`),
junto con el mapeo que se realizó (en formato JSON).

El funcionamiento de este código depende fuertemente de la organización de los archivos del proyecto: Se comunica con Google Drive para descargar los archivos, por lo que ejecutar este código sin el acceso
necesario resultará en un error.

# Uso

El proyecto cuenta con una interfaz mínima de consola con parámetros y ayuda para cambiar la funcionalidad:

![image](./assets/cli.png)

> [!CAUTION]
> Si pasamos `-C` o `--clean-first` se borra TODO el contenido del cache (`tmp/`) y de los resultados (`output/`).
> Es una buena idea usarlo para asegurarse que no haya datos viejos o basura que puedan contaminar el resultado.
> Pero hay que tener cuidado con borrar _outputs_ que ya eran correctos.

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

La sección de _**QA (Quality Assurance)**_ debe ejecutar una seria de controles para todos sus _datasets_. Los controles están estructurados de manera jerárquica, de forma tal que existen algunos de nivel superior que llaman a otros de nivel inferior.

Por ejemplo, los `Controles` de `Subtopicos`, llaman a `Controles` de `Archivo` para analizar `.csv`s (_Encoding_, _delimiter_), y `Controles` de `Consistencia` (Diferencias entre lo declarado en la plantilla y lo efectivo en un _dataset_).
Etc.

```
Subtopico
|
|\_Archivo
|
 \_Consistencia
 
 ...

```

El _entry point_ del programa de QA es 'main.py'. Ejecuta primero los tests unitarios y después el código.

<div>
<a href="https://fund.ar">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/datos-Fundar/fundartools/assets/86327859/6ef27bf9-141f-4537-9d78-e16b80196959">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/datos-Fundar/fundartools/assets/86327859/aa8e7c72-4fad-403a-a8b9-739724b4c533">
    <img src="fund.ar"></img>
  </picture>
</a>
</div>
