from typing import Iterable

VALID_ENCODINGS: list[str]
"""Son todos los encodings validos de Python"""

VALID_ENCODINGS = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775',
                   'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864',
                   'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125',
                   'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258',
                   'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'latin_1',
                   'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8',
                   'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16',
                   'johab', 'koi8_r', 'koi8_t', 'koi8_u', 'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland',
                   'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004',
                   'shift_jisx0213', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be',
                   'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig']

PRIORITY_ENCODINGS: list[str]
"""Está completamente incluída en VALID_ENCODINGS. Son todos los encodings que estamos dispuestos a detectar."""

PRIORITY_ENCODINGS = ['utf_8', 'utf_8_sig', 'ascii', 'latin_1', 'iso8859_2',
                      'cp1252', 'mac_latin2', 'utf_16', 'utf_32', 'utf_7']

PRIORITY_ENCODINGS_WITH_ALIAS: list[str]
"""Está completamente incluída en PRIORITY_ENCODINGS. Son los alias definidos en la documentación de Python, más
   otros alias de los mismos encodings. Si se añaden nuevos, hay que respetar el orden de PRIORITY_ENCODINGS."""

PRIORITY_ENCODINGS_WITH_ALIAS = ['utf_8', 'utf-8', 'U8', 'UTF', 'utf8', 'cp65001', 'utf_8_sig',
                                 'utf-8-sig', 'ascii', '646', 'us-ascii', 'latin_1', 'iso-8859-1',
                                 'iso8859-1', '8859', 'cp819', 'latin', 'latin-1', 'latin1', 'L1',
                                 'iso8859_2', 'iso-8859-2', 'latin-2', 'latin2', 'L2', 'cp1252',
                                 'windows-1252', 'mac_latin2', 'maclatin2', 'maccentraleurope', 'mac_centeuro',
                                 'utf-16', 'utf_16', 'U16', 'utf16', 'utf-32', 'utf_32', 'U32', 'utf32',
                                 'utf-7', 'utf_7', 'U7', 'unicode-1-1-utf-7']

ESP_CHARSET: Iterable[str]
"""Es la lista de caracteres que se consideran válidos en una celda."""

ESP_CHARSET = '0123456789abcdefghijklmnñopqrstuvwxyzABCDEFGHIJKLMNÑOPQRSTUVWXYZáéíóúÁÉÍÓÚ _-+.,;()'
