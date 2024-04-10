from typing import Callable

def similarity(a: str, b: str) -> float:
    
    # TODO: Implementar alguna técnica de fuzzy matching.
    return 1 if a == b else 0

def similar_to(a: str) -> Callable[[str], float]:
    return lambda b: similarity(a, b)