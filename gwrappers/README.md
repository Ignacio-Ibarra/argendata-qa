<div align="center">
    <h1>GWrappers</h1>
    Wrappers de los wrappers de pydrive
</div>

---

La motivación de este módulo es que sea (aún) más sencillo manejarse con los archivos de Google Drive.

Uso:

```python
auth = GAuth.authenticate()
drive = GDrive(auth)
file = GResource.from_id('1HOPNoKDprfZF7OC1X4Rlmr99WT5JKTmu')

folder = GResource.from_id('1C46wVxI4W2PMXmgqaIhEpKK27rhhBQxy')

GResource.create_and_upload('1WfnyLP5awozZdDhzBQAPB1a9AP_fdnvN',
                            {'mimeType': GResource.FOLDER_MIMETYPE,
                             'title': 'testing2'})

file.download(f'./tmp/{file.DEFAULT_FILENAME}')
```

# Autenticación - GAuth

Para agilizar la autenticación, `GAuth` y `GDrive` son clases Singleton (se las puede instanciar sólo una vez).
Luego, proveen métodos `get_instance()` para obtener la instancia (ya instanciada, valga la redundancia).

De ésta manera, es más limpio obtener las instancias autenticadas desde los `GResources`.


# Recursos - GResource

La idea es tratar a los archivos de Google Drive como objetos.
Para unificar 'archivos' y 'carpetas', en este módulo, a dicha unión se la llama 'recurso'.
Un 'recurso' es simplemente algo que está subido a Google Drive.

En memoria, un recurso podría estar definido simplemente por (título, id, mimeType), aunque realmente
podría ser simplemente el ID, pues identifica unívocamente al archivo, pero el título y el mimeType son ayudas
prácticas para nosotros (humanos). Luego, cualquier operación se puede hacer en función de esa información.

En la práctica, si no se especifican los metadatos al pedir un recurso por ID, el comportamiento
predeterminado es que traiga todos los metadatos (`GResource.from_id(metadata='all)'`)

# Árbol de Sistema de Archivos - FSTree (To-Do)

De la misma manera, el árbol del sistema de archivos (A partir de ahora 'FSTree', significando 'File System Tree'),
puede ser un árbol que sólo contenga las IDs de los recursos. Para fines de búsqueda e iteración, es mejor tener una copia local del 
FSTree del drive, en vez de hacer solicitudes. Dada la posibilidad de mirar la última fecha-hora de modificación 
de un recurso, el árbol puede actualizarse localmente para estar actualizado.

Actualmente la única funcionalidad que guarda un árbol de IDs está en `GFolder.as_dict()` (y `.to_json()` 
que usa internamente el método anterior). Genera un diccionario de diccionarios si se pasa el parámetro `recursive=True`.

