import argendata.qa as qa
from .utils.gwrappers import GAuth, GDrive

def main():
    auth = GAuth.authenticate()
    drive = GDrive(auth)

    verificaciones = qa.analyze('TRANEN')
    print(verificaciones)

if __name__ == "__main__":
    main()