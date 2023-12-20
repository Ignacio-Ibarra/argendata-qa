from tests_base import EncodingTest
import charset_normalizer
import chardet

def detectar_encodings_con_charsetnormalizer(filepath: str) -> str:
    try:
        with open(filepath, 'rb') as file:
            sample = file.read()
        
        result = charset_normalizer.detect(sample)

        return result['encoding']

    except Exception as e:
        print(f"Error: {e}")
        return e.__class__.__name__

@EncodingTest.testcase(detectar_encodings_con_charsetnormalizer)
class Encodings1: pass

def detectar_encodings_con_chardet(filepath: str) -> str:
    try:
        with open(filepath, 'rb') as file:
            detector = chardet.universaldetector.UniversalDetector()

            # Read the file in chunks to minimize memory usage
            for line in file:
                detector.feed(line)
                if detector.done:
                    break

            detector.close()
            result = detector.result

            # The detected encoding and confidence
            detected_encoding = result['encoding']
            confidence = result['confidence']

            return detected_encoding
    except Exception as e:
        return e.__class__.__name__
    
@EncodingTest.testcase(detectar_encodings_con_chardet)
class Encodings3: pass

#  def detectar_encodings_con_bloques(filepath: str) -> str:
#      ...
#      ...
#      ...
#      return 'mac_latin2'
#  
#  @EncodingTest.testcase(detectar_encodings_con_bloques)
#  class Encodings2: pass

if __name__ == '__main__':
    EncodingTest.run_all()
