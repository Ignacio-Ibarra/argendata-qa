import argendata
import argparse

class Parser(argparse.ArgumentParser):
    
    def __init__(self):
        super(Parser, self).__init__(description='ArgenData CLI')

        self.add_argument('-s', '--subtopico', type=str, help='Subtopico a analizar')
        self.add_argument('-e', '--entrega', type=int, help='Entrega a analizar')
        self.add_argument('-a', '--alias', type=str, help='Alias de la entrega a analizar (Ejemplo: ABCDEF2)')
    
    def get_args(self): ...

    def parse_args(self):
        self.args = super(Parser, self).parse_args().__dict__
        return self
    


if __name__ == '__main__':
    parser = Parser().parse_args()
    args = parser.args

    if all(map(lambda x: x is None, args.values())):
        print('No se especificó ningún argumento')
        parser.print_help()
        exit(1)

    subtopico = args.get('subtopico', None)
    entrega = args.get('entrega', None)

    alias = args.get('alias', None)
    if alias is not None:
        if subtopico is not None or entrega is not None:
            print('No se puede especificar un alias y un subtopico/entrega al mismo tiempo')
            exit(1)

        subtopico = alias[:6]
        entrega = int(alias[6:])

    argendata.main(subtopico, entrega)