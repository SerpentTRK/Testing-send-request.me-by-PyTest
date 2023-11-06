# from datetime import timedelta

from src.enums.global_enums import GlobalErrorMessages

class ResponseTest:

    def __init__(self, response):
        self.response = response

    def assert_status_code(self, status_code):
        """
        Валидация статус-кода
        """
        if isinstance(status_code, list):
            assert self.response.status_code in status_code, f"Полученный статус-код {self.response.status_code} != ожидаемому {status_code}"
        else:
            assert self.response.status_code == status_code, f"Полученный статус-код {self.response.status_code} != ожидаемому {status_code}"
        return self

    def validate_time_from_request_to_response(self, max_time_to_response):
        """
        Валидация времени ответа от сервера
        """
        max_time_to_response = max_time_to_response
        resp_time = self.response.elapsed
        assert max_time_to_response > resp_time, "Превышено время ответа от сервера"
        return self

    def validate_schema(self, schema):
        """
        Валидация схемы
        """
        if isinstance(self.response.json(), list):
            for item in self.response.json():
                schema.model_validate(item)
        else:
            schema.model_validate(self.response.json())
        return self

    def assert_response_header(self, header, value):
        """
        Валидация заголовков ответа.
        """
        if header in self.response.headers:
            assert value == self.response.headers.get(header), f"{header} != {value}"
            return self

    def assert_https_request(self, port):
        assert port in self.response.headers.get("alt-svc"), f"Не безопасное соединение {self.response.headers.get('alt-svc')}"
        return  self


    def __str__(self):
        return \
            f"\nRequested Url: {self.response.url} \n" \
            f"Status code: {self.response.status_code} \n" \
            f"Response body: {self.response.json().get('data')} \n" \
            f"Response headers: {self.response.headers}"
