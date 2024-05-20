import unittest

class TestGeonomencladores(unittest.TestCase):

    def test_no_info_geografica(self):
        cases = [
            ({'valor1': [1,2,3,4], 'valor2': ['a', 'b', 'c', 'd']},
             None),
        ]

        for case, expected in cases:
            self.assertEqual(expected, expected)
    
    def test_cod(self):
        cases = [
            ({'iso3': ['ARG']},
             True),

            ({'iso': ['ARG']},
            True),

            ({'codigo_fundar': ['ARG']},
             True)
        ]

        for case, expected in cases:
            self.assertEqual(expected, expected)
    
    def test_desc(self):
        cases = [
            ({'region': ['Argentina']},
             True),

            ({'countryname': ['República Argentina']},
            True),

            ({'pais': ['Argentina (República)']},
             True)
        ]

        for case, expected in cases:
            self.assertEqual(expected, expected)
    
    def test_cod_desc(self):
        cases = [
            ({'region': ['Argentina'], 'code': ['ARG']},
             True),

            ({'countryname': ['República Argentina'], 'iso3': ['ARG']},
            True),

            ({'pais': ['Argentina (República)'], 'region_code': ['ARG']},
             True)
        ]

        for case, expected in cases:
            self.assertEqual(expected, expected)
    
    def test_2cod_2desc(self):
        cases = [
            ({'region1': ['Argentina'], 'code1': ['ARG'],
              'region2': ['Argentina'], 'code2': ['ARG']},
             True),
        ]

        for case, expected in cases:
            self.assertEqual(expected, expected)
    
    def test_n_cod_m_desc(self):
        cases = [
            ({'region1': ['Argentina'], 'code1': ['ARG'],
              'region2': ['Argentina'], 'code2': ['ARG'],
              'region3': ['Argentina']},
             True),

             ({'region1': ['Argentina'], 'code1': ['ARG'],
              'region2': ['Argentina'], 'code2': ['ARG'],
              'code3': ['ARG']},
             True),
        ]

        for case, expected in cases:
            self.assertEqual(expected, expected)