from unittest import TestLoader, TextTestRunner
from test.utils.files.charsets import *  # Necesario para instanciar los tests
from test.utils.files.charsets import EncodingTest
from test.verificador import VerificadorStringTestsDinamicos, VerificadorStringTestsEstaticos


def get_suite():
    loader = TestLoader()
    suite = EncodingTest.get_suite()
    suite.addTest(loader.loadTestsFromTestCase(VerificadorStringTestsDinamicos))
    suite.addTests(loader.loadTestsFromTestCase(VerificadorStringTestsEstaticos))
    return suite


if __name__ == '__main__':
    TextTestRunner().run(get_suite())
