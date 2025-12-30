from pydantic import BaseModel, EmailStr
from typing import Optional


# ================= USER =================
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True


# ================= TOKEN =================
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
#==============pPASSWORD RESET=============

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

