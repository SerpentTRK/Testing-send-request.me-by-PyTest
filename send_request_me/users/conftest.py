import requests
import pytest
import json

from configuration import baseUrl_users

@pytest.fixture
def create_user():
    """
    Фикстура создает пользователя, передает данные в тест, и по завершении теста удаляет пользователя.
    """
    payload = json.dumps({
        "first_name": "Вальдемар",
        "last_name": "Евлампиевич",
        "company_id": 3
    })
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(baseUrl_users, headers=headers, data=payload)
    user_id = resp.json().get("user_id")
    # print(user_id)  # удобно в постмане проверить, удалился ли потом пользователя

    yield resp

    payload = {}
    headers = {}
    resp_del = requests.delete(baseUrl_users + str(user_id), headers=headers, data=payload)
    # print(resp_del.json())  # убедиться, что записи нет





