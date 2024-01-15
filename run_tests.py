import unittest
import tests.tests_controles_calidad

loader = unittest.TestLoader()
start_dir = "./tests"

suite = loader.discover(start_dir)
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
