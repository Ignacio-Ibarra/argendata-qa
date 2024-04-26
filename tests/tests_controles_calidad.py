import unittest
from pandas import DataFrame
from argendata.qa.controles_calidad import (
    controles, 
    tiene_caracteres_raros, 
    check_wrong_colname,
    is_tidy
)

class TestControlesCalidad(unittest.TestCase):

    #  def test_tidy_data(self): ...
    
    #  def test_nullity_check(self): ...
    
    #  def test_duplicates(self): ...

    # ['nullity_check', 'duplicates', 'variables']

    def test_check_wrong_colname(self):
        valid_colnames = ['abc', 'anio', 'abc1']
        invalid_colnames = ['1abc', 'año', '1995', 'a bc', '', ' ']

        for colname in valid_colnames:
            self.assertFalse(check_wrong_colname(colname), f'Fallo en {colname}')
        
        for colname in invalid_colnames:
            self.assertTrue(check_wrong_colname(colname), f'Falló en {colname}')

    
    def test_header(self): ...
    def test_tiene_caracteres_raros(self):
        valid_words = ['Hello', 'world', 'áéíóú', 'üñôç', 'ÁÉÍÓÚ', 'ÜÑÇ', '123', 'hello_world', '(hello, world)']
        invalid_words = ['Hello@', 'world#', 'áéíóú$', '%üñôç', '&ÁÉÍÓÚ', '*ÜÑÇ', '123^', 'hello_world!', '(hello, world)%']

        for word in valid_words:
            self.assertFalse(tiene_caracteres_raros(word))

        for word in invalid_words:
            self.assertTrue(tiene_caracteres_raros(word))
    
    def test_special_characters(self):
        test_cases = []

        with_special_chars = DataFrame({
                'column1': ['hello', 'world', 'test'],
                'column2': ['hello@', 'world#', 'test$'],
                'column3': [1, 2, 3]
        })

        with_special_chars_expected = (False, {'column2': {'hello@': [0], 'world#': [1], 'test$': [2]}})
        test_cases.append((with_special_chars, with_special_chars_expected))

        without_special_chars = DataFrame({
                'column1': ['hello', 'world', 'test'],
                'column2': ['hello', 'world', 'test'],
                'column3': [1, 2, 3]
        })
        
        without_special_chars_expected = (True, {})
        test_cases.append((without_special_chars, without_special_chars_expected))

        # Run all testcases
        for data, expected in test_cases:
            result = controles['special_characters'](data)
            self.assertEqual(result, expected)
    
    def test_tidy_data(self):

        df1 = DataFrame({
            'col1': ['a', 'b', 'c', 'd'],
            'val1': [1, 2, 3, 4]
        })

        df2 = DataFrame({
            'col1': ['a', 'b', 'c', 'd'],
            'col2': ['a', 'b', 'c', 'd'],
            'val1':  [1, 2, 3, 4]
        })

        cases = [
            ({
                'data': df1,
                'keys': ['col1', 'val1']
            },
            True),

            ({
                'data': df2,
                'keys': ['col1']
            },
            False)
        ]

        for case, expected in cases:
            self.assertEqual(is_tidy(**case), expected)
    
    #  def test_variables(self): ...
    #  class TestVerificacionVariables(TestCase):
    #      def setUp(self):
    #          self.declarados = pd.DataFrame({
    #              'dataset_archivo': ['file1', 'file1'],
    #              'variable_nombre': ['var1', 'var2'],
    #              'tipo_dato': ['float64', 'object']
    #          })
    #  
    #          self.filename = 'file1'
    #  
    #      def test_ok(self):
    #          df = pd.DataFrame({
    #              'var1': [1.0, 2.0, 3.0],
    #              'var2': ['a', 'b', 'c']
    #          })
    #          result = ControlSubtopico.verificar_variables(self.declarados, df, self.filename)
    #          self.assertTrue(result)
    #  
    #      def test_tipos_erroneos(self):
    #          df = pd.DataFrame({
    #              'var1': ["1", "2", "3"],
    #              'var2': ['a', 'b', 'c']
    #          })
    #          result = ControlSubtopico.verificar_variables(self.declarados, df, self.filename)
    #          self.assertFalse(result)
    #  
    #      def test_variables_erroneas(self):
    #          df = pd.DataFrame({
    #              'var1': ["1", "2", "3"],
    #              'var3': ['a', 'b', 'c']
    #          })
    #          result = ControlSubtopico.verificar_variables(self.declarados, df, self.filename)
    #          self.assertFalse(result)

    def test_uninmplemented(self):
        uninmplemented = []

        for control in controles:
            if f'test_{control}' in dir(TestControlesCalidad):
                continue
            
            uninmplemented.append(control)

        self.assertEqual(len(uninmplemented), 0, f'Uninmplemented tests: {uninmplemented}')
