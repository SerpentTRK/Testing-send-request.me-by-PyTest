from pydantic import BaseModel, HttpUrl, UUID4, EmailStr

from pydantic.types import PastDate, FutureDate, List, PaymentCardNumber
from pydantic.networks import IPv4Address, IPv6Address
from pydantic.color import Color

from src.enums.schema_enums import Company_stats

computer = {
    "id": 21,
    "status": "ACTIVE",
    "activated_at": "2013-06-01",
    "expiration_at": "2040-06-01",
    "host_v4": "91.192.222.17",
    "host_v6": "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
    "detailed_info": {
        "physical": {
            "color": 'green',
            "photo": 'https://images.unsplash.com/photo-1587831990711-23ca6441447b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MXx8ZGVza3RvcCUyMGNvbXB1dGVyfGVufDB8fDB8fA%3D%3D&w=1000&q=80',
            "uuid": "73860f46-5606-4912-95d3-4abaa6e1fd2c"
        },
        "owners": [{
            "name": "Stephan Nollan",
            "card_number": "4000000000000002",
            "email": "shtephan.nollan@gmail.com",
        }]
    }
}


class Owners(BaseModel):
    name: str
    card_number: PaymentCardNumber  # валидация карточного номера
    email: EmailStr  # валидация электронной почты, но надо поставить еще библиотеку для этой валидации. Гугли мануал


class Physical(BaseModel):
    color: Color   # вшитая валидация цвета
    photo: HttpUrl  # валидация ссылки
    uuid: UUID4


class Detailed_info(BaseModel):
    physical: Physical
    owners: List[Owners]


class Computer(BaseModel):
    id: int
    status: Company_stats  # это уже знакомые нам enum-ы
    activated_at: PastDate  # при валидации будет проверяться, что это прошедшая дата
    expiration_at: FutureDate  # при валидации будет проверяться что эта дата еще не наступила
    host_v4: IPv4Address  # валидация IP v4
    host_v6: IPv6Address  # валидация IP v6
    detailed_info: Detailed_info

comp = Computer.model_validate(computer)

print(comp)
print(comp.detailed_info)
print(comp.detailed_info.owners)  # у нас же там []
for dicts in comp.detailed_info.owners:
    print(dicts)

print(comp.detailed_info.physical.photo)  # это вариации resp.json().get("").get("")... (может и без .json() )
print(comp.detailed_info.physical.photo.host)















