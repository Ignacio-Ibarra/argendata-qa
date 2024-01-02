from unittest import TestCase
from argendata.qa import ControlSubtopico
from argendata.qa.verificaciones import *

class TestVerificacionNivelRegistro(TestCase):
    
    def test_distintos(self):
        df = pd.DataFrame({
            'orden_grafico': [1, 2, 3],
            'dataset_archivo': ['a', 'b', 'c'],
            'script_archivo': ['d', 'e', 'f'],
            'variable_nombre': ['g', 'h', 'i'],
            'url_path': ['j', 'k', 'l'],
            'fuente_nombre': ['m', 'n', 'o'],
            'institucion': ['p', 'q', 'r']
        })
        self.assertIsNone(ControlSubtopico.verificar_nivel_registro(df))

    def test_un_duplicado(self):
        df = pd.DataFrame({
            'orden_grafico': [1, 1, 2],
            'dataset_archivo': ['a', 'a', 'b'],
            'script_archivo': ['d', 'd', 'e'],
            'variable_nombre': ['g', 'g', 'h'],
            'url_path': ['j', 'j', 'k'],
            'fuente_nombre': ['m', 'm', 'n'],
            'institucion': ['p', 'p', 'q']
        })
        self.assertEqual(ControlSubtopico.verificar_nivel_registro(df), '1')

    def test_vacio(self):
        df = pd.DataFrame({
            'orden_grafico': [],
            'dataset_archivo': [],
            'script_archivo': [],
            'variable_nombre': [],
            'url_path': [],
            'fuente_nombre': [],
            'institucion': []
        })
        self.assertIsNone(ControlSubtopico.verificar_nivel_registro(df))

    def test_todos_duplicados(self):
        df = pd.DataFrame({
            'orden_grafico': [1, 1, 1],
            'dataset_archivo': ['a', 'a', 'a'],
            'script_archivo': ['d', 'd', 'd'],
            'variable_nombre': ['g', 'g', 'g'],
            'url_path': ['j', 'j', 'j'],
            'fuente_nombre': ['m', 'm', 'm'],
            'institucion': ['p', 'p', 'p']
        })
        self.assertEqual(ControlSubtopico.verificar_nivel_registro(df), '1')

    def test_multiples_duplicados(self):
        df = pd.DataFrame({
            'orden_grafico': [1, 2, 3, 1, 2, 3],
            'dataset_archivo': ['A', 'B', 'C', 'A', 'B', 'C'],
            'script_archivo': ['script_A', 'script_B', 'script_C', 'script_A', 'script_B', 'script_C'],
            'variable_nombre': ['var1', 'var2', 'var3', 'var1', 'var2', 'var3'],
            'url_path': ['url1', 'url2', 'url3', 'url1', 'url2', 'url3'],
            'fuente_nombre': ['fuente1', 'fuente2', 'fuente3', 'fuente1', 'fuente2', 'fuente3'],
            'institucion': ['inst1', 'inst2', 'inst3', 'inst1', 'inst2', 'inst3']
        })
        self.assertEqual(ControlSubtopico.verificar_nivel_registro(df), '1, 2, 3')


class TestVerificacionDatasets(TestCase):
    def setUp(self):
        self.template = pd.DataFrame({
            'dataset_archivo': ['file1', 'file2', 'file3', 'file1'],
            'variable_nombre': ['var1', 'var2', 'var3', 'var4'],
            'tipo_dato': ['entero', 'alfanumerico', 'entero', 'alfanumerico'],
            'primary_key': [True, False, True, False],
            'nullable': [False, True, False, True]
        })

    def test_todos_presentes(self):
        datasets = ['file1', 'file2', 'file3']
        result, intersection, _ = verificacion_datasets(self.template, datasets)
        self.assertTrue(result)
        self.assertEqual(intersection, set(datasets))

    def test_faltan_algunos(self):
        datasets = ['file1', 'file2']
        result, intersection, _ = verificacion_datasets(self.template, datasets)
        self.assertFalse(result)
        self.assertEqual(intersection, set(datasets))

    def test_sobran_algunos(self):
        datasets = ['file1', 'file2', 'file3', 'file4']
        result, intersection, _ = verificacion_datasets(self.template, datasets)
        self.assertFalse(result)
        self.assertEqual(intersection, set(['file1', 'file2', 'file3']))

