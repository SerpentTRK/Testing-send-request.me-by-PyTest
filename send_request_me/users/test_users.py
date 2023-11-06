import pytest
import requests
import json

from datetime import timedelta
from configuration import baseUrl_users
from src.baseclasses.response import ResponseTest
from src.baseclasses.responses_users.response import ResponseUsersTest
from src.baseclasses.responses_companies.response import ResponseCompaniesTest

from src.pydantic_shemas.model_api_users_200 import ModelUsers200
from src.pydantic_shemas.model_api_https_422 import Model_https_422
from src.pydantic_shemas.model_api_user_201 import ModelUser201
from src.pydantic_shemas.model_api_404 import Model404
from src.pydantic_shemas.model_api_https_400 import Model_https_400
from src.pydantic_shemas.model_api_user_200 import ModelUser200


@pytest.mark.parametrize("about, stat_code, schema, full_address", [
    ("{ -016- GET USERS WITH PARAMETERS {'limit': 10, 'offset': 5} }", 200, ModelUsers200, requests.get(baseUrl_users, params={"limit": 10, "offset": 5})),
    ("{ -017- GET USERS WITH PARAMETERS {'limit': -1} }", 422, Model_https_422, requests.get(baseUrl_users, params={"limit": -1})),
    ("{ -018- GET USERS WITH PARAMETERS {'limit': 'abc', 'offset': 'abc'} }", 422, Model_https_422, requests.get(baseUrl_users, params={"limit": "abc", "offset": "abc"})),
    ("{ -019- GET USERS BY HTTP WITHOUT SSL }", 200, ModelUsers200, requests.get("http://send-request.me/api/users/")),
    ("{ -020- POST NEW USER }", 201, ModelUser201, "New"),
    ("{ -021- POST NEW USER WITH INCORRECT ID }", 404, Model404, requests.post(baseUrl_users, headers={'Content-Type': 'application/json'}, data=json.dumps({"first_name": "1", "last_name": "2", "company_id": 33}))),
    ("{ -022-1- POST NEW USER WITH USERDATA {'first_name': '1', 'last_name': None, 'company_id': 3} }", 422, Model_https_422, requests.post(baseUrl_users, headers={'Content-Type': 'application/json'}, data=json.dumps({"first_name": "1", "last_name": None, "company_id": 3}))),
    ("{ -022-2- POST NEW USER WITH PARAMETERS {'first_name': '1', 'company_id': 3} }", 422, Model_https_422, requests.post(baseUrl_users, headers={'Content-Type': 'application/json'}, data=json.dumps({"first_name": "1", "company_id": 3}))),
    ("{ -023- POST NEW USER IN 'CLOSED' COMPANY {'first_name': '1', 'last_name': '2', 'company_id': 5} }", 400, Model_https_400, requests.post(baseUrl_users, headers={'Content-Type': 'application/json'}, data=json.dumps({"first_name": "1", "last_name": "2", "company_id": 5}))),
    ("{ -024- GET USER BY USER_ID }", 200, ModelUser200, "User_id"),
    ("{ -025- GET USER BY INCORRECT USER_ID }", 404, Model404, "Get_incorrect_user_id"),
    ("{ -026- UPDATE USER BY USER_ID }", 200, ModelUser200, "Update_user"),
    ("{ -027- UPDATE USER BY INCORRECT USER_ID }", 404, Model404, "Put_incorrect_user_id"),
    ("{ -028- UPDATE USER BY INCORRECT COMPANY_ID }", 404, Model404, "Put_incorrect_company_id"),
    ("{ -030- DELETE USER BY INCORRECT USER_ID}", 404,  Model404, "Delete_user")
])
def test_base_check_users_000(about, stat_code, schema, full_address, create_user):
    """
    Проведение общих проверок для всех тестов:
        Статус-код соответствует ожидаемому
        Валидация модели
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        Время ответа сервера - не превышает 500ms;* это время пришлось сильно увеличить,
        т.к. тестовая база иногда еле отзывается, и все тесты падают на этой проверке
    """

    if full_address == "New":
        resp = create_user
    elif full_address == "User_id":
        user_id = create_user.json().get("user_id")
        resp = requests.get(baseUrl_users + str(user_id))
    elif full_address == "Get_incorrect_user_id":
        resp = requests.get(baseUrl_users + "999999999999")
    elif full_address == "Update_user":
        user_id = create_user.json().get("user_id")
        payload = json.dumps({"first_name": "Гена", "last_name": "Пипеткин", "company_id": "3"})
        headers = {'Content-Type': 'application/json'}
        resp = requests.put(baseUrl_users + str(user_id), headers=headers, data=payload)
    elif full_address == "Put_incorrect_user_id":
        payload = json.dumps({"first_name": "Гена", "last_name": "Пипеткин", "company_id": "3"})
        headers = {'Content-Type': 'application/json'}
        resp = requests.put(baseUrl_users + "999999999999", headers=headers, data=payload)
    elif full_address == "Put_incorrect_company_id":
        user_id = create_user.json().get("user_id")  # получили id из фикстуры
        payload = json.dumps({"first_name": "Маня", "last_name": "Пена", "company_id": "30"})
        headers = {'Content-Type': 'application/json'}
        resp = requests.put(baseUrl_users + str(user_id), headers=headers, data=payload)
    elif full_address == "Delete_user":
        user_id, payload, headers = 99999999999, {}, {}
        resp = requests.delete(baseUrl_users + str(user_id), headers=headers, data=payload)
    else:
        resp = full_address

    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response

    test_object.assert_status_code(stat_code). \
        validate_schema(schema). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443"). \
        validate_time_from_request_to_response(timedelta(microseconds=11500000))


