import pandas as pd
from pandas.core.series import Series
import openpyxl

def cell_notna(x: openpyxl.cell.cell.Cell):
    return x.value is not None

def cell_length(x: openpyxl.cell.cell.Cell):
    return len(str(x.value))

def autoajustar_columnas(workbook_path: str, MAX_LEN: int = 100):
    wb = openpyxl.load_workbook(filename = workbook_path)        
    for name in wb.sheetnames:
        worksheet = wb[name]
        for col in worksheet.columns:
            column = col[0].column_letter
            max_len = max(map(cell_length, filter(cell_notna, col)))
            adjusted_width = (max_len + 2) * 1.2
            adjusted_width = min(adjusted_width, MAX_LEN)
            worksheet.column_dimensions[column].width = adjusted_width
    wb.save(workbook_path)

def clean_fuentes(x: str):
    return x.strip().replace(';', ',')

def formato_fuentes(x):
    fuente, institucion = x
    return f'{fuente} - {institucion}'

def generate_ids(subtopico: str, plantilla: pd.DataFrame):
    output = {
        'ID Gráfico': {},
        'Estilo': {},
        'Titulo': {},
        'Subtitulo': {},
        'Eje X': {},
        'Eje Y': {},
        'Nota': {},
        'Referencia': {},
        'Observaciones': {},
        'csv': {},
        'Fuentes': {},
    }

    for i, ((n, g), group) in enumerate(plantilla.groupby(['subtopico_desc', 'orden_grafico'])):
        j = i+1
        point_index = n.rfind('.')
        n = n[:point_index]
        n = n.replace('.', '-')
        result = f'{subtopico}_{n}_{g}'
        index = f'{subtopico}_g{j}'

        dataset_archivo: Series = group['dataset_archivo']
        dataset_archivo: str = dataset_archivo.iloc[0] # Asumo 1:1 grafico:dataset

        fuentes = group[['fuente_nombre', 'institucion']].to_records(index=False)
        
        fuentes_r = set(map(lambda x: tuple(map(clean_fuentes, x)), fuentes))
        fuentes_r = '; '.join(map(formato_fuentes, fuentes_r))

        output['ID Gráfico'][result] = index
        output['Fuentes'][result] = fuentes_r
        output['csv'][result] = dataset_archivo

        for k in set(output) - {'ID Gráfico', 'Fuentes', 'csv'}:
            output[k][result] = ''
    
    return output
