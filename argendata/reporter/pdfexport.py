import subprocess
import platform

def is_installed(command):
    try:
        subprocess.run([command, '--version'], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE, 
                       check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def pandoc_export(input: str, output: None|str = None) -> Exception|str:
    if not is_installed('pandoc'):
        print("Pandoc is not installed. Please install it. See https://pandoc.org/installing.html")
        return Exception("Pandoc is not installed")
    try:
        output = output or input[:-2]+'pdf'
        subprocess.run(['pandoc', input, 
                        '-o', output,
                        '--pdf-engine=xelatex'], 
                        check=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        return output
    except subprocess.CalledProcessError as e:
        if "xelatex not found" in str(e.stderr):
            print("PDF compilation failed. XeLaTeX is not installed. Please install it.")
            os_name = platform.system()
            if 'Linux' in os_name:
                print("Using APT package manager:")
                print("sudo apt-get install texlive-xetex")
            else:
                print("See: https://www.tug.org/texlive/")
                
        
        return e
