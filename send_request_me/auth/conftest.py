import requests
import pytest
import json

from configuration import baseUrl_users

#  надо переименовать. Тут не создание авторизация(авторизация,
#  но данные мы получаем по токену, а не по логину паролю, а получение токена
def _authorization(login, password, timeout):
    url = "https://send-request.me/api/auth/authorize"
    payload = json.dumps({"login": login, "password": password, "timeout": timeout})
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, headers=headers, data=payload)
    # return resp.status_code
    return resp
@pytest.fixture
def authorization():
    return _authorization #вызываем функцию внутри теста
    # auth_result = _autrorizatoin
    # return auth_result


#  надо переименовать. Тут не создание токена, а авторизация по токену
@pytest.fixture
def create_token():
    payload = json.dumps({
        "login": "Test_login",
        "password": "qwerty12345"
    })
    headers = {'Content-Type': 'application/json'}
    resp = requests.post("https://send-request.me/api/auth/authorize", headers=headers, data=payload)
    token = resp.json().get("token")
    return resp
    # print(token)