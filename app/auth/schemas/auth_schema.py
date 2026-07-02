import re
from pydantic import BaseModel, field_validator, ValidationInfo
from fastapi import Body


PHONE_REGEX = re.compile(r"^09\d{9}$")

class UserRegisterSchema(BaseModel):
    phone_number: str = Body(..., description="user phone for auth", title="PhoneNumber", max_length=11)

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v:str, info: ValidationInfo) -> str:
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid Phone Number")
        return v
    
class UserLoginSchema(UserRegisterSchema):
    pass


class UserVerifiedSchema(BaseModel):
    otp: str = Body(..., description="user otp for auth", title="OTP", max_length=4)
    phone_number: str = Body(..., description="user phone for auth", title="PhoneNumber", max_length=11)

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v:str, info: ValidationInfo) -> str:
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid Phone Number")
        return v
    

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v:str, info: ValidationInfo) -> str:
        if not v.isdigit() or len(v) != 4:
            raise ValueError("Invalid Type OTP")
        return v