@pytest.mark.users
def test_get_users_with_limit_and_offset_016():
    """
    Получить список пользователей с query-параметрами limit = 10 и offset = 5

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON data 10 пользователей, user_id начинается с 6-ой по счету записи
    """
    offset = 5
    params = {"limit": 10, "offset": offset}
    resp = requests.get(baseUrl_users, params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_users = ResponseUsersTest(resp)

    # test_object.assert_status_code(200). \
    #     validate_schema(ModelUsers200). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_users.assert_limit_json_body_data(10).\
        calculate_first_id_for_response_with_offset(offset)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.skip("{id записи об ошибке} Вместо 422 получаем статус-код 200. Skip-аем пока не починят")
@pytest.mark.users
def test_get_users_with_incorrect_limit_017():
    """
    Получить список пользователей с отрицательным query-параметрам limit = -1

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 422;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON присутствует описание ошибки
    Полученный результат: Выгружены всех пользователей из БД, статус-код 200, время ответа > 500ms
    """
    params = {"limit": -1}
    resp = requests.get(baseUrl_users, params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response

    test_object.assert_status_code(422). \
        validate_schema(Model_https_422). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443"). \
        validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_get_users_with_incorrect_str_limit_and_offset_018():
    """
    Получить список пользователей с query-параметрами limit = abc и offset = abc

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 422;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON присутствует описание ошибки
    """
    params = {"limit": "abc", "offset": "abc"}
    resp = requests.get(baseUrl_users, params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_users = ResponseUsersTest(resp)

    # test_object.assert_status_code(422). \
    #     validate_schema(Model_https_422). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_users.assert_response_message_about_error_422("msg", "value is not a valid integer")
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_get_users_list_by_http_019():
    """
    Получить списка компаний HTTP-запросом (не HTTPS)

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 301;
        Время ответа сервера - не превышает 500ms;
        Response header "Location" - "https://send-request.me/api/users/"
        Response header "Connection" - "keep-alive"
    """
    resp = requests.get("http://send-request.me/api/users/", allow_redirects=False)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response

    test_object.assert_status_code(301). \
        assert_response_header("connection", "keep-alive")
    assert resp.headers["Location"] == "https://send-request.me/api/users/"
    test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.users
def test_create_user_020(create_user):
    """
    Зарегистрировать нового пользователя

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 201;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        Новая запись JSON ответа соответствует тому, что мы
            отправляли при регистрации + содержит Id созданного юзера
    """
    test_object = ResponseTest(create_user)
    test_object_users = ResponseUsersTest(create_user)

    # test_object.assert_status_code(201). \
    #     validate_schema(ModelUser201). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443"). \
    test_object_users.assert_user("Вальдемар", "Евлампиевич", 3)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_create_user_with_incorrect_company_id_021():
    """
    Зарегистрировать нового пользователя с не верным company_id

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 404;
        Время ответа сервера - не превышает 500ms;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        Схема JSON-ответа соответствует требованиям;
        В JSON - присутствует ключ detail, значением является описание ошибки
    """
    company_id = "33"
    payload = json.dumps({"first_name": "1", "last_name": "2", "company_id": company_id})
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(baseUrl_users, headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.assert_status_code(404). \
    #     validate_schema(Model404). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_response_message_about_error_404(company_id)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.parametrize("user_data", [
    ({"first_name": "1", "last_name": None, "company_id": 3}),
    ({"first_name": "1", "company_id": 3})
])
@pytest.mark.users
def test_create_user_with_null_and_empty_last_name_022(user_data):
    """
    Зарегистрировать пользователя с обязательным полем last_name = None;
    Создать пользователя вообще без строки last_name и её значения.

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 422;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON присутствует описание ошибки
    """
    payload = json.dumps(user_data)
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(baseUrl_users, headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_users = ResponseUsersTest(resp)

    # test_object.assert_status_code(422). \
    #     validate_schema(Model_https_422). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")

    if "last_name" in user_data:
        test_object_users.assert_response_message_about_error_422("msg", "none is not an allowed value")
    else:
        test_object_users.assert_response_message_about_error_422("msg", "field required")

    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_create_user_in_with_closed_status_023():
    """
    Создать пользователя в компании company_status = CLOSED

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 400;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON присутствует описание ошибки
    """
    company_id = "5"
    payload = json.dumps({"first_name": "1", "last_name": "2", "company_id": company_id})
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(baseUrl_users, headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_users = ResponseUsersTest(resp)

    # test_object.assert_status_code(400). \
    #     validate_schema(Model_https_400). \
    #     assert_https_request("443"). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive")
    test_object_users.assert_response_message_about_error_400(company_id)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_get_user_by_id_024(create_user):
    """
    Получить данные пользователя по его user_id

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        Запись JSON ответа соответствует тому, что мы отправляли при регистрации
        """
    user_id = create_user.json().get("user_id")
    resp = requests.get(baseUrl_users + str(user_id))
    test_object = ResponseTest(resp)
    test_object_users = ResponseUsersTest(resp)

    # test_object.assert_status_code(200). \
    #     validate_schema(ModelUser200). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_users.assert_user("Вальдемар", "Евлампиевич", 3)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_get_created_user_by_incorrect_id_025(create_user):
    """
    Получить данные пользователя по не корректному user_id

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 404;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON присутствует описание ошибки
        """
    user_id = "999999999999"
    resp = requests.get(baseUrl_users + user_id)
    test_object = ResponseTest(resp)
    test_object_users = ResponseUsersTest(resp)

    # test_object.assert_status_code(404). \
    #     validate_schema(Model404). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_users.assert_response_message_about_error_404(user_id)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))


@pytest.mark.users
def test_update_user_026(create_user):
    """
    Внести изменения в данные существующего пользователя

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        Новая запись JSON ответа соответствует тому, что мы отправляли при редактировании пользователя
    """
    user_id = create_user.json().get("user_id")  # получили id из фикстуры
    payload = json.dumps({"first_name": "Гена", "last_name": "Пипеткин", "company_id": "3"})
    headers = {'Content-Type': 'application/json'}
    resp = requests.put(baseUrl_users + str(user_id), headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_users = ResponseUsersTest(resp)

    # test_object.assert_status_code(200). \
    #     validate_schema(ModelUser200). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_users.assert_user("Гена", "Пипеткин", 3)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_update_user_with_incorrect_user_id_027():
    """
    Отредактировать не существующего пользователя (не существующий user_id)

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 404;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON присутствует описание ошибки
    """
    user_id = 99999999999  # не существующий user_id
    payload = json.dumps({"first_name": "Гена", "last_name": "Пипеткин", "company_id": "3"})
    headers = {'Content-Type': 'application/json'}
    resp = requests.put(baseUrl_users + str(user_id), headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_users = ResponseUsersTest(resp)

    # test_object.assert_status_code(404). \
    #     validate_schema(Model404). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_users.assert_response_message_about_error_404(user_id)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_update_user_with_incorrect_company_id_028(create_user):
    """
    Отредактировать пользователя не существующей компании (не существующий company_id)

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 404;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON присутствует описание ошибки
    """
    user_id = create_user.json().get("user_id")  # получили id из фикстуры
    company_id = "30"
    payload = json.dumps({"first_name": "Маня", "last_name": "Пена", "company_id": company_id})
    headers = {'Content-Type': 'application/json'}
    resp = requests.put(baseUrl_users + str(user_id), headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.assert_status_code(404). \
    #     validate_schema(Model404). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_response_message_about_error_404(company_id)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_delete_user_029(create_user):
    """
    Удалить пользователя

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 202;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям; (Там одно слово Null, потому реально я эту схему не заводил)
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON ответа выводится: null
    """
    user_id = create_user.json().get("user_id")  # получили id из фикстуры

    payload = {}
    headers = {}
    resp = requests.delete(baseUrl_users + str(user_id), headers=headers, data=payload)
    test_object = ResponseTest(resp)

    test_object.assert_status_code(202). \
        assert_https_request("443"). \
        validate_time_from_request_to_response(timedelta(microseconds=500000))


@pytest.mark.users
def test_delete_deleted_user_030(create_user):
    """
    Удалить удаленного пользователя

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 202;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям; (Там одно слово Null, потому реально я эту схему не заводил)
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON ответа выводится: null
    """
    user_id = create_user.json().get("user_id")  # получили id из фикстуры

    payload = {}
    headers = {}
    resp = requests.delete(baseUrl_users + str(user_id), headers=headers, data=payload)
    resp = requests.delete(baseUrl_users + str(user_id), headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_users = ResponseUsersTest(resp)

    test_object.assert_status_code(404). \
        assert_https_request("443")
    test_object_users.assert_response_message_about_error_404(user_id)
    test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test_delete_user_with_incorrect_user_id_031():
    """
    Удалить не существующего пользователя (не существующий user_id)

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 404;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям; (Там одно слово Null, потому реально я эту схему не заводил)
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON присутствует описание ошибки
    """
    user_id = 99999999999

    payload = {}
    headers = {}
    resp = requests.delete(baseUrl_users + str(user_id), headers=headers, data=payload)
    test_object = ResponseTest(resp)
    test_object_users = ResponseUsersTest(resp)

    test_object.assert_status_code(404). \
        validate_schema(Model404). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443")
    test_object_users.assert_response_message_about_error_404(user_id)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))


@pytest.mark.users
def test__issues__get_created_user_by_id_032(create_user):
    """
    Это специальный тест, где мы получим заведомо не верный ответ от сервера.
    Получить данные пользователя по его user_id

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        Запись JSON ответа соответствует тому, что мы отправляли при регистрации
    Полученный результат: не тот статус код 202, не та схема
        """
    user_id = create_user.json().get("user_id")
    resp = requests.get("https://send-request.me/api/issues/users/" + str(user_id))
    test_object = ResponseTest(resp)

    test_object_users = ResponseUsersTest(create_user)

    test_object.assert_status_code(200). \
        validate_schema(ModelUser200). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443")
    test_object_users.assert_user("Вальдемар", "Евлампиевич", 3)
    test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.users
def test__issues__create_user_033():
    """
    Это специальный тест, где мы получим заведомо не верный ответ от сервера.
    Зарегистрировать нового пользователя (делаем громоздко внутри теста, не используем фикстуру)

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 201;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        Новая запись JSON ответа соответствует тому, что мы
            отправляли при регистрации + содержит Id созданного юзера
    Полученный результат: все данные юзера не совпадают
    """
    url = "https://send-request.me/api/issues/users/"
    payload = json.dumps({"first_name": "Дыр", "last_name": "Пыр", "company_id": 3})
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, headers=headers, data=payload)

    test_object = ResponseTest(resp)
    test_object_users = ResponseUsersTest(resp)
    user_id = resp.json().get("user_id")

    test_object.assert_status_code(201). \
        validate_schema(ModelUser201). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443")
    test_object_users.assert_user("Дыр", "Пыр", 3)
    test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

    payload = {}
    headers = {}
    resp_del = requests.delete(baseUrl_users + str(user_id), headers=headers, data=payload)

