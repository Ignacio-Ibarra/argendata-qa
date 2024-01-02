import unittest
from argendata.utils import MethodMapping

class TestMethodMappingBackCompatibility(unittest.TestCase):

    def test_register_with_key(self):
        mapping = MethodMapping()

        @mapping.register("key")
        def some_function():
            return "Hello, World!"

        self.assertEqual(mapping["key"], some_function)

    def test_register_multiple_with_key(self):
        mapping = MethodMapping()

        @mapping.register("key1")
        def function_one():
            return "Function One"

        @mapping.register("key2")
        def function_two():
            return "Function Two"

        self.assertEqual(mapping["key1"], function_one)
        self.assertEqual(mapping["key2"], function_two)

    def test_overwrite_with_key(self):
        mapping = MethodMapping()

        @mapping.register("key")
        def initial_function():
            return "Initial Function"

        @mapping.register("key")
        def new_function():
            return "New Function"

        self.assertEqual(mapping["key"], new_function)

    def test_access_nonexistent(self):
        mapping = MethodMapping()

        with self.assertRaises(KeyError):
            result = mapping["nonexistent_key"]

    def test_register_new(self):
        mapping = MethodMapping()

        def some_function():
            return "Hello, World!"

        mapping.register(some_function)
        self.assertEqual(mapping[some_function.__name__], some_function)

    def test_register_new_decorator(self):
        mapping = MethodMapping()

        @mapping.register
        def some_function():
            return "Hello, World!"

        self.assertEqual(mapping["some_function"], some_function)