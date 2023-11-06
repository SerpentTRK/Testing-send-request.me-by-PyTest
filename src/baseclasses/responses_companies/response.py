import re

from src.enums.global_enums import GlobalErrorMessages


class ResponseCompaniesTest:

    def __init__(self, response):
        self.response = response

    def validate_status_company(self, body_key, body_value):
        """
        Валидация нужных элементов json("body")
        """
        for dicts in self.response.json().get("data"):
            for key, value in dicts.items():
                if key == body_key:
                    assert value == body_value, "Не верный company_status"
                    return self

    def assert_limit_json_body_data(self, num):
        """
        Валидация json("body") c query-параметром limit
        """
        for key, value in self.response.json().get("meta").items():
            if key == "limit":
                len_data = value
        assert len(self.response.json().get("data")) == len_data == num, "Ошибка в работе limit"
        return self

    def assert_offset_json_body_data(self, offset_num, company_id):
        """
        Валидация json("body") c query-параметром offset
        """
        for key, value in self.response.json().get("meta").items():
            if key == "offset":
                offset_meta_data = value
        for dicts in self.response.json().get("data"):
            for key, value in dicts.items():
                if key == "company_id":
                    first_id = value

        assert offset_meta_data == offset_num and company_id == first_id, "Ошибка в работе offset"
        return self

    def assert_first_language_in_response(self, lang):
        """
        Если в JSON есть translation_lang, то первый язык должен быть EN
        """
        for dict in self.response.json().get("description_lang")[:1]:
            for key, value in dict.items():
                if key == "translation_lang":
                    assert value == lang, "Первый язык должен быть EN"
                    return self

    def assert_comparison_uri_in_request_and_response(self, url):
        """
        Проверка на совпадение URI из запроса и URI из ответа
        """
        assert self.response.url == url, "Адреса не совпадают"
        return self

    def assert_response_message_about_error_404(self, company_id):
        """
        Валидация 404 ошибки. В нем должен быть указан тот company_id, что и в URI
        """
        for key, value in self.response.json().get("detail").items():
            assert value == f"Company with requested id: {company_id} is absent", self
            return self

    def assert_response_message_about_error_422(self, resp_key, resp_value):
        """
        Валидация сообщения об 404 ошибке.
        """
        for dicts in self.response.json().get("detail"):
            for key, value in dicts.items():
                if key == resp_key:
                    assert value == resp_value
                    return self

    def assert_language(self, lang):
        """
        Валидация текста языка в тексте. Функция принимает алфавит и сверяет соответствие
        """
        text = self.response.json().get("description").split()  # [каждое, слово, отдельно]
        text = ''.join(text)  # вернулитекстизспискаудалилипробелы
        only_text = re.sub(r'[^\w\s]', '', text)  # удаляем все символы, отличные от букв

        for words in only_text:
            assert words.lower() in lang
            return self



    def __str__(self):
        return \
            f"\nRequested Url: {self.response.url} \n" \
            f"Status code: {self.response.status_code} \n" \
            f"Response body: {self.response.json().get('data')} \n" \
            f"Response headers: {self.response.headers}"