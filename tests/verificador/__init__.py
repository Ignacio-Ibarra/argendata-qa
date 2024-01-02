from typing import Iterable

from src.verificador.abstracto import Verifica
from src.utils import Final, Attribute
from unittest import TestCase


@Verifica["blabla"]
class VerificadorStrings:
    a_verificar: str
    caracteres: Iterable[str]

    def __init__(self, a_verificar: str, caracteres):
        self.a_verificar = a_verificar
        self.caracteres = caracteres

    def verificar_a(self, a_verificar: Final[Attribute[str]]):
        return a_verificar == 'a'

    def verificar_len(self, a_verificar: Final[Attribute[str]]):
        return len(a_verificar) > 1

    def verificar_conteo_caracteres(self, a_verificar: Final[Attribute[str]],
                                    caracteres: Final[Attribute[Iterable[str]]]):

        return [a_verificar.count(c) for c in caracteres]

    def verificar_modificar_caracteres(self, caracteres: Final[Attribute[Iterable[str]]]):
        caracteres += 'abc'
        return self.caracteres

    def verificar_conteo_postmutacion(self, a_verificar, caracteres: Final[Attribute[Iterable[str]]]):
        return [a_verificar.count(c) for c in caracteres]

    def verificar_nada(self):
        return 1+1


class VerificadorStringTestsEstaticos(TestCase):
    test: Verifica

    @classmethod
    def setUpClass(cls):
        cls.test = VerificadorStrings

    def test_ClassName(self):
        self.assertEqual(self.test.__name__, 'VerificadorStrings')

    def test_SpecializationName(self):
        self.assertEqual(self.test.__specialization_classname__, "blabla")

    def test_Verificaciones(self):
        verificaciones = self.test._verificaciones
        self.assertEqual(list(verificaciones.keys()),
                         ["verificar_a", "verificar_len",
                          "verificar_conteo_caracteres", "verificar_modificar_caracteres",
                          'verificar_conteo_postmutacion', 'verificar_nada'])


class VerificadorStringTestsDinamicos(TestCase):
    test: Verifica

    @classmethod
    def setUpClass(cls):
        cls.test = VerificadorStrings('myString', # a_verificar alias
                                      'abc', # a_verificar
                                      ['c', 'd']) # extra params: 'caracteres'

    def test_ClassName(self):
        self.assertEqual(self.test.__class__.__name__, 'VerificadorStrings')

    def test_SpecializationName(self):
        self.assertEqual(self.test.__class__.__specialization_classname__, "blabla")

    def test_name(self):
        self.assertEqual(self.test.name, 'myString')

    def test_verificaciones(self):
        expected = {'verificar_a': False,
                    'verificar_len': True,
                    'verificar_conteo_caracteres': [1, 0],
                    'verificar_modificar_caracteres': ['c', 'd', 'a', 'b', 'c'],
                    'verificar_conteo_postmutacion': [1, 0, 1, 1, 1],
                    'verificar_nada': 2}

        self.assertEqual(self.test.verificar_todo(), expected)