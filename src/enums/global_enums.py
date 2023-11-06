from enum import Enum

class GlobalErrorMessages(Enum):
    WRONG_SCHEMA = "Incorrect JSON-schema"
    WRONG_STATUS_CODE = "Status code != 200"
    WRONG_RESPONSE_HEADER_CONTENT_TYPE = "content-type != application/json"
    WRONG_RESPONSE_HEADER_CONNECTION = "connection != keep-alive"
    WRONG_DEFAULT_COMPANY_STATUS = "Company status != ACTIVE"
    WRONG_DEFAULT_META_SETTINGS = "Respons have incorrect meta-settings"