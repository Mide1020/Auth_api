from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import secrets
from jose import jwt, JWTError
from schemas import ForgotPasswordRequest, ResetPasswordRequest
from database import get_db
from models import User
from schemas import UserCreate, UserOut, Token, RefreshTokenRequest, UserRegisterResponse
from auth.utils import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordRequestForm
from auth.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])

# ================= REGISTER =================
@router.post("/register", response_model=UserRegisterResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # check if email exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # create inactive user
    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        is_active=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # create verification token (1 hour expiry)
    verification_token = create_access_token(
        {"sub": new_user.email},
        expires_delta=timedelta(hours=1)
    )

    verification_link = f"http://localhost:8000/auth/verify?token={verification_token}"

    # TEMP: print link (later send via email)
    print("Verification link:", verification_link)

    #return new_user
    return {
    "id": new_user.id,
    "email": new_user.email,
    "is_active": new_user.is_active,
    "verification_token": verification_token
}


# ================= LOGIN =================
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    access_token = create_access_token({"sub": user.email})
    refresh_token = secrets.token_urlsafe(32)

    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ================= REFRESH TOKEN =================
@router.post("/refresh", response_model=Token)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.refresh_token == data.refresh_token).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token({"sub": user.email})
    new_refresh_token = secrets.token_urlsafe(32)

    user.refresh_token = new_refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


# ================= EMAIL VERIFICATION =================
@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        return {"message": "User already verified"}

    user.is_active = True
    user.refresh_token = None
    db.commit()

    return {"message": "Email verified successfully"}

#=================Forgotten password==========
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"message": "If account exists, reset link sent"}

    reset_token = create_access_token(
        {"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )

    user.reset_token = reset_token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)
    db.commit()

    reset_link = f"http://localhost:8000/auth/reset-password?token={reset_token}"
    print("Password reset link:", reset_link)

    return {"message": "Password reset link sent"}

#======================RESET PASSWORD =======================
@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    from jose import jwt, JWTError
    from auth.utils import SECRET_KEY, ALGORITHM

    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user or user.reset_token != data.token:
        raise HTTPException(status_code=400, detail="Invalid token")

    if user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")

    user.password_hash = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()

    return {"message": "Password reset successful"}


#=============LOGOUT ROUTER =======
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Logs out the current user by invalidating their refresh token.
    """
    current_user.refresh_token = None
    db.commit()
    return {"message": "Successfully logged out"}



