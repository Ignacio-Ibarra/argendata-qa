from pandas import DataFrame, read_csv
from argendata.qa.subtopico import Subtopico
from argendata.utils import LoggerFactory
from argendata.utils.files import file as makedirs
from argendata.utils.gwrappers.resources import GResource, GFile, GFolder
from .remapper import *
import csv

logger = LoggerFactory.getLogger("freeze")

def exportar_definitivo(nombre_subtopico: str, entrega: int, verificaciones_datasets: dict):
    logger.info(f'Exportando {nombre_subtopico}{str(entrega)} como definitivo...')
    subtopico = Subtopico.from_name(nombre_subtopico, entrega)

    subtopico.dataset: GFolder
    subtopico.plantilla: DataFrame
    file: GFile

    ids = remapper.generate_ids(nombre_subtopico, subtopico.plantilla)
    csv_map = {v.strip():k for k,v in ids['csv'].items()}

    for file in subtopico.dataset.resources:
        path = file.download('./tmp/'+file.clean_title+file.extension)
        pr_id = csv_map[file.clean_title+file.extension]
        pb_id = ids['ID Gráfico'][pr_id]
        verificacion = verificaciones_datasets[file.clean_title+file.extension]
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