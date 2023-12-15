class Verificador:
    """Se encarga de ejecutar la pipeline de verificaciones."""

    resultado: dict
    """Tiene todas las claves de la salida.
       Es importante que se vayan llenando a medida que se ejecutan las verificaciones."""

    resultado = {
        'cant_datasets_decl': None,
        'cant_datasets_efvos': None,
        'cant_graf_errores': None,
        'cant_graficos': None,
        'cant_scripts_decl': None,
        'cant_scripts_declarados_no_cargados': None,
        'cant_scripts_efectivos_no_declarados': None,
        'cant_scripts_efvos': None,
        'cant_variables_no_cargadas': None,
        'cant_variables_no_declaradas': None,
        'cant_variables_verificadas': None,
        'columnas_con_nulos': None,
        'control_calidad': None,
        'datasets_a_verificar': None,
        'datasets_declarados_no_cargados': None,
        'datasets_efectivos_no_declarados': None,
        'encoding_delimiter_df': None,
        'fecha_verificacion': None,
        'graf_errores': None,
        'insepccion_fuentes': None,
        'scripts_declarados_no_cargados': None,
        'scripts_efectivos_no_declarados': None,
        'subtopico': None,
        'variables_no_cargadas': None,
        'variables_no_declaradas': None,
        'variables_tipo_dato_verificar': None
    }

    class Verificacion:
        """Wrapper de una verificacion ejecutable."""
        def __call__(self, *args, **kwargs):
            return self.__call__(*args, **kwargs)

        def __init__(self, other: callable):
            self.__dict__ = other.__dict__
            self.__name__ = other.__name__
            self.__call__ = other.__call__

        def __str__(self):
            return f"Verificacion({self.__name__})"

        def __repr__(self):
            return str(self)

    def __init__(self):
        ...
