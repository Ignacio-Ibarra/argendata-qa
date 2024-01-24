import argendata.qa as qa
from subprocess import CalledProcessError
from .utils.gwrappers import GAuth, GDrive
from .utils.files import file
from .utils import timeformat
from datetime import datetime
import pandas as pd
import json
import pytz
from .utils.logger import LoggerFactory
from pandas import DataFrame
import pandas as pd
from argendata.reporter import Reporter
from argendata.reporter.pdfexport import pandoc_export
from argendata.freeze import generate_ids, autoajustar_columnas

def bold_fmt(s:str)->str:
    return f"**{s}**"

def wrap_string(string: str, max_length: int) -> str:
    if len(string) <= max_length:
        return string
    
    prefix_suffix_length = max_length - 3
    half_length = prefix_suffix_length // 2
    return string[:half_length+1] + '...' + string[-half_length:]


def make_table(df:DataFrame, bold_cols:bool = False, wrap_text:bool = False, wrapped_cols:list[str]|None = None, max_width:int|None = None)->DataFrame: 
    
    if wrap_text:
        for col in wrapped_cols:
            df[col] = df[col].apply(lambda s: wrap_string(s, max_length=max_width))

    df.columns = [bold_fmt(col) for col in df.columns]
    return df

def main(subtopico: str, entrega: int, generate_indices: bool):
    log = LoggerFactory.getLogger('main')
    auth = GAuth.authenticate()
    drive = GDrive(auth)

    verificaciones, subtopico_obj = qa.analyze(subtopico, entrega=entrega)
    now_timestamp = datetime.now(tz=pytz.timezone('America/Argentina/Buenos_Aires'))
    today_str = now_timestamp.strftime("%d/%m/%Y")

    verificaciones['fecha'] = today_str
    verificaciones['subtopico'] = subtopico

    outfile = subtopico+str(entrega)+"-"+timeformat(now_timestamp)
    outfile_path = f'./output/{subtopico+str(entrega)}/result-'+outfile+'.json'

    with open(file(outfile_path), 'w') as fp:
        json.dump(obj=verificaciones, indent=4, fp=fp)

    log.info(f'Reporte para {subtopico+str(entrega)} generado en {outfile_path}')

    report_generator = Reporter(subtopico, today_str, verificaciones)
    archivos = report_generator.generar_reporte(output_folder=f'./output/{subtopico+str(entrega)}/',
                                                merge_to=f"{outfile}.md")

    log.info("Generando reporte PDF...")
    export_result = pandoc_export(archivos[-1])
    if isinstance(export_result, Exception):
        log.error(f'Error al convertir a pdf')
        if isinstance(export_result, CalledProcessError):
            log.error(f"Error en el comando {' '.join(export_result.cmd)}")
            if getattr(export_result, 'stderr', None):
                stderr = export_result.stderr.decode().strip()
                for line in stderr.split('\n'):
                    log.error(line)
    else:
        log.info(f'PDF generado: {export_result}')
    
    if generate_indices:
        ids = generate_ids(subtopico, subtopico_obj.plantilla)
        pd.DataFrame(ids).to_excel(file(f'./output/{subtopico+str(entrega)}/{subtopico}.xlsx'), index=False)
        autoajustar_columnas(f'./output/{subtopico+str(entrega)}/{subtopico}.xlsx')


if __name__ == "__main__":
    main()