class TestVerificacionScripts(TestCase):

    def test_ok(self):
        plantilla = pd.DataFrame({'script_archivo':['script1', 'script2', 'script3']})
        scripts = ['script1', 'script2', 'script3']
        self.assertEqual(verificacion_scripts(plantilla, scripts), (True, set(['script1', 'script2', 'script3'])))

    def test_faltan_algunos(self):
        plantilla = pd.DataFrame({'script_archivo':['script1', 'script2', 'script3']})
        scripts = ['script1', 'script3']
        self.assertEqual(verificacion_scripts(plantilla, scripts), (False, set(['script1', 'script3'])))

    def test_sobran_algunos(self):
        plantilla = pd.DataFrame({'script_archivo':['script1', 'script2']})
        scripts = ['script1', 'script2', 'script3']
        self.assertEqual(verificacion_scripts(plantilla, scripts), (False, set(['script1', 'script2'])))

    def test_faltan_todos(self):
        plantilla = pd.DataFrame({'script_archivo':['script1', 'script2', 'script3']})
        scripts = []
        self.assertEqual(verificacion_scripts(plantilla, scripts), (False, set()))

    def test_sobran_todos(self):
        plantilla = pd.DataFrame({'script_archivo':[]})
        scripts = ['script1', 'script2', 'script3']
        self.assertEqual(verificacion_scripts(plantilla, scripts), (False, set()))


class TestVerificacionVariables(TestCase):
    def setUp(self):
        self.declarados = pd.DataFrame({
            'dataset_archivo': ['file1', 'file1'],
            'variable_nombre': ['var1', 'var2'],
            'tipo_dato': ['float64', 'object']
        })

        self.filename = 'file1'

    def test_ok(self):
        df = pd.DataFrame({
            'var1': [1.0, 2.0, 3.0],
            'var2': ['a', 'b', 'c']
        })
        result = verificacion_variables(self.declarados, df, self.filename)
        self.assertTrue(result)

    def test_tipos_erroneos(self):
        df = pd.DataFrame({
            'var1': ["1", "2", "3"],
            'var2': ['a', 'b', 'c']
        })
        result = verificacion_variables(self.declarados, df, self.filename)
        self.assertFalse(result)

    def test_variables_erroneas(self):
        df = pd.DataFrame({
            'var1': ["1", "2", "3"],
            'var3': ['a', 'b', 'c']
        })
        result = verificacion_variables(self.declarados, df, self.filename)
        self.assertFalse(result)


class TestVerificacionCompletitud(TestCase):
    def setUp(self):
        self.plantilla = pd.DataFrame({
            'dataset_archivo': ['file1', 'file2', 'file3', 'file1', 'file2'],
            'seccion_desc': ['desc1', 'desc2', None, 'desc4', 'desc5'],
            'nivel_agregacion': ['aggr1', 'aggr2', 'aggr3', 'aggr4', 'aggr5'],
            'unidad_medida': ['med1', 'med2', 'med3', 'med4', 'med5'],
            'other_column': [None, 'value2', 'value3', None, 'value5']
        })
        self.interseccion = {'file1', 'file2'}

    def test_vacio(self):
        empty_df = pd.DataFrame()
        self.assertRaises(AttributeError, lambda: ControlSubtopico.verificar_completitud(empty_df, self.interseccion))

    def test_plantilla_vacia(self):
        plantilla = pd.DataFrame({
            'dataset_archivo': [],
            'seccion_desc': [],
            'nivel_agregacion': [],
            'unidad_medida': [],
            'other_column': []
        })
        result = ControlSubtopico.verificar_completitud(plantilla, self.interseccion)
        self.assertTrue(result.empty)

    def test_interseccion_vacia(self):
        interseccion = {'file4', 'file5'}
        result = ControlSubtopico.verificar_completitud(self.plantilla, interseccion)
        self.assertTrue(result.empty)

    def test_ok(self):
        plantilla = self.plantilla.copy()
        plantilla.fillna('value', inplace=True)
        result = ControlSubtopico.verificar_completitud(plantilla, self.interseccion)
        self.assertTrue(result.empty)

    def test_filas_incompletas(self):
        expected_output = pd.DataFrame({
            'dataset_archivo': ['file1'],
            'columna_plantilla': ['other_column'],
            'filas_incompletas': [2]
        })
        result = ControlSubtopico.verificar_completitud(self.plantilla, self.interseccion)
        self.assertTrue(result.equals(expected_output))