import jinja2 as jinja
from jinja2 import meta
import re
import os
import sys

def get_jinja_variables(folder: str, filename: str) -> set[str]:
    """Devuelve las variables que fueron declaradas en un template de jinja"""
    env = jinja.Environment(loader=jinja.FileSystemLoader(folder))
    template_source = env.loader.get_source(env, filename)[0]
    parsed_content = env.parse(template_source)
    return meta.find_undeclared_variables(parsed_content)

def generate_template_class(template_path):
    folder, file = os.path.split(template_path)
    variables = get_jinja_variables(folder, file)
    
    valid_chars = re.compile(r'[a-zA-Z_]')
    point_index = file.rfind('.')
    clean_name = file[:point_index]
    clean_name = filter(valid_chars.match, clean_name)
    clean_name = "".join(clean_name)
    clean_name = clean_name.replace('_', ' ').title().replace(' ', '')
    
    result = f"@Template('./{template_path}')"
    result += f"\nclass {clean_name}:"

    for var in variables:
        result += f"\n    {var}: ..."

    return result

def main(args):
    if len(args) < 2:
        print("Not enough arguments.")
        print("Usage: python templateclass.py <template.md> [optional: output.py]")
        sys.exit(1)
    
    path = args[1]
    
    result = generate_template_class(path)

    if len(args) > 2:
        outfile = args[2]
        if not outfile[-3:] == '.py':
            outfile += '.py'

        with open(outfile, 'w') as f:
            f.write(result)
    else:
        print(result)

    exit(0)

if __name__ == "__main__":
    args = sys.argv
    main(args)
    