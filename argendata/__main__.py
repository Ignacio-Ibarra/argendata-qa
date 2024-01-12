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

def main(subtopico: str, entrega: int):
    log = LoggerFactory.getLogger('main')
    auth = GAuth.authenticate()
    drive = GDrive(auth)

    verificaciones = qa.analyze(subtopico, entrega=entrega)
    now_timestamp = datetime.now(tz=pytz.timezone('America/Argentina/Buenos_Aires'))
    today_str = now_timestamp.strftime("%d/%m/%Y")

    verificaciones['fecha'] = today_str
    verificaciones['subtopico'] = subtopico

    pp = pprint.PrettyPrinter(indent=4)
    #  pp.pprint(verificaciones)

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
        'subtopico' : subtopico, #ok
        'fecha_verificacion' : today_str #ok
    }


    # Armo data de Template Resumen. 
    cant_graficos, errores = verificaciones['verificacion_nivel_registro']

    string_errores_graficos = lambda es: f"{len(es)} errores graficos." + '' if len(es) == 0 else f"Graficos {', '.join(map(str, es))}"
    """'es' deberia ser una lista que contiene los numeros de grafico que tienen errores. Devuelve la string formateada."""

    filesystem_analysis_result = verificaciones['verificacion_sistema_de_archivos'][1]


    datasets_declarados = set(filesystem_analysis_result['datasets']['declarados'])
    datasets_efectivos = set(filesystem_analysis_result['datasets']['efectivos'])
    datasets_interseccion = set(filesystem_analysis_result['datasets']['interseccion'])
    datasets_no_declarados = list(datasets_efectivos - datasets_declarados)
    datasets_no_cargados  = list(datasets_declarados - datasets_efectivos)
    
    scripts_declarados = set(filesystem_analysis_result['scripts']['declarados'])
    scripts_efectivos = set(filesystem_analysis_result['scripts']['efectivos'])
    scripts_interseccion = set(filesystem_analysis_result['scripts']['interseccion'])
    scripts_no_declarados = list(scripts_efectivos - scripts_declarados)
    scripts_no_cargados   = list(scripts_declarados - scripts_efectivos)

    tabla_resumen_ = {
        'Datasets': list(map(len, [datasets_declarados, datasets_efectivos, datasets_interseccion, datasets_no_declarados, datasets_no_cargados])),
        'Scripts' : list(map(len, [scripts_declarados, scripts_efectivos, scripts_interseccion, scripts_no_declarados, scripts_no_cargados]))
    }

    tabla_resumen = pd.DataFrame(tabla_resumen_, index = ['Declarados', 'Efectivos', 'Interseccion', 'No declarados', 'No cargados'])

    if len(datasets_no_declarados) == 0: 
        tabla_datasets_no_declarados = pd.DataFrame({'Datasets no declarados': ['-']})
    else:
        tabla_datasets_no_declarados = pd.DataFrame({'Datasets no declarados': datasets_no_declarados})

    if len(datasets_no_cargados) == 0:
        tabla_datasets_no_cargados =   pd.DataFrame({'Datasets no cargados': ['-']})
    else:
        tabla_datasets_no_cargados =   pd.DataFrame({'Datasets no cargados': datasets_no_cargados})

    if len(scripts_declarados) == 0:
        tabla_scripts_no_declarados = pd.DataFrame({'Scripts no declarados': ['-']})
    else:
        tabla_scripts_no_declarados = pd.DataFrame({'Scripts no declarados': scripts_no_declarados})
    
    if len(scripts_no_cargados) == 0:
        tabla_scripts_no_cargados   = pd.DataFrame({'Scripts no cargados': ['-']})
    else:
        tabla_scripts_no_cargados   = pd.DataFrame({'Scripts no cargados': scripts_no_cargados})

    resumen = {
        'cant_graficos' : cant_graficos, #ok
        "string_errores_graficos" : string_errores_graficos(errores), #ok
        "tabla_resumen" : tabla_resumen, #ok
        "tabla_datasets_no_cargados" : tabla_datasets_no_cargados, #ok
        "tabla_datasets_no_declarados" : tabla_datasets_no_declarados, #ok
        "tabla_scripts_no_cargados" : tabla_scripts_no_cargados, #ok
        "tabla_scripts_no_declarados" : tabla_scripts_no_declarados #ok
        }

    # Armo data Insepeccion de Fuentes 
    fuentes, instituciones = list(), list()
    for (fuente,institucion) in verificaciones['verificacion_fuentes']:
        fuentes.append(fuente)
        instituciones.append(institucion)

    fuentes = pd.DataFrame({'Fuente': fuentes, 'Institución': instituciones})

    # TODO: falta traerse el output de verificación completitud para 
    # poder enchufarle a template_metadatos_incompletos.md

    # Armo datos para el template_dataset_titulo.md
    datasest_verificados_df = pd.DataFrame({'Datasets Verificados' : ['-']})
    if len(datasets_interseccion) > 0:
        datasest_verificados_df = pd.DataFrame({'Datasets Verificados' : list(datasets_interseccion)})
          



    resumenes_ds = list()
    ENCODINGS_VALIDOS = ('utf-8', 'UTF-8', 'utf_8')
    for (dataset_name,chequeos) in verificaciones['verificacion_datasets'].items():
        encoding = chequeos['detected_encoding']
        delimiter = chequeos['delimiter']

        resumen_ds = {
            'nombre': dataset_name,
            'encoding': encoding,
            'encoding_resultado': 'OK' if encoding in ENCODINGS_VALIDOS else f"Encoding inválido. Tuvo que haber sido uno de estos: {', '.join(ENCODINGS_VALIDOS)}",
            'delimiter': delimiter,
            'delimiter_resultado': 'OK' if delimiter == ',' else f"Delimiter inválido. El delimiter siempre debe ser ','",
        }

        ##  Armo data de los Datasets

        if 'quality_checks' not in chequeos.keys():
            quality_checks = {
                'tidy_data': 'Error',
                'duplicates': 'Error',
                'nullity_check': 'Error',
                'header': 'Error',
                'special_characters': 'Error',
                'tipo_datos': pd.DataFrame(),
                'detalle_caracteres_especiales': pd.DataFrame()
            }

            resumen_ds['qa'] = quality_checks
            resumenes_ds.append(resumen_ds)
            continue

        quality_checks_ = chequeos['quality_checks']

        # Tipo de dato
        
        variables = quality_checks_['variables']
        diferencia_simetrica : [list[list]] = variables[2]
        if len(diferencia_simetrica)>0:
            set_dif_simetrica = set(map(tuple, diferencia_simetrica))
            
            variables_efectivas : list[list] = variables[1]
            set_efectivo = set(map(tuple,variables_efectivas)) 
            efvo_dict = {k:v for k,v in variables_efectivas}

            mal_declarado = set_dif_simetrica - set_efectivo

            data = []
            for i, tupla in enumerate(mal_declarado):
                var_decl = tupla[0]
                dtype_decl = tupla[1]
                
                # Verificar si el valor está en lista_B
                if var_decl in efvo_dict:
                    dtype_efvo = efvo_dict[var_decl]
                    data.append( (var_decl, dtype_efvo, dtype_decl))
            
            tipo_dato_df = pd.DataFrame(data, columns = ['Variable Nombre','Tipo de Dato Efectivo', 'Tipo de Dato Declarado'])
        else:
            tipo_dato_df = pd.DataFrame([('-','-','-')], columns = ['Variable Nombre','Tipo de Dato Efectivo', 'Tipo de Dato Declarado'])

        # Caracteres especiales 
        caracters_ok, result =  quality_checks_['special_characters'] # acá el booleano quedó al revés, hay que arreglar en el codigo de verificadores. 

        thresh = 10

        data = []
        if not caracters_ok:
            for variable,sub_result in result.items():
                for string_error, idx_list in sub_result.items(): 
                    if len(idx_list)> thresh:
                        idx_str = f"Entre las filas {min(idx_list)} y {max(idx_list)}"
                    else:
                        idx_str = f"En las filas {', '.join(map(str,idx_list))}"
                    data.append((variable, string_error, idx_str))


            caracteres_especiales_df = pd.DataFrame(data, columns=['Variable Nombre', 'Cadena con caracteres especiales','Filas'])

        else: 
            caracteres_especiales_df = pd.DataFrame([('-','-','-')], columns=['Variable Nombre', 'Cadena con caracteres especiales','Filas'])
        
        quality_checks = {
                'tidy_data': 'No se pudo hacer debido a un error' if 'tidy_data' not in quality_checks_.keys() else 'OK' if quality_checks_['tidy_data'] else \
                    'Es posible que no tenga formato `long`, analizar archivo. Por favor completar [aquí]() si el dataset se encuentra o no'
                    'en formato `long` para poder tomarlo en cuenta en un futuro reporte. En caso de que esté en formato `wide` por favor corregir el archivo',
                'duplicates': 'No se pudo hacer debido a un error' if 'duplicates' not in quality_checks_.keys() else 'OK' if quality_checks_['duplicates'] else 'Se encontraron filas duplicadas en el dataset, para las variables definidas como claves.',
                'nullity_check': 'No se pudo realizar debido a un error.' if isinstance(quality_checks_['nullity_check'], tuple) else 'OK' if quality_checks_['nullity_check'] is True else 'Se encontraron valores nulos para las variables definidas como NOT NULLABLE',
                'header': 'OK' if quality_checks_['header'][0] is True else 'Se encontraron columnas con nombres mal formateados ver [documentación]((https://docs.google.com/document/d/1vH59Akk1eZTb0m4wIyEdhyVV_rx2q8lg4bG5k2tJP20/edit?usp=sharing))',
                'special_characters': 'OK' if quality_checks_['special_characters'][0] else 'Hay columnas que poseen caracteres raros, ver detalle abajo.',
                'tipo_datos': tipo_dato_df,
                'detalle_caracteres_especiales': caracteres_especiales_df
            }
        
        resumen_ds['qa'] = quality_checks
        resumenes_ds.append(resumen_ds)


    metadatos_incompletos_ = verificaciones['verificacion_sistema_de_archivos'][2]
    metadatos_incompletos = {
                'Dataset Archivo': ['-'],
                'Columna Plantilla': ['-'],
                'Filas Incompletas': ['-']
    }

    if len(metadatos_incompletos_.keys()) > 0:
        metadatos_incompletos = metadatos_incompletos_

    metadatos_incompletos = pd.DataFrame.from_dict(metadatos_incompletos)

    params = [('./argendata/reporter/templates/template_gutter.md', file(f'./output/render-{subtopico}/gutter.md')),
                 ('./argendata/reporter/templates/template_resumen.md', file(f'./output/render-{subtopico}/resumen.md')),
                 ('./argendata/reporter/templates/template_inspeccion_fuentes.md', file(f'./output/render-{subtopico}/fuentes.md')),
                 ('./argendata/reporter/templates/template_metadatos_incompletos.md', file(f'./output/render-{subtopico}/metinc.md')),
                 ('./argendata/reporter/templates/template_dataset_titulo.md', file(f'./output/render-{subtopico}/dataset_titulo.md'))]
    
    for x in resumenes_ds:
        params.append(('./argendata/reporter/templates/template_dataset.md', file(f'./output/render-{subtopico}/'+x['nombre']+".md")))

    templates = list(map(lambda x: generate_template(*x), params))

    datos_template = [gutter, resumen, fuentes, metadatos_incompletos, datasest_verificados_df, *resumenes_ds] 

    # O bien fs es functorialmente aplicativo sobre xs,
    # o bien uso una lista zippeable (Que es en si misma un functor aplicativo)
    for f,x in zip(templates, datos_template):
        f(x) # <*>


    with open(f'./output/render-{subtopico}/{subtopico}.md', 'w', encoding='utf-8') as merged_file: 
        [merged_file.write(open(file, encoding='utf-8').read()) for file in map(lambda x: x[1], params) if os.path.isfile(file)]


    log.debug(len(datos_template))



if __name__ == "__main__":
    main()