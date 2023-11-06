from pydantic import BaseModel


class ModelAuth200(BaseModel):
    user_name: str
    email_address: str
    valid_till: str