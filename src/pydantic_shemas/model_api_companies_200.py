from typing import List

from pydantic import BaseModel, field_validator
from src.enums.schema_enums import Company_stats, CompanyErrors

"""
id: int   int = None или int = "" или int = 0 - если это не обязательный параметр
company_id: int = Field(gt=0) - Это вариант валидации инструментами pydantic, то же
самое что валидировано ниже
"""

class Datum(BaseModel):
    company_id: int
    company_name: str
    company_address: str
    company_status: Company_stats  # аналог "enum": [ "ACTIVE", "CLOSED", "BANKRUPT"]

class Meta(BaseModel):
    limit: int
    offset: int
    total: int

class Model_companies_200(BaseModel):
    data: List[Datum]
    meta: Meta


@field_validator("company_id")
def check_company_id(cls, company_id):
    """
    Прооверка Id компании. Число не может быть отрицательным
    Это пример того, что тут тоже можно проводить валидацию, создавая свои валидаторы
    """
    if company_id > 0:
        return company_id
    else:
        raise ValueError('company_id имеет не корректное значение')