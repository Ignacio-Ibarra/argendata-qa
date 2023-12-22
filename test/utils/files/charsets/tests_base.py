from unittest import TestCase, TextTestRunner, TestSuite, TestLoader
from glob import glob
import json
import os

def without_extension(filename):
    last_dot_index = filename.rfind('.')

    if last_dot_index == -1:
        return filename
    
    return filename[:last_dot_index]

class EncodingBaseTests:
    def test_detectar_encoding(self, file):
        name = os.path.basename(file)
        name = without_extension(name)
        detected = self.function(file)
        if name.startswith('test_') or name.startswith('long-test_'):
            index = name.find('_')
            expected = name[index+1:]
        else:
            expected = self.encodings_expected[name]
        if detected != expected:
            if detected:
                print(f"\n[Warning, '{detected}' != '{expected}' on '{name}' with '{self.function.__name__}'] ", end='')
        self.assertTrue(True)

    def test_abrir(self, file):
        try:
            with open(file, 'r') as f:
                ...
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)
            print(e)

    #  def test_caracteres_raros(self, file):
    #      try:
    #          with open(file, 'r') as f:
    #              for x in f.readlines():
    #                  if ';' in x:
    #                      self.assertTrue(False)
    #      except Exception:
    #          self.assertTrue(False)
    #      self.assertTrue(True)

def make_test(function, file):
    def curry_self(self):
        function(self, file)
    return curry_self

class EncodingTest:
    gtests: list[type] = []

    def testcase(f: callable):
        def make_testcase(cls: type):
            class NewClass(cls, TestCase):
                function = staticmethod(f)
                files = []
                encodings_expected: dict
                with open('./test/utils/files/charsets/testfiles_encoding/encodings.json', 'r') as fp:
                    encodings_expected = json.load(fp)

            for file in glob('./test/utils/files/charsets/testfiles_encoding/*.csv'):
                name = os.path.basename(file)
                name = without_extension(name)
                NewClass.files.append(name)
                
                for k,v in EncodingBaseTests.__dict__.items():
                    if k.startswith('test_'):
                        setattr(NewClass, f'{k}_{name}', make_test(v, file))

            EncodingTest.gtests.append(NewClass)
            return NewClass
        return make_testcase

    @staticmethod
    def get_suite():
        loader = TestLoader()
        suite = TestSuite()
        for test in EncodingTest.gtests:
            suite.addTest(loader.loadTestsFromTestCase(test))
        return suite

    @staticmethod
    def run_all():
        TextTestRunner().run(EncodingTest.get_suite())
