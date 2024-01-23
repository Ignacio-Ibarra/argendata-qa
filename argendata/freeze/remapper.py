import pandas as pd

def clase_eq(nombre: str, plantilla: pd.DataFrame) -> dict: # [[id_privada: str], [id: str, ... str]]
    """
    Toma una plantilla y asigna IDs a los gráficos. Los agrupa por fila (según ciertas columnas) y asigna dos
    IDs, una 'privada' (compuesta por los numeros de 'subtopico_desc' y 'orden_grafico') y una 'publica'
    que es 'SUBTOP_gX' con X siendo el índice de la fila en el conteo post-unique.
    """
    control = dict()

    last_added = 1
    for subtopico_desc, orden_grafico, titulo_grafico, dataset_archivo, url_path, fuente_nombre, institucion in plantilla[['subtopico_desc', 'orden_grafico', 'titulo_grafico', 'dataset_archivo', 'url_path', 'fuente_nombre', 'institucion']].iloc:
        enum_index = subtopico_desc.rfind('.')
        subtopico_desc = subtopico_desc[:enum_index]
        subtopico_desc = subtopico_desc.replace('.', '-')
        
        pr_id = f"{nombre}_{subtopico_desc}_{orden_grafico}"

        if pr_id not in control.keys():
            control[pr_id] = (f'{nombre}_g{last_added}', titulo_grafico, dataset_archivo, url_path, [])
            last_added += 1
            
    
    return control

def clase_eq_df(d: dict):
    """
    Convierte un diccionario de tipo 'id_privada': ('id_gX', ...)
    a un diccionario de tipo 'id_gX': ('id_privada', ...)
    Y lo devuelve como DataFrame para ser exportado como xlsx
    """
    flip = {v[0]:(k, *v[1:]) for k,v in d.items()} # Cambio la clave
    df = pd.DataFrame(flip, index=['ID Privada','Nombre Gráfico','Nombre Dataset','Fuente URL','Fuente Nombre','Fuente Institución'])
    return df.T