import pytest
import requests
import time

from datetime import timedelta

from src.baseclasses.response import ResponseTest
from src.baseclasses.responses_auth.response import ResponseAuthTest

from src.pydantic_shemas.model_api_https_422 import Model_https_422
from src.pydantic_shemas.model_auth_200 import ModelAuth200

@pytest.mark.parametrize("login, password, timeout, result", [
    ("1234567", "qwerty12345", 30000, 200),
    ("123", "qwerty12345", 30000, 200),
    ("1", "qwerty12345", 30000, 422),
    ("12", "qwerty12345", 30000, 422),
    ("0", "qwerty12345", 30000, 422),
    ("", "qwerty12345", 30000, 422),
    (None, "qwerty12345", 30000, 422),
    ("123", "qwerty", 30000, 403),
    ("123", "0", 30000, 403),
    ("123", "", 30000, 403),
    ("123", None, 30000, 422)
])
def test_create_token_with_different_combination_034(login, password, timeout, result, authorization):
    """
    Получить токен подставляя допустимые и не допустимые значения обязательных полей для
    создания tocken

    Проведение общих проверок для всех тестов:
        Статус-код соответствует ожидаемому
        Валидация модели или сообщения об ошибке
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        Время ответа сервера - не превышает 500ms;* это время пришлось сильно увеличить,
        т.к. тестовая база иногда еле отзывается, и все тесты падают на этой проверке
    """
    test_object = ResponseTest(authorization(login, password, timeout))  # ответ от сервера, который мы предали в класс Test_response
    test_object_auth = ResponseAuthTest(authorization(login, password, timeout))


    if (authorization(login, password, timeout)).status_code == 200:
        test_object.assert_status_code(200). \
            assert_response_header("content-type", "application/json"). \
            assert_response_header("connection", "keep-alive"). \
            assert_https_request("443")
        test_object_auth.assert_token("token", 32)
        test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))
    elif (authorization(login, password, timeout)).status_code == 422:
        test_object.validate_schema(Model_https_422). \
            assert_response_header("content-type", "application/json"). \
            assert_response_header("connection", "keep-alive"). \
            assert_https_request("443")

        resp = authorization(login, password, timeout).json().get("detail")
        for item in resp:
            resp_value = item["msg"]
        test_object_auth.assert_response_message_about_error_422("msg", resp_value)

        test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))
    else:
        test_object.assert_response_header("content-type", "application/json"). \
            assert_response_header("connection", "keep-alive"). \
            assert_https_request("443")
        test_object_auth.assert_response_message_about_error_403("Invalid password")
        test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

    # if (authorization(login, password, timeout)).status_code == 422:
    #     resp = authorization(login, password, timeout).json().get("detail")
    #     for item in resp:
    #         print(item["msg"])




def test_get_data_about_user_by_token_035(create_token):
    """
    Получить данные пользователя по токену.

    Проведение общих проверок для всех тестов:
        Статус-код 200;
        Валидация модели;
        Response header "Content-Type" - "application/json";
        Response header "Connection" - "keep-alive";
        Соединение безопасное, порт 443;
        Проверка, что логин пользователя при создании токена совпадает с данными, при авторизации по токену;
        Время ответа сервера - не превышает 500ms;* это время пришлось сильно увеличить,
        т.к. тестовая база иногда еле отзывается, и все тесты падают на этой проверке
    """
    payload = {}
    headers = {"x-token": (create_token).json().get("token")}
    resp = requests.get("https://send-request.me/api/auth/me", headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_auth = ResponseAuthTest(resp)

    test_object.assert_status_code(200). \
        validate_schema(ModelAuth200). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443")
    test_object_auth.assert_user_data("Test_login")
    test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

def test_get_data_about_user_with_incorrect_token_036():
    """
        Авторизовать пользователя по не верному (поддельному) токену.

        Проведение общих проверок для всех тестов:
            Статус-код 403;
            Валидация сообщения об ошибке;
            Response header "Content-Type" - "application/json";
            Response header "Connection" - "keep-alive";
            Соединение безопасное, порт 443;
            Время ответа сервера - не превышает 500ms;* это время пришлось сильно увеличить,
            т.к. тестовая база иногда еле отзывается, и все тесты падают на этой проверке
        """
    payload = {}
    headers = {"x-token": "48b61190f764f18d75ee696cbb115be0"}
    resp = requests.get("https://send-request.me/api/auth/me", headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_auth = ResponseAuthTest(resp)

    test_object.assert_status_code(403). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443")
    test_object_auth.assert_response_message_about_error("Token is incorrect. Please login and try again")
    test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

def test_get_data_about_user_with_token_after_timeout_037(authorization):
    """
    Авторизация по просроченному токену.

    Проведение общих проверок для всех тестов:
        Статус-код 403;
        Валидация сообщения об ошибке;
        Response header "Content-Type" - "application/json";
        Response header "Connection" - "keep-alive";
        Соединение безопасное, порт 443;
        Время ответа сервера не исследуем, т.к. тут осознанно придерживаем выполнение теста, чтобы
        время жизни токена истекло
    """
    resp = authorization("1234765", "qwerty12345", 2)

    time.sleep(5)

    url = "https://send-request.me/api/auth/me"
    payload = ""
    headers = {'x-token': resp.json().get("token")}
    resp = requests.request("GET", url, headers=headers, data=payload)

    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_auth = ResponseAuthTest(resp)

    print(resp.json())

    test_object.assert_status_code(403). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443")
    test_object_auth.assert_response_message_about_error("Token is expired. Please login and try again")
    test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

def test_get_data_about_user_without_token_038():
    """
        Авторизовать пользователя без токена.

        Проведение общих проверок для всех тестов:
            Статус-код 403;
            Валидация сообщения об ошибке;
            Response header "Content-Type" - "application/json";
            Response header "Connection" - "keep-alive";
            Соединение безопасное, порт 443;
            Время ответа сервера - не превышает 500ms;* это время пришлось сильно увеличить,
            т.к. тестовая база иногда еле отзывается, и все тесты падают на этой проверке
        """
    payload = {}
    headers = {"x-token": ""}
    resp = requests.get("https://send-request.me/api/auth/me", headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_auth = ResponseAuthTest(resp)

    test_object.assert_status_code(403). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443")
    test_object_auth.assert_response_message_about_error_403("Token is incorrect. Please login and try again")
    test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

