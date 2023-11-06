from enum import Enum

class Company_stats(Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    BANKRUPT = "BANKRUPT"

class CompanyErrors(Enum):
    WRONG_COMANY_ID = "Company_id is not correct/не корректное id"
    WRONG_COMPANY_NAME = "First_letter_must_be_a_Capital/первая буква должна быть заглавная"
    WRONG_COMPANY_STATUS = "Incorrect company status/не верный статус компании"
    WRONG_HEADER_Content_Type = "Mistake! 'Content-Type' != 'application/json'"