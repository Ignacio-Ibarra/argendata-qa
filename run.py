import argendata
import argparse
import os

def remove_folder_recursive(folder_path):
    try:
        items = os.listdir(folder_path)
        
        for item in items:
            item_path = os.path.join(folder_path, item)
            
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                remove_folder_recursive(item_path)
        os.rmdir(folder_path)
        
    except OSError as e:
        print(f"Error: {e}")


class Parser(argparse.ArgumentParser):
    
    def __init__(self):
        super(Parser, self).__init__(description='ArgenData CLI')

        self.add_argument('-s', '--subtopico', type=str, help='Subtopico a analizar')
        self.add_argument('-e', '--entrega', type=int, help='Entrega a analizar')
        self.add_argument('-a', '--alias', type=str, help='Alias de la entrega a analizar (Ejemplo: ABCDEF2)')
        self.add_argument('-C', '--clean-first', action='store_true', help='Borra los archivos de la entrega antes de analizarla')
        self.add_argument('-i', '--index', action='store_true', help='Crea la tabla de índices')
        self.add_argument('-d', '--exportar-definitivo', action='store_true', help='Genera tabla de índices y renombra los archivos.')
        self.add_argument('-u', '--update', action='store_true')

        # Argumento de debug para poder testear los argumentos.
        # Si está, no se ejecuta el programa.
        self.add_argument('--testarguments', '--testarguments', type=bool, help=argparse.SUPPRESS)
    
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
    generate_indices = args.get('index', False)
    exportar_definitivo = args.get('exportar_definitivo', False)
    update = args.get('update', False)

    if (not subtopico and not alias) or (entrega and alias) or (subtopico and not entrega):
        print('Se debe especificar un subtopico y una entrega, o un alias')
        parser.print_help()
        exit(1)

    if alias is not None:
        if subtopico is not None or entrega is not None:
            print('No se puede especificar un alias y un subtopico/entrega al mismo tiempo')
            parser.print_help()
            exit(1)

        subtopico = alias[:6]
        entrega = int(alias[6:])

    if args.get('testarguments', False):
        exit(0)

    clean_first = args.get('clean_first', False)

    if clean_first:
        remove_folder_recursive(f'./output/')
        remove_folder_recursive(f'./tmp/')

    if update:
        print(subtopico, entrega)
    else:
        argendata.main(subtopico, entrega, generate_indices, exportar_definitivo)