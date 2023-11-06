from pydantic import BaseModel, field_validator


class Detail(BaseModel):
    reason: str

class Model404(BaseModel):
    detail: Detail