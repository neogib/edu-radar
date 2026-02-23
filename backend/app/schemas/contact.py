from typing import Annotated

from pydantic import EmailStr, Field, StringConstraints

from app.schemas.base import CustomBaseModel

NameStr = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]
TopicStr = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)
]
MessageStr = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
]
EmailAddressStr = Annotated[EmailStr, Field(max_length=254)]
TurnstileTokenStr = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2048)
]


class ContactSubmitRequest(CustomBaseModel):
    name: NameStr
    email: EmailAddressStr
    topic: TopicStr
    message: MessageStr
    turnstile_token: TurnstileTokenStr


class ContactSubmitResponse(CustomBaseModel):
    success: bool
