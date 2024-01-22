from typing import Generator, NamedTuple, Type
from pandas import DataFrame
from jinja2 import meta 
import jinja2 as jinja
import inspect
import os

Template = Type[NamedTuple]

class AbstractTemplate:
    u"""
    Clase base para la generación de clases que representan templates de Jinja.
    Todos los métodos que estén definidos acá los va a heredar cualquier clase que se
    cree con el decorador @Template.
    """
    def render(self, output=None) -> str:
        """
        Devuelve la string del render si no se especifica output. Sino, devuelve la ruta del output.
        """
        variables = {k: getattr(self, k) for k in self.__annotations__}

        with open(self.template) as f:
            template = jinja.Template(f.read())
        
        result = template.render(**variables)
        
        if not output:
            return result
        
        with open(output, 'w') as f:
            f.write(result)
        
        return output

    def __repr__(self):
        return f'{self.__class__.__name__}({self.template})'

def get_jinja_variables(folder: str, filename: str) -> set[str]:
    """Devuelve las variables que fueron declaradas en un template de jinja"""
    env = jinja.Environment(loader=jinja.FileSystemLoader(folder))
    template_source = env.loader.get_source(env, filename)[0]
    parsed_content = env.parse(template_source)
    return meta.find_undeclared_variables(parsed_content)

def get_defined_methods(klass) -> set[str]:
    """Devuelve los métodos definidos en una clase"""
    return set(attr for attr in dir(klass) if inspect.isfunction(getattr(klass, attr)))

def template(template_path: str) -> callable:
    u"""
    Anotación que tiene como objetivo definir los campos de una clase para que represente
    correctamente una template de Jinja. Usa 'template_path' para verificar que las variables
    de la clase estén definidas en el template (No chequea tipos).

    La clase resultante es el resultado de haber fabricado una NamedTuple con los campos
    y tipos declarados, junto con todos los métodos definidos en 'AbstractTemplate'.
    """
    def template_of(klass: type) -> Template:
        annotations: dict[str, type] = klass.__annotations__

        if not annotations:
            raise ValueError(f"Template '{klass.__name__}' of '{template_path}' has no annotations.")

        fields: list[tuple[str, type]] = [(k,v) for k,v in annotations.items()]

        if not (os.path.exists(template_path) and os.path.isfile(template_path)):
            raise ValueError(f"Template file '{template_path}' does not exist")

        folder, file = os.path.split(template_path)
        variables: set[str] = get_jinja_variables(folder, file)

        diff: set[str] = variables - set(annotations)

        if len(diff) > 0:
            diff_vars: Generator[str, None, None] = (f"'{x}'" for x in diff)
            diff_vars: str = ", ".join(diff_vars)
            error_str = f"Template variables {diff_vars} are not defined in "\
                          f"template '{klass.__name__}' of '{template_path}'"
            raise ValueError(error_str)

        result_klass: type = NamedTuple(klass.__name__, fields)

        result_klass.template: str = template_path

        # Esto es necesario porque NamedTuple no soporta multiple inheritance.
        for method in get_defined_methods(AbstractTemplate):
            setattr(result_klass, method, getattr(AbstractTemplate, method))

        # TODO: No sé si se puede definir esto como classmethod en AbstractTemplate sin romper nada.
        result_klass.from_dict = classmethod(lambda cls, d: cls(**d))

        return result_klass

    return template_of

