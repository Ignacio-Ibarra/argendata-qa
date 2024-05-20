from pandas import DataFrame, read_csv
from argendata.qa.subtopico import Subtopico
from argendata.utils import LoggerFactory
from argendata.utils.files import file as makedirs
from argendata.utils.gwrappers.resources import GResource, GFile, GFolder
from .remapper import *
import json
import csv

logger = LoggerFactory.getLogger("freeze")

def exportar_definitivo(subtopico_obj, nombre_subtopico: str, entrega: int, verificaciones_datasets: dict, csv_map: dict, ids = None):
    logger.info(f'Exportando {nombre_subtopico}{str(entrega)} como definitivo...')
    #subtopico_obj = Subtopico.from_name(nombre_subtopico, entrega)

    subtopico_obj.dataset: GFolder
    subtopico_obj.plantilla: DataFrame
    file: GFile

    if ids is None:
        ids, _, _ = remapper.generate_ids(nombre_subtopico, subtopico_obj.plantilla)

    # with open(mappings_file, 'w') as fp:
    #     mappings = {k:list(map(ids["ID Gráfico"].__getitem__,v)) for k,v in csv_map.items()}
    #     json.dump(mappings, indent=4, fp=fp)

    for file in subtopico_obj.dataset.resources:
        # check file class
        if not isinstance(file, GFile):
            logger.error(f"Skipping {file.name} as it is not a file")
            continue
        name = file.clean_title+file.extension
        name = name.strip()
        if any(invalid_format in name for invalid_format in ['.nc', '.geojson']):
            logger.error(f"Skipping {name} as it has an invalid format")
            continue

        path = file.download('./tmp/'+name)

        mappings = csv_map.get(name, None)

        if not mappings:
            logger.error(f"Skipping {name} as it has no mappings")
            continue

        for mapping in mappings:
            if any(invalid_format in name for invalid_format in ['.nc', '.geojson']):
                logger.error(f"Skipping {name} as it has an invalid format")
                continue

            pr_id, pb_id = mapping['private'], mapping['public']

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