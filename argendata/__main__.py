import argendata.qa as qa
from .utils.gwrappers import GAuth, GDrive
from .utils.files import file
from .utils import timeformat, parse_time_arg
from datetime import datetime
import pandas as pd
import pprint
import json
import pytz
import os
from .utils.logger import LoggerFactory
from .reporter import JinjaEnv

def generate_template(template_path: str, filepath: str):
    env = JinjaEnv(template_path)
    def curry_data(data):
        with open(filepath, 'w', encoding='utf-8') as fp:
            fp.write(env.template.render(data=data))
    return curry_data

def main():
    log = LoggerFactory.getLogger('main')
    auth = GAuth.authenticate()
    drive = GDrive(auth)
    
    subtopico = 'TRANEN'
    verificaciones = qa.analyze(subtopico, entrega=2)
    now_timestamp = datetime.now(tz=pytz.timezone('America/Argentina/Buenos_Aires'))
    today_str = now_timestamp.strftime("%d/%m/%Y")

    verificaciones['fecha'] = today_str
    verificaciones['subtopico'] = subtopico

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(verificaciones)

    output_filename = './output/result-'+subtopico+"-"+timeformat(now_timestamp)+'.json'

    with open(file(output_filename), 'w') as fp:
        json.dump(obj=verificaciones, indent=4, fp=fp)

    log.info(f'Reporte para {subtopico} generado en {output_filename}')

    # TODO:
    # Todo esto pertenece a otra parte del programa (quiza reporter_fachada, pero puede llamarse distinto)
    # Esta aca ahora para poder hacer los reportes. La logica se puede simplificar mucho, junto con cambiar
    # los outputs de las verificaciones para minimizar el tamaño del reporte crudo, y tambien minimizar
    # la cantidad de postprocesamiento (decompresion) de la info del mismo.

    gutter = {
        'subtopico' : subtopico,
        'fecha_verificacion' : today_str
    }

    string_errores_graficos = lambda es: f"{len(es)} errores graficos.' + '' if k == 0 else 'Graficos {', '.join(es)}"
    """'es' deberia ser una lista que contiene los numeros de grafico que tienen errores. Devuelve la string formateada."""

    filesystem_analysis_result = verificaciones['verificacion_sistema_de_archivos'][1]

    tabla_resumen_ = {
        'Datasets': list(map(len, filesystem_analysis_result['datasets'].values())),
        'Scripts' : list(map(len, filesystem_analysis_result['scripts'].values()))
    }

    tabla_resumen = pd.DataFrame(tabla_resumen_)

    datasets_declarados = set(filesystem_analysis_result['datasets']['declarados'])
    datasets_efectivos = set(filesystem_analysis_result['datasets']['efectivos'])

    scripts_declarados = set(filesystem_analysis_result['scripts']['declarados'])
    scripts_efectivos = set(filesystem_analysis_result['scripts']['efectivos'])

    tabla_datasets_no_declarados = pd.DataFrame({'Datasets no declarados': list(datasets_efectivos - datasets_efectivos)})
    tabla_datasets_no_cargados =   pd.DataFrame({'Datasets no cargados': list(datasets_declarados - datasets_efectivos)})

    tabla_scripts_no_declarados = pd.DataFrame({'Scripts no declarados': list(scripts_declarados - scripts_efectivos)})
    tabla_scripts_no_cargados   = pd.DataFrame({'Scripts no cargados': list(scripts_efectivos - scripts_efectivos)})

    resumen = {
        "string_errores_graficos" : "",
        "tabla_resumen" : tabla_resumen,
        "tabla_datasets_no_cargados" : tabla_datasets_no_cargados,
        "tabla_datasets_no_declarados" : tabla_datasets_no_declarados,
        "tabla_scripts_no_declarados" : tabla_scripts_no_declarados,
        "tabla_scripts_no_cargados" : tabla_scripts_no_cargados,
    }

    fuentes, instituciones = list(), list()
    for (fuente,institucion) in verificaciones['verificacion_fuentes']:
        fuentes.append(fuente)
        instituciones.append(institucion)

    fuentes = pd.DataFrame({'Fuente': fuentes, 'Institución': instituciones})


    resumenes_ds = list()
    ENCODINGS_VALIDOS = ('utf-8', 'UTF-8')
    for (k,v) in verificaciones['verificacion_datasets'].items():
        encoding = v['detected_encoding']
        delimiter = v['delimiter']

        if 'quality_checks' not in v.keys():
            quality_checks = quality_checks = {
                'tidy_data': 'Error',
                'duplicates': 'Error',
                'nullity_check': 'Error',
                'header': 'Error',
                'special_characters': 'Error',
                'tipo_datos': pd.DataFrame(),
                'detalle_caracteres_especiales': pd.DataFrame()
            }
            resumenes_ds.append(resumen_ds)
            continue

        quality_checks_ = v['quality_checks']
        quality_checks = {
                'tidy_data': 'OK' if quality_checks_['tidy_data'] else 'Es posible que no tenga formato Long, analizar archivo.',
                'duplicates': 'OK' if quality_checks_['duplicates'] else 'Mal.',
                'nullity_check': 'No se pudo realizar debido a un error.' if isinstance(quality_checks_['nullity_check'], tuple) else 'OK' if quality_checks_['nullity_check'] is True else 'Mal.',
                'header': 'OK' if quality_checks_['header'][0] is True else 'Mal.',
                'special_characters': 'OK' if quality_checks_['special_characters'][0] else 'Mal.',
                'tipo_datos': pd.DataFrame(),
                'detalle_caracteres_especiales': pd.DataFrame()
            }
        
        resumen_ds = {
            'nombre': k,
            'encoding': encoding,
            'encoding_resultado': 'OK' if encoding in ENCODINGS_VALIDOS else f"Mal. Tuvo que haber sido uno de estos: {', '.join(ENCODINGS_VALIDOS)}",
            'delimiter': delimiter,
            'delimiter_resultado': 'OK' if delimiter == ',' else f"Mal. El delimiter siempre debe ser ','",
            'qa': quality_checks
        }
        resumenes_ds.append(resumen_ds)

    params = [('./argendata/reporter/templates/template_gutter.md', file(f'./output/render-{subtopico}/gutter.md')),
                 ('./argendata/reporter/templates/template_resumen.md', file(f'./output/render-{subtopico}/resumen.md')),
                 ('./argendata/reporter/templates/template_inspeccion_fuentes.md', file(f'./output/render-{subtopico}/fuentes.md'))]
    
    for x in resumenes_ds:
        params.append(('./argendata/reporter/templates/template_dataset.md', file(f'./output/render-{subtopico}/'+x['nombre']+".md")))

    templates = list(map(lambda x: generate_template(*x), params))

    datos_template = [gutter, resumen, fuentes, *resumenes_ds]

    # O bien fs es functorialmente aplicativo sobre xs,
    # o bien uso una lista zippeable (Que es en si misma un functor aplicativo)
    for f,x in zip(templates, datos_template):
        f(x) # <*>


    with open(f'./output/render-{subtopico}/{subtopico}.md', 'w') as merged_file: [merged_file.write(open(file).read()) for file in map(lambda x: x[1], params) if os.path.isfile(file)]


    log.debug(len(datos_template))


if __name__ == "__main__":
    main()