from pydantic import BaseModel, field_validator
from typing import List

from src.enums.schema_enums import Company_stats


class Ctx(BaseModel):
    enum_values: List[Company_stats] = None
    limit_value: int = 0

class Data_from_detail(BaseModel):
    loc: list[str]
    msg: str
    type: str
    ctx: Ctx = None  # не обязательное поле

class Model_https_422(BaseModel):
    detail: List[Data_from_detail]

