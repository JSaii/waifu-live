from pykakasi import kakasi

def convert_to_hiragana(text: str) -> str:
    kks = kakasi()
    result = kks.convert(text)
    return "".join(item["hira"] for item in result)
