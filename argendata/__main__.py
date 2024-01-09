import argendata.qa as qa
from .utils.gwrappers import GAuth, GDrive
from .utils.files import file
from .utils import timeformat, parse_time_arg
from datetime import datetime
import pprint
import json
import pytz
from .utils.logger import LoggerFactory

def main():
    log = LoggerFactory.getLogger('main')
    auth = GAuth.authenticate()
    drive = GDrive(auth)
    
    subtopico = 'MINERI'
    verificaciones = qa.analyze(subtopico, entrega=1)
    now_timestamp = datetime.now(tz=pytz.timezone('America/Argentina/Buenos_Aires'))
    today_str = now_timestamp.strftime("%d/%m/%Y")

    verificaciones['fecha'] = today_str
    verificaciones['subtopico'] = subtopico

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(verificaciones)

    output_filename = './output/result-'+subtopico+"-"+timeformat(now_timestamp)+'.json'

    with open(file(output_filename), 'w') as fp:
        json.dump(obj=verificaciones, indent=4, fp=fp)

    log.info(f'Reporte para {subtopico} generado en {output_filename}')

if __name__ == "__main__":
    main()