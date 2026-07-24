from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.logout import LogoutUseCase
from app.application.use_cases.request_otp import OTP_TTL_SECONDS, RequestOtpUseCase
from app.application.use_cases.verify_otp import VerifyOtpUseCase
from app.domain.entities.user import User
from app.presentation.dependencies import (
    get_bearer_token,
    get_current_user,
    get_logout_use_case,
    get_request_otp_use_case,
    get_verify_otp_use_case,
)
from app.presentation.schemas.auth import (
    OtpRequestRequest,
    OtpRequestResponse,
    OtpVerifyRequest,
    OtpVerifyResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request", response_model=OtpRequestResponse)
async def request_otp(
    payload: OtpRequestRequest,
    use_case: Annotated[RequestOtpUseCase, Depends(get_request_otp_use_case)],
) -> OtpRequestResponse:
    otp = await use_case.execute(payload.phone_number)
    return OtpRequestResponse(expires_in_seconds=OTP_TTL_SECONDS, otp_code=otp.code)


@router.post("/otp/verify", response_model=OtpVerifyResponse)
async def verify_otp(
    payload: OtpVerifyRequest,
    use_case: Annotated[VerifyOtpUseCase, Depends(get_verify_otp_use_case)],
) -> OtpVerifyResponse:
    user, session = await use_case.execute(payload.phone_number, payload.code)
    return OtpVerifyResponse(
        access_token=session.token,
        user=UserResponse(id=user.id, phone_number=user.phone_number),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(id=user.id, phone_number=user.phone_number)


@router.post("/logout", status_code=204)
async def logout(
    token: Annotated[str, Depends(get_bearer_token)],
    use_case: Annotated[LogoutUseCase, Depends(get_logout_use_case)],
) -> None:
    await use_case.execute(token)
