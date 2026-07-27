from pydantic import BaseModel, Field


class OtpRequestRequest(BaseModel):
    phone_number: str = Field(min_length=6, max_length=32)


class OtpRequestResponse(BaseModel):
    expires_in_seconds: int
    otp_code: str


class OtpVerifyRequest(BaseModel):
    phone_number: str = Field(min_length=6, max_length=32)
    code: str = Field(min_length=6, max_length=6)


class UserResponse(BaseModel):
    id: int
    phone_number: str
    is_admin: bool


class OtpVerifyResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
