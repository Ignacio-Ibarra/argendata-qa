from logging import Logger

from src.gwrappers import GResource, GAuth, GDrive, GFolder
from src.logger import LoggerFactory
from src.verificador.subtopico import Subtopico
from src.verificador.verificadores import Test

ARGENDATA_FOLDER_ID = '16Out5kOds2kfsbudRvSoHGHsDfCml1p0'
VALID_NAMES = ["CAMCLI", "TRANEN", "CIETEC", "INVDES", "AGROPE", "COMEXT", "CRECIM", "DESHUM", "ESTPRO", "INDUST",
               "INVIED", "MINERI", "SEBACO", "DESIGU", "MERTRA", "POBREZ", "SALING", "ACECON", "BADEPA", "DEUDAS",
               "PRECIO"]


def main(log: Logger):
    auth = GAuth.authenticate()
    drive = GDrive(auth)

    Subtopico.from_name("TRANEN").verificar(Test)
