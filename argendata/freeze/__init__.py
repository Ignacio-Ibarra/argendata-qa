from pandas import DataFrame, read_csv
from argendata.qa.subtopico import Subtopico
from argendata.utils import LoggerFactory
from argendata.utils.files import file as makedirs
from argendata.utils.gwrappers.resources import GResource, GFile, GFolder
from .remapper import *
import json
import csv

logger = LoggerFactory.getLogger("freeze")

def exportar_definitivo(nombre_subtopico: str, entrega: int, verificaciones_datasets: dict, ids = None):
    logger.info(f'Exportando {nombre_subtopico}{str(entrega)} como definitivo...')
    subtopico = Subtopico.from_name(nombre_subtopico, entrega)

    subtopico.dataset: GFolder
    subtopico.plantilla: DataFrame
    file: GFile

    if ids is None:
        ids = remapper.generate_ids(nombre_subtopico, subtopico.plantilla)

    csv_map = dict()
    for k,v in ids['csv'].items():
        csv_map.setdefault(v.strip(), []).append(k)
    
    mappings_file = \
        makedirs(f'./output/{nombre_subtopico}{entrega}/definitivos/mappings.json')

    with open(mappings_file, 'w') as fp:
        mappings = {k:list(map(ids["ID Gráfico"].__getitem__,v)) for k,v in csv_map.items()}
        json.dump(mappings, indent=4, fp=fp)

    for file in subtopico.dataset.resources:
        name = file.clean_title+file.extension
        path = file.download('./tmp/'+name)
        
        pr_ids = csv_map[name]

        for pr_id in pr_ids:
            pb_id = ids['ID Gráfico'][pr_id]

            logger.info(f"Mapping {name} -> {pr_id} <-> {pb_id}")
            
            verificacion = verificaciones_datasets[name]
            encoding, delimiter = verificacion['detected_encoding'], verificacion['delimiter']

            df = read_csv(path, encoding=encoding, delimiter=delimiter)
            df.to_csv(makedirs(f'./output/{nombre_subtopico}{entrega}/definitivos/{pb_id}.csv'),
                    encoding='utf-8',
                    sep=',',
                    quoting=csv.QUOTE_ALL,
                    quotechar='"',
                    lineterminator='\n',
                    decimal='.',
                    index=False)