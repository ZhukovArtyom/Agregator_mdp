import textrazor
import requests


class TextRazorTextAnalyzer:

    translate_api_key="a2ec4440b51765470cb2"
    def __init__(self, api_key):
        self.client = textrazor.TextRazor(api_key)
        # Включаем категоризацию
        self.client.set_classifiers(["textrazor_newscodes"])

    def translate_text(self, text, source_lang="en", target_lang="ru"):
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": f"{source_lang}|{target_lang}",
            "key": self.translate_api_key,
            "de": "buggy_art@mail.ru"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        translated = response.json()["responseData"]["translatedText"]
        return translated

    def analyze_text(self, text):
        response = self.client.analyze(text)
        categories = response.categories()

        if not categories:
            return None

        categor = []
        for category in categories:
            if category.score > 0.397:
                general_category = category.label.split('>')[0].strip()
                translated_category = self.translate_text(general_category)
                if translated_category not in categor:
                    categor.append(translated_category)
                    print(translated_category, category.score)

        return categor if categor else None






