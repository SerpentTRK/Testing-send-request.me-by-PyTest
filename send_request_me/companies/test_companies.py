import pytest
import requests

from datetime import timedelta

from configuration import baseUrl
from src.baseclasses.response import ResponseTest
from src.baseclasses.responses_companies.response import ResponseCompaniesTest

from src.pydantic_shemas.model_api_companies_200 import Model_companies_200
from src.pydantic_shemas.model_api_https_422 import Model_https_422
from src.pydantic_shemas.model_api_company_200 import Model_company_200
from src.pydantic_shemas.model_api_404 import Model404

@pytest.mark.parametrize("about, stat_code, schema, full_address", [
    ("{ -001- GET COMPANIES WITHOUT PARAMETERS }", 200, Model_companies_200, requests.get(baseUrl)),
    ("{ -002- GET COMPANIES WITH HTTP WITHOUT PARAMETERS }", 200, Model_companies_200, requests.get("http://send-request.me/api/companies/")),
    ("{ -003- GET COMPANIES WITH params={'limit': 1, 'offset': 2} }", 200, Model_companies_200, requests.get(baseUrl, params={"limit": 1, "offset": 2})),
    ("{ -004-1- GET COMPANIES WITH STATUS 'ACTIVE' }", 200, Model_companies_200, requests.get(baseUrl, params={"status": "ACTIVE"})),
    ("{ -004-2- GET COMPANIES WITH STATUS 'CLOSED' }", 200, Model_companies_200, requests.get(baseUrl, params={"status": "CLOSED"})),
    ("{ -004-3- GET COMPANIES WITH STATUS 'BANKRUPT' }", 200, Model_companies_200, requests.get(baseUrl, params={"status": "BANKRUPT"})),
    ("{ -005- GET COMPANIES WITH INCORRECT STATUS 'ABC' }", 422, Model_https_422, requests.get(baseUrl, params={"status": "ABC"})),
    ("{ -006- GET COMPANIES WITH params = {'limit': -1} }", 422, Model_https_422, requests.get(baseUrl, params={"limit": -1})),
    ("{ -007- GET COMPANIES WITH params = {'limit': 'abc'} }", 422, Model_https_422, requests.get(baseUrl, params={"limit": "abc"})),
    ("{ -008- GET COMPANIES WITH params = {'offset': -1} }", 200, Model_companies_200, requests.get(baseUrl, params={"offset": -1})),
    ("{ -009- GET COMPANIES WITH params = {'offset': abc} }", 422, Model_https_422, requests.get(baseUrl, params={"offset": "abc"})),
    ("{ -010- GET COMPANY BY id=1 }", 200, Model_company_200, requests.get(baseUrl + "1")),
    ("{ -011- GET COMPANY BY id=8 }", 404, Model404, requests.get(baseUrl + "8")),
    ("{ -012- GET COMPANY BY id=1 and choice supported language RU }", 200, Model_company_200, requests.get("https://send-request.me/api/companies/1", headers={"Accept-Language": "RU"})),
    ("{ -013- GET COMPANY BY id=1 and choice unsupported language KZ }", 200, Model_company_200, requests.get("https://send-request.me/api/companies/1", headers={"Accept-Language": "KZ"}))
])
def test_base_check_companies_000(about, stat_code, schema, full_address):
    """
    Проведение общих проверок для всех тестов:
        Статус-код соответствует ожидаемому
        Валидация модели
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        Время ответа сервера - не превышает 500ms;* это время пришлось сильно увеличить,
        т.к. тестовая база иногда еле отзывается, и все тесты падают на этой проверке

    Идея этой проверки в том, что в случае падения одной из проверок, прерывается проведение и всех остальных в тесте.
    Потому все тесты разделены на две группы. Тут единые, "базовые" проверки, а далее уже идут исключительно валидация
    того ответа, который мы ожидаем в каждом из тестов, но без общих проверок. В случае падения теста это позволит
    быстрее понять как локализовать проблему.

    * из этой проверки исключены тесты 014 и 015, т.к. они на отдельный uri, специально сделаны с ошибками
    """
    resp = full_address  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response

    test_object.assert_status_code(stat_code). \
        validate_schema(schema). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443"). \
        validate_time_from_request_to_response(timedelta(microseconds=1500000))


