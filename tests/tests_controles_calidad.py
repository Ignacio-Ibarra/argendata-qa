import unittest
from pandas import DataFrame
from argendata.qa.controles_calidad import controles, tiene_caracteres_raros

class TestControlesCalidad(unittest.TestCase):

    #  def test_tidy_data(self): ...
    
    #  def test_nullity_check(self): ...
    
    #  def test_duplicates(self): ...
    
    #  def test_header(self): ...

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
    
    #  def test_variables(self): ...

    def test_uninmplemented(self):
        uninmplemented = []

        for control in controles:
            if f'test_{control}' in dir(TestControlesCalidad):
                continue
            
            uninmplemented.append(control)

        self.assertEqual(len(uninmplemented), 0, f'Uninmplemented tests: {uninmplemented}')
