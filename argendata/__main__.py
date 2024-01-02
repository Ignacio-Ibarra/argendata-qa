import argendata.qa as qa
from .utils.gwrappers import GAuth, GDrive

def main():
    auth = GAuth.authenticate()
    drive = GDrive(auth)

    qa.analyze('TRANEN')

if __name__ == "__main__":
    main()