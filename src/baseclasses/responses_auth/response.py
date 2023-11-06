class ResponseAuthTest:

    def __init__(self, response):
        self.response = response

    def assert_token(self, token, token_len):
        """
        Валидация токена
        """
        for key, value in self.response.json().items():
            assert key == token, f"{token} != {key}"
            assert len(value) == token_len, f"token: {value}. Длинна токена != {token_len}"
            return self

    def assert_response_message_about_error_403(self, error_message):
        """
        Валидация сообщения об ошибке. В нем должен быть указан тот company_id, что и в URI
        """
        for key, value in self.response.json().get("detail").items():
            assert value == error_message, f"{error_message} != {value}"
            return self

    def assert_response_message_about_error_422(self, resp_key, resp_value):
        """
        Валидация сообщения об 422 ошибке.
        """
        for dicts in self.response.json().get("detail"):
            for key, value in dicts.items():
                if key == resp_key:
                    assert value == resp_value
                    return self

    def assert_user_data(self, user_name):
        assert user_name == self.response.json().get("user_name"), f"{user_name} != {self.response.json().get('user_name')}"
        return self


    def __str__(self):
        return \
            f"\nRequested Url: {self.response.url} \n" \
            f"Status code: {self.response.status_code} \n" \
            f"Response body: {self.response.json().get('data')} \n" \
            f"Response headers: {self.response.headers}"