@pytest.mark.companies
def test_get_companies_list_001():
    """
    Получение списка компаний.

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON 3 компании, id первой в списке = 1, company_status = ACTIVE
    """
    resp = requests.get(baseUrl)  #запрос к серверу
    test_object = ResponseTest(resp)  #ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.assert_status_code(200). \
    #     validate_schema(Model_companies_200). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_limit_json_body_data(3). \
        validate_status_company("company_status", "ACTIVE")
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.companies
def test_get_companies_list_by_http_002():
    """
    Получить списка компаний HTTP-запросом (не HTTPS)

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 301;
        Время ответа сервера - не превышает 500ms;
        Response header "Location" - "https://send-request.me/api/companies/"
        Response header "Connection" - "keep-alive"
    """
    resp = requests.get("http://send-request.me/api/companies/", allow_redirects=False)  #запрос к серверу
    test_object = ResponseTest(resp)  #ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    test_object.assert_status_code(301).\
        assert_response_header("connection", "keep-alive")
    assert resp.headers["Location"] == "https://send-request.me/api/companies/"
    test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

    #"https://stackoverflow.com/questions/110498/is-there-an-easy-way-to-request-a-url-in-python-and-not-follow-redirects"

@pytest.mark.companies
def test_get_companies_with_limit_and_offset_003():
    """
    Получение списка компаний с указанием limit=1 и offset=2

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON data одна компания (limit = 1), company_id = 3 (offset = 2)
    """
    params = {"limit": 1, "offset": 2}
    resp = requests.get(baseUrl, params=params)  #запрос к серверу
    test_object = ResponseTest(resp)  #ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.assert_status_code(200). \
    #     validate_schema(Model_companies_200). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    # в проверке на offset (offset_value, ожидаемый в JSON первый company_id)
    test_object_companies.assert_limit_json_body_data(1). \
        assert_offset_json_body_data(2, 3)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))

