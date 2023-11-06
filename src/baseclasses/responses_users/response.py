import pytest
import requests

from pytest import assume

from configuration import baseUrl_users
from src.enums.global_enums import GlobalErrorMessages


class ResponseUsersTest:

    def __init__(self, response):
        self.response = response

    def assert_limit_json_body_data(self, num):
        """
        Валидация json("body") c query-параметром limit
        """
        for key, value in self.response.json().get("meta").items():
            if key == "limit":
                len_data = value
        assert len(self.response.json().get("data")) == len_data == num, self
        return self

    def assert_response_message_about_error_404(self, user_id):
        """
        Валидация сообщения об ошибке. В нем должен быть указан тот company_id, что и в URI
        """
        for key, value in self.response.json().get("detail").items():
            assert value == f"User with requested id: {user_id} is absent", self
            return self

    def assert_response_message_about_error_400(self, company_id):
        """
        Валидация сообщения об ошибке. В нем должен быть указан тот company_id, что и в URI
        """
        for key, value in self.response.json().get("detail").items():
            assert value == f"User could not be assigned to company with id: {company_id}. Because it is not active", self
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

    def calculate_first_id_for_response_with_offset(self, offset):
        """
        Проблема в том, что id пользователей начинаются не с 1, а произвольного числа,
        потому чтобы понять, правильно в тесте работает offset или нет, нам надо сперва
        сделать запрос без offset, и взять resp.json().get("data")[offset].get("user_id") = id шестого
        по порядку пользователя в базе, и сразвнить с id первого пользователя из теста.
        """
        params = {"limit": 10}
        resp = requests.get(baseUrl_users, params=params)

        # print(resp.json().get("data")[0].get("user_id")) # без offset
        # print(self.response.json().get("data")[0].get("user_id"))  # c offset
        assert resp.json().get("data")[offset].get("user_id") == self.response.json().get("data")[0].get("user_id")
        return self

    def assert_user(self, first_name, last_name, company_id):
        """
        Проверка на соответствие того, что пользователь в БД именно такой, каким его создали
        """
        for key, value in self.response.json().items():
            if key == "first_name" and value != first_name:
                raise ValueError("Имя не совпадает")
            if key == "last_name" and value != last_name:
                raise ValueError("Фамилия не совпадает")
            if key == "company_id" and value != company_id:
                raise ValueError("Id не совпадает")
            return self

    # def assert_user(self, first_name, last_name, company_id):
    #     """
    #     Проверка на соответствие того, что пользователь в БД именно такой, каким его создали
    #     """
    #     for key, value in self.response.json().items():
    #         with pytest.assume:
    #             if key == "first_name":
    #                 assert value == first_name, "Не совпадает имя"
    #             if key == "last_name":
    #                 assert value == last_name, "Не совпадает фамилия"
    #             if key == "company_id":
    #                 assert value == company_id, "Не совпадает Id"
    #         return self




    def __str__(self):
        return \
            f"\nRequested Url: {self.response.url} \n" \
            f"Status code: {self.response.status_code} \n" \
            f"Response body: {self.response.json().get('data')} \n" \
            f"Response headers: {self.response.headers}"