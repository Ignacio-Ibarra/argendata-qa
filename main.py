from gwrappers import GResource, GAuth, GDrive, GFolder
from logger import LoggerFactory
from verificador.subtopicos import VerificadorSubtopico

ARGENDATA_FOLDER_ID = '16Out5kOds2kfsbudRvSoHGHsDfCml1p0'


if __name__ == "__main__":
    log = LoggerFactory.getLogger('main')
    auth = GAuth.authenticate()
    drive = GDrive(auth)

    root: GFolder = GResource.from_id(ARGENDATA_FOLDER_ID)
    subtopicos_folder = next(filter(lambda x: x.title == 'SUBTOPICOS', root.resources))

    root.to_json(recursive=False)

    # v_tranen = VerificadorSubtopico.from_name('TRANEN')
    # log.debug(v_tranen.carpetas)

    file = GResource.from_id('1x5TtZy_tFge5IW41qS1HSYIYL6JqBaXEjyd-2uPF48E')
    log.debug(file)

    file.copy_to('1HC_tFP_Hx7EfVZgbRXX0fGTpk-pQli0Y')    



#  def example():
#      log = LoggerFactory.getLogger('main')
#
#      auth = GAuth.authenticate()
#      drive = GDrive(auth)
#      file = GResource.from_id('1HOPNoKDprfZF7OC1X4Rlmr99WT5JKTmu')
#      folder = GResource.from_id('1C46wVxI4W2PMXmgqaIhEpKK27rhhBQxy')
#
#      GResource.create_and_upload('1WfnyLP5awozZdDhzBQAPB1a9AP_fdnvN',
#                                  {'mimeType': GResource.FOLDER_MIMETYPE,
#                                   'title': 'testing2'})
#
#      file.download(f'./tmp/{file.DEFAULT_FILENAME}')
