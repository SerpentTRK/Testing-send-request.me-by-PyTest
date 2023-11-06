from pydantic import BaseModel


class Detail(BaseModel):
    reason: str


class Model_https_400(BaseModel):
    detail: Detail