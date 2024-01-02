# Verificador

Un `Verificador` es una clase que _verifica_ ciertas cualidades de una instancia de un objeto. Por ejemplo, un `Verificador` de (un) archivo puede asegurar que un archivo particular tenga un formato y/o encoding particular. Un verificador de (varios) archivos, puede asegurar que multiples archivos cumplan con la verificacion individual.

Los verificadores tienen la siguiente estructura:

```python
@Verifica[<clase_de_verficacion: str|type>, <prefijo: str>]
class <Nombre>:
    atributo_1: Any
    atributo2: Any
    ...

    def __init__(self, parametro_1, parametro_2, ...):
        self.atributo_1 = parametro_1
        self.atributo_2 = parametro_2
        ...

    def <prefijo><nombre>(self, <parametros>):
        ...
```

Y se usan así:

```python
<Nombre>(<nombre_instancia: str>, <parametro_1>, <parametro_2>, ...).verificar_todo()
```

Donde:

- `clase_de_verificacion` : Es una string o una clase (un tipo). Es el tipo de lo que se va a verificar.
- `prefijo` : Los métodos de la clase que empiecen con el prefijo, serán considerados como verificaciones a ejecutarse por `verificar_todo`.
- `Nombre` : Es el nombre de la clase que verifica `clase_de_verificacion`.

Especial atención en los parámetros. El `__init__` de la clase toma directamente los parámetros (la instancia a verificar + info del contexto, si aplica). Sin embargo, cuando se instancia la verificación, se pasa un nombre de instancia. Por ejemplo, si estamos verificando un archivo, se pasa el nombre del archivo. Ésto posibilita que luego, cuando se loggean las acciones, se pueda especificar exactamente qué se está verificando en un momento dado.

Los `parametros` de los métodos del verificador siempre comienzan con `self`, pero pueden incluír cualquiera de los `atributos` que se hayan definido en la clase. Si se indica un atributo como parámetro, en `verificar_todo` se pasará una referencia a dicho atributo, podiéndose usar así por el cuerpo del método.

> [!NOTE]
> Que los parámetros sean pasados por referencia implica que la única forma de
> modificarlos es mutándolos. Re-asignar un parámetro por referencia no tiene efecto
> (simplemente cambia el objeto al que apunta el mismo nombre).
> Por ejemplo, un ejemplo de mutación es usar `append()` sobre una lista.
> La muta, pero no la reasigna.

Los métodos de un verificador (las _verificaciones_) se ejecutan todas juntas con `verificar_todo()`. El resultado de `verificar_todo()` es un diccionario que mapea:

```
<nombre_de_verificacion> : <resultado>
```

Cada verificación puede devolver algo (o nada). En cualquier caso, genera una entrada en el diccionario del resultado. Si no devuelve nada, entonces se registra un `None` para esa verificación.

