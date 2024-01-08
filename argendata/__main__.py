import argendata.qa as qa
from .utils.gwrappers import GAuth, GDrive
from .utils import timeformat, parse_time_arg
from datetime import datetime
import pprint
import json
import pytz

def main():
    auth = GAuth.authenticate()
    drive = GDrive(auth)

    verificaciones = qa.analyze('TRANEN')
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(verificaciones)

    with open('result-'+timeformat(datetime.now(tz=pytz.timezone('America/Argentina/Buenos_Aires')))+'.json', 'w') as fp:
        json.dump(obj=verificaciones, indent=4, fp=fp)

if __name__ == "__main__":
    main()