from pydantic import BaseModel


class ModelUser200(BaseModel):
    first_name: str = None
    last_name: str
    company_id: int = 0
    user_id: int