from typing import Any, List, Optional

from pydantic import BaseModel, field_validator
from src.enums.schema_enums import Company_stats, CompanyErrors


class Meta(BaseModel):
    limit: int = 0
    offset: int = 0
    total: int


class Datum(BaseModel):
    first_name: Optional[str] = None
    last_name: str
    company_id: Any = 0
    user_id: int


class ModelUsers200(BaseModel):
    meta: Meta
    data: List[Datum]