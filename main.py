from logging import Logger

from gwrappers import GResource, GAuth, GDrive, GFolder
from logger import LoggerFactory
from verificador.subtopicos import VerificadorSubtopico

ARGENDATA_FOLDER_ID = '16Out5kOds2kfsbudRvSoHGHsDfCml1p0'
VALID_NAMES = ["CAMCLI", "TRANEN", "CIETEC", "INVDES", "AGROPE", "COMEXT", "CRECIM", "DESHUM", "ESTPRO", "INDUST",
               "INVIED", "MINERI", "SEBACO", "DESIGU", "MERTRA", "POBREZ", "SALING", "ACECON", "BADEPA", "DEUDAS",
               "PRECIO"]

def main(log: Logger):
    auth = GAuth.authenticate()
    drive = GDrive(auth)

    for subtopico in VALID_NAMES[:10]:
        Subtopico.from_name(subtopico).verificar(Test)

if __name__ == "__main__":
    log = LoggerFactory.getLogger('main')
    try:
        main(log)
    except KeyboardInterrupt:
        logg