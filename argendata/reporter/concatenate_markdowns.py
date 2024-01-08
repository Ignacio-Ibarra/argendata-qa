import shutil


def key_to_file(key:str)->str:
    """Toma una clave y retorna el nombre del archivo correspondiente.

    Args:
        key (str): Nombre del tipo de template

    Returns:
        str: 'template_'+key+'.md' 
    """
    return f"template_{key}.md"


class ConcatenateMarkdowns:

    def __init__(self, template_keys:list[str], markdown_folder:str, output_report_file:str):

        self.used_templates =  [markdown_folder + "/" + key_to_file(x) for x in template_keys]
    
