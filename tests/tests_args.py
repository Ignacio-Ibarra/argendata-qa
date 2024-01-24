import subprocess
import unittest

def execute_python_file(file_path, **kwargs):
    args = []
    for key, value in kwargs.items():
        prefix = ''
        if len(key) == 1:
            prefix = '-'
        else:
            prefix = '--'
        
        args.append(f'{prefix}{key}')
        args.append(str(value))
    process = subprocess.Popen(['python3', file_path, *args], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    return process.returncode, stdout, stderr

def run(**kwargs):
    return execute_python_file('run.py', **kwargs)

class TestsArguments(unittest.TestCase):

    def test_no_arguments(self):
        returncode, stdout, stderr = run()

        self.assertEqual(returncode, 1)
    
    def test_alias_ok(self):
        returncode, stdout, stderr = run(alias='TRANEN1', 
                                         testarguments=True)

        self.assertEqual(returncode, 0, (stdout, stderr))
    
    def test_subtopico_entrega_ok(self):
        returncode, stdout, stderr = run(subtopico='TRANEN', 
                                         entrega=1, 
                                         testarguments=True)

        self.assertEqual(returncode, 0, (stdout, stderr))
    
    """
    | s | e | a | r |
    |---|---|---|---|
    | 0 | 0 | 0 | 0 |
    | 0 | 0 | 1 | 1 | # -a TRANEN1
    | 0 | 1 | 0 | 0 |
    | 0 | 1 | 1 | 0 |
    | 1 | 0 | 0 | 0 |
    | 1 | 0 | 1 | 0 |
    | 1 | 1 | 0 | 1 | # -s TRANEN -e 1
    | 1 | 1 | 1 | 0 |
    """
    def test_wrong_combinations(self):
        x = 0b000
        while x <= 0b111:
            kwargs = {}
            if x & 0b100:
                kwargs['subtopico'] = 'TRANEN'
            if x & 0b010:
                kwargs['entrega'] = 1
            if x & 0b001:
                kwargs['alias'] = 'TRANEN1'

            if x not in (0b001, 0b110):
                returncode, stdout, stderr = run(**kwargs)
                self.assertEqual(returncode, 1, (stdout, stderr))

            x += 1
    
