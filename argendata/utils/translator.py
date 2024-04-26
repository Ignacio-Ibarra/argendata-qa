import sys
import re
from typing import Literal, List
from time import sleep
import numpy.random as random
import pandas as pd
from lingua import LanguageDetector



if (sys.version_info[0] < 3):
    import urllib2
    import urllib
    import HTMLParser
else:
    import html
    import urllib.request
    import urllib.parse

agent = {'User-Agent':
         "Mozilla/4.0 (\
compatible;\
MSIE 6.0;\
Windows NT 5.1;\
SV1;\
.NET CLR 1.1.4322;\
.NET CLR 2.0.50727;\
.NET CLR 3.0.04506.30\
)"}


def unescape(text):
    if (sys.version_info[0] < 3):
        parser = HTMLParser.HTMLParser()
    else:
        parser = html
    return (parser.unescape(text))


def translate(to_translate, to_language="auto", from_language="auto"):
    """Returns the translation using google translate
    you must shortcut the language you define
    (French = fr, English = en, Spanish = es, etc...)
    if not defined it will detect it or use english by default

    Example:
    print(translate("salut tu vas bien?", "en"))
    hello you alright?
    """
    sleep(random.uniform(.5,.7))

    base_link = "http://translate.google.com/m?tl=%s&sl=%s&q=%s"
    if (sys.version_info[0] < 3):
        to_translate = urllib.quote_plus(to_translate)
        link = base_link % (to_language, from_language, to_translate)
        request = urllib2.Request(link, headers=agent)
        raw_data = urllib2.urlopen(request).read()
    else:
        to_translate = urllib.parse.quote(to_translate)
        link = base_link % (to_language, from_language, to_translate)
        request = urllib.request.Request(link, headers=agent)
        raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("utf-8")
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    re_result = re.findall(expr, data)
    if (len(re_result) == 0):
        result = ""
    else:
        result = unescape(re_result[0])
    return (result)

def bulk_translate(string_list:List[str], input_lang:Literal['en','es','fr','auto'] = 'auto', 
                   output_lang:Literal['en','es','fr','auto'] = 'auto', collapser:str =" @ ")->list[str]:
    
    s = collapser.join(string_list)
    o = translate(s, from_language=input_lang, to_language=output_lang)
    return [x.lstrip().rstrip() for x in o.split(collapser)]

def translate_by_chunk(string_list: List[str], n_chunks: int = 5, 
                   input_lang: Literal['en', 'es', 'fr', 'auto'] = 'auto', 
                   output_lang: Literal['en', 'es', 'fr', 'auto'] = 'auto', 
                   collapser: str = " @ ") -> List[str]:
    
    translated_strings = []
    
    chunk_size = len(string_list)//n_chunks
    # Divide la lista de cadenas en chunks
    for i in range(0, len(string_list), chunk_size):
        chunk_list = string_list[i:i+chunk_size]
                
        # Traduce el chunk actual
        translated_chunk = bulk_translate(chunk_list, input_lang=input_lang, output_lang=output_lang, collapser=collapser)
               
        # Divide el resultado del chunk traducido y lo agrega a la lista de traducciones
        translated_strings.extend(translated_chunk)
    
    return translated_strings


def detect_language(list_strings:list[str], lang_detector:LanguageDetector)->str: 
    detections = lang_detector.compute_language_confidence_values_in_parallel(list_strings)
    results = list(map(lambda x: x[0].language.iso_code_639_1.name.lower(), detections))
    # TODO: determinar falsos positivos.
    # TODO: ver como viene la distribución de scores para ver si elijo el primero o no. 
    return results

def auto_translate(input_strings:list[str], lang_detector:LanguageDetector): 
    df = pd.DataFrame()
    df['detected_languages'] = detect_language(list_strings=input_strings, lang_detector=lang_detector)
    df['input_strings'] = input_strings
    df['output_strings'] = input_strings

    for detected_lang in df.detected_languages.unique(): 
        filtered_list = df.loc[df.detected_languages == detected_lang, 'input_strings'].to_list()
        if detected_lang != "es":
            translated_list = bulk_translate(string_list=filtered_list, input_lang=detected_lang, output_lang='es')
            df.loc[df.detected_languages == detected_lang, 'output_strings'] = translated_list

    return df.output_strings.to_list()


def auto_translator(lang_detector:LanguageDetector): 
    return lambda input_strings: auto_translate(input_strings=input_strings, lang_detector=lang_detector)