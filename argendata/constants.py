from dotenv import dotenv_values

ARGENDATA_FOLDER_ID = ''
def get_argendata_folder_id():
    ARGENDATA_FOLDER_ID = dotenv_values()['ARGENDATA_FOLDER_ID']
    return ARGENDATA_FOLDER_ID

VALID_NAMES = ["CAMCLI", "TRANEN", "CIETEC", "INVDES", "AGROPE", "COMEXT", "CRECIM", "DESHUM", "ESTPRO", "INDUST",
               "INVIED", "MINERI", "SEBACO", "DESIGU", "MERTRA", "POBREZ", "SALING", "ACECON", "BADEPA", "DEUDAS",
               "PRECIO"]


def carpeta_subtopico(nombre):
    return f'ArgenData - {nombre}'