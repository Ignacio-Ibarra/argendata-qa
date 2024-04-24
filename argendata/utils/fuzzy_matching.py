from argendata.utils.translator import bulk_translate, translate
import unicodedata
import numpy as np
from typing import List, Callable
from lingua import Language, LanguageDetectorBuilder, LanguageDetector
import pandas as pd

languages = [Language.ENGLISH, 
             Language.SPANISH,
             Language.FRENCH,
             Language.PORTUGUESE]



detector = LanguageDetectorBuilder.from_languages(*languages).build()


# Limpieza de strings
def remove_whitespaces(s:str)->str:
    return " ".join(s.split())

def strip_accents(s:str)->str:
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
    

def remove_punctuation(s:str, remove_string:str ='!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¿´')->str:
    translation = str.maketrans(remove_string, ' ' * len(remove_string))
    return s.translate(translation)

def remove_special_words(s:str, special_words:list=['republica','de', 'del'])->str:
    s = ' '.join(filter(lambda x: x not in special_words,  s.split(" ")))
    return s

    
def sort_words_alphabetically(s:str)->str:
    return " ".join(sorted(s.split(" ")))


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
    
     
        


def normalize_string(s:str, 
                     to_lower:bool=False,
                     rm_accents:bool=False,
                     rm_punct:bool=False, 
                     rm_spw:bool=False, 
                     rm_whitesp:bool=False, 
                     sort_words:bool=False)->str:
    if to_lower:
        s = s.lower()
            
    if rm_accents:
        s = strip_accents(s)
    if rm_punct:
        s = remove_punctuation(s)
    if rm_spw:
        s = remove_special_words(s)
    if rm_whitesp:
        s = remove_whitespaces(s)
    if sort_words:
        s = sort_words_alphabetically(s)
    return s

def str_normalizer(normalize_params:dict)->Callable:
    return lambda s: normalize_string(s=s, **normalize_params)

# Tokenización..
def ngrams_tokenizer(s: str, n:int=3) -> List[str]:
    return [s[i:i+n] for i in range(len(s)-n+1)]
 
def word_tokenizer(s:str)->list[str]: 
    return s.split(" ")

def character_tokenizer(s:str)->list[str]: 
    return list(s)


# Métricas
def jaccard_similarity(s1:str, s2:str, tokenizer:Callable)->float:
    set1 = set(tokenizer(s1))
    set2 = set(tokenizer(s2))
    intersect_n = len(set1 & set2)
    union_n =len(set1 | set2)
    return intersect_n / union_n

def jaccard_words_similarity(s1:str,s2:str, tokenizer=word_tokenizer)->float:
    return jaccard_similarity(s1,s2,tokenizer)

def jaccard_character_similarity(s1:str,s2:str, tokenizer=character_tokenizer)->float:
    return jaccard_similarity(s1,s2,tokenizer)

def jaccard_ngrams_similarity(s1:str,s2:str, tokenizer=ngrams_tokenizer)->float:
    return jaccard_similarity(s1,s2,tokenizer)

def inclusion_en_derecha(s1,s2): 
    set1 = set(word_tokenizer(s1) )
    set2 = set(word_tokenizer(s2) ) 
    return int(set1 <= set2)

def inclusion_en_izquierda(s1,s2): 
    set1 = set(word_tokenizer(s1) )
    set2 = set(word_tokenizer(s2) ) 
    return int(set1 >= set2)
        
def levenshtein_distance(a, b):
    n = len(a)
    m = len(b)

    matrix = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        matrix[i][0] = i
    for j in range(m + 1):
        matrix[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,  # deletion
                matrix[i][j - 1] + 1,  # insertion
                matrix[i - 1][j - 1] + cost  # substitution
            )

    # The bottom-right cell contains the minimum edit distance
    return matrix[n][m]

 
def map_value(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

def mapper_of(ostart, ostop):
    return lambda value, istart, istop : map_value(value, istart, istop, ostart, ostop)

    
my_mapper = mapper_of(0,1)

def normalized_levenshtein_similarity(s1:str, s2:str, mapper:callable = my_mapper)->float:
    negative_max_len = -max(len(s1),len(s2))
    scr = -levenshtein_distance(s1,s2)
    norm_scr = mapper(scr, negative_max_len, 0)
    return norm_scr



def similarity_scores(s1:str, s2:str)->bool:
    
    incl_der_scr = inclusion_en_derecha(s1,s2)
    incl_izq_scr = inclusion_en_izquierda(s1,s2)
    norm_lev_scr = normalized_levenshtein_similarity(s1,s2)
    jacc_w_scr = jaccard_words_similarity(s1,s2)
    jacc_c_scr = jaccard_character_similarity(s1, s2)
    jacc_n_scr = jaccard_ngrams_similarity(s1,s2)

    return [
        incl_der_scr, 
        incl_izq_scr, 
        norm_lev_scr, 
        jacc_w_scr, 
        jacc_c_scr, 
        jacc_n_scr
        ]

def binarization_thresh(similarities_scores:list, threshs:list)->list[int]:
    return [scr >= th for scr,th in zip(similarities_scores, threshs)]

def combine_results(bin_results:list, weights:list):
    return np.dot(bin_results, weights)

threshs_selected = [
    1, 1, 
    0.6, 0.1, 0.6, 0.6]
n = len(threshs_selected)
weights_selected = [1/n]*n

def evaluate_similarity(s1:str, s2:str, threshs:list=threshs_selected, weights:list = weights_selected)->float:
    # if normalizer: 
    #     s1, s2 = list(map(normalizer, [s1,s2]))
    sim_scr = similarity_scores(s1,s2)
    bin_results = list(map(int, binarization_thresh(similarities_scores=sim_scr, threshs=threshs)))
    result = combine_results(bin_results=bin_results, weights=weights)
    return result

def likely_matching(s1:str, s2:str, threshs:list=threshs_selected, strictly=False, k:int=-1)->bool:
    # if normalizer: 
    #     s1, s2 = list(map(normalizer, [s1,s2]))
    sim_scr = similarity_scores(s1,s2)
    bin_results = binarization_thresh(similarities_scores=sim_scr, threshs=threshs)
    result = any(bin_results)
    if k > -1: 
        result = sum(bin_results) >= k
    if strictly: 
        result = all(bin_results)
    return result

def colnames_similarity(a: str, b: str) -> float:
    
    scr = normalized_levenshtein_similarity(s1=a, s2=b, mapper=my_mapper)
    return scr 

def colnames_similarityx(a: str) -> Callable[[str], float]:
    return lambda b: colnames_similarity(a, b)