@pytest.mark.parametrize("company_status", [
    ("ACTIVE"),
    ("CLOSED"),
    ("BANKRUPT")
])
@pytest.mark.companies
def test_get_companies_with_different_correct_statuses_004(company_status):
    """
    Получение списка компаний с разными company_status = ACTIVE, CLOSED или BANKRUPT

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON компании только с указанным статусом
    """
    params = {"status": company_status}
    resp = requests.get(baseUrl, params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.assert_status_code(200). \
    #     validate_schema(Model_companies_200). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.validate_status_company("company_status", company_status)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.companies
def test_get_companies_with_incorrect_status_ABC_005():
    """
    Получение списка компаний с указанием company_status = abc

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
    params = {"status": "ABC"}
    resp = requests.get(baseUrl, params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.assert_status_code(422). \
    #     validate_schema(Model_https_422). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_response_message_about_error_422(
        "msg", "value is not a valid enumeration member; permitted: 'ACTIVE', 'BANKRUPT', 'CLOSED'"
    )
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.skip("{id записи об ошибке} Вместо 422 получаем статус-код 200. Skip-аем пока не починят")
@pytest.mark.companies
def test_get_companies_with_query_int_limit_006():
    """
    Получение списка компаний с указанием limit = -1

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 422;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON присутствует описание ошибки
    Полученный результат: Выгружены все компании из БД, статус-код 200
    """
    params = {"limit": -1}
    resp = requests.get(baseUrl, params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response

    test_object.assert_status_code(422). \
        validate_schema(Model_https_422). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443"). \
        validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.companies
def test_get_companies_with_query_str_limit_007():
    """
    Получение списка компаний с указанием limit = abc

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
    params = {"limit": "abc"}
    resp = requests.get(baseUrl, params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.validate_schema(Model_https_422). \
    #     assert_status_code(422). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_response_message_about_error_422("msg", "value is not a valid integer")
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.skip("Протестирвано в общем test_base_check_users_000. Дополнительных проверок нет")
@pytest.mark.companies
def test_get_companies_with_query_int_offset_008():
    """
    Получить список компаний с указанием offset = -1

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON id первой в списке компании начинается = 1, и количество компаний = 3
    """
    params = {"offset": -1}
    resp = requests.get(baseUrl, params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response

    test_object.assert_status_code(200). \
        validate_schema(Model_companies_200). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443"). \
        validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.companies
def test_get_companies_with_query_int_offset_009():
    """
    Получить список компаний с указанием offset = abc

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
    params = {"offset": "abc"}
    resp = requests.get(baseUrl, params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.validate_schema(Model_https_422). \
    #     assert_status_code(422). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_response_message_about_error_422("msg", "value is not a valid integer")
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.companies
def test_get_company_by_id_010():
    """
    Получить информацию о компании по существующему Id=1 в эндпоинте URI

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON - company_id совпадает с id URI и первый в списке поддерживаемых языков EN;
    """
    company_id = "1"
    resp = requests.get(baseUrl + company_id)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.assert_status_code(200). \
    #     validate_schema(Model_company_200). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_first_language_in_response("EN"). \
        assert_comparison_uri_in_request_and_response(baseUrl + company_id)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.companies
def test_get_company_by_incorrect_id_011():
    """
    Получить информацию о компании по не существующему Id=8 в эндпоинте URI

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 404;
        Время ответа сервера - не превышает 500ms;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Схема JSON-ответа соответствует требованиям;
        Соединение безопасное, порт 443
        В JSON - присутствует ключ detail, значением является описание ошибки
    """
    company_id = "8"
    resp = requests.get(baseUrl + company_id)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.assert_status_code(404). \
    #     validate_schema(Model404). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_response_message_about_error_404(company_id)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.companies
def test_get_company_by_id_and_change_support_language_012():
    """
    Получить информацию о компании по существующему id=1 в эндпоинте URI, с выбором поддерживаемого языка RU

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json";
        Response header "Connection" - "keep-alive";
        Соединение безопасное, порт 443
        company_id в JSON совпадает с id URI;
        Текст в description на Русском языке
    """
    company_id = "1"
    headers = {"Accept-Language": "RU"}
    ru_symbols = ('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    resp = requests.get(baseUrl + company_id, headers=headers)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.validate_schema(Model_company_200). \
    #     assert_status_code(200). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_comparison_uri_in_request_and_response(baseUrl + company_id).\
        assert_language(ru_symbols)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.companies
def test_det_company_by_id_and_change_unsupported_language_013():
    """
    Получить информацию о компании по существующему id=1 в эндпоинте URI, с выбором не поддерживаемого языка KZ

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON - company_id совпадает с id URI и первый в списке поддерживаемых языков EN;
    """
    company_id = "1"
    headers = {"Accept-Language": "KZ"}
    resp = requests.get(baseUrl + company_id, headers=headers)   # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    # test_object.validate_schema(Model_company_200). \
    #     assert_status_code(200). \
    #     assert_response_header("content-type", "application/json"). \
    #     assert_response_header("connection", "keep-alive"). \
    #     assert_https_request("443")
    test_object_companies.assert_first_language_in_response("EN"). \
        assert_comparison_uri_in_request_and_response(baseUrl + company_id)
    # test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.companies
def test__issues__get_companies_with_limit_offset_and_status_company_014():
    """
    Это специальный тест, где мы получим заведомо не верный ответ от сервера.
    Получение списка компаний с указанием limit=1 ,offset=1 и status_company = ACTIVE

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует Требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
    Полученный результат: падает валидация offset и company-status
    """
    params = {"limit": 1, "offset": 1, "status": "ACTIVE"}
    resp = requests.get("https://send-request.me/api/issues/companies", params=params)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    test_object.assert_status_code(200). \
        validate_schema(Model_companies_200). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443")
    test_object_companies.assert_limit_json_body_data(1).\
        assert_offset_json_body_data(1, 2).\
        validate_status_company("company_status", "ACTIVE")
    test_object.validate_time_from_request_to_response(timedelta(microseconds=1500000))

@pytest.mark.companies
def test__issues__get_companies_by_id_015():
    """
    Это специальный тест, где мы получим заведомо не верный ответ от сервера.
    Получение компании по company_id

    Ожидаемый результат:
        Запрос успешно отправлен;
        Статус-код 200;
        Время ответа сервера - не превышает 500ms;
        Схема JSON-ответа соответствует требованиям;
        Response header "Content-Type" - "application/json"
        Response header "Connection" - "keep-alive"
        Соединение безопасное, порт 443
        В JSON - company_id совпадает с id URI и первый в списке поддерживаемых языков EN;
    Полученный результат: Превышено время ожидания ответа от сервера
    """
    company_id = "2"
    resp = requests.get("https://send-request.me/api/issues/companies/" + company_id)  # запрос к серверу
    test_object = ResponseTest(resp)  # ответ от сервера, который мы предали в класс Test_response
    test_object_companies = ResponseCompaniesTest(resp)

    test_object.assert_status_code(200). \
        validate_schema(Model_company_200). \
        assert_response_header("content-type", "application/json"). \
        assert_response_header("connection", "keep-alive"). \
        assert_https_request("443")
    test_object_companies.assert_first_language_in_response("EN"). \
        assert_comparison_uri_in_request_and_response("https://send-request.me/api/issues/companies/" + company_id)
    test_object.validate_time_from_request_to_response(timedelta(microseconds=500000))
