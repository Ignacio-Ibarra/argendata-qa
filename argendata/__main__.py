import argendata.qa as qa
from .utils.gwrappers import GAuth, GDrive
import pprint

def main():
    auth = GAuth.authenticate()
    drive = GDrive(auth)

    verificaciones = qa.analyze('TRANEN')
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(verificaciones)

if __name__ == "__main__":
    main()