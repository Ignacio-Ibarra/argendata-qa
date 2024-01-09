import argendata.qa as qa
from .utils.gwrappers import GAuth, GDrive
from .utils.files import file
from .utils import timeformat, parse_time_arg
from datetime import datetime
import pprint
import json
import pytz

def main():
    auth = GAuth.authenticate()
    drive = GDrive(auth)
    
    subtopico = 'TRANEN'
    verificaciones = qa.analyze(subtopico)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(verificaciones)

    now_timestamp = timeformat(datetime.now(tz=pytz.timezone('America/Argentina/Buenos_Aires')))
    output_filename = './output/result-'+subtopico+"-"+now_timestamp+'.json'

    with open(file(output_filename), 'w') as fp:
        json.dump(obj=verificaciones, indent=4, fp=fp)

if __name__ == "__main__":
    main()