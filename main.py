from fastapi import FastAPI, Depends
from database import Base, engine
from auth.router import router as auth_router
from auth.dependencies import get_current_user
from models import User
from users.router import router as users_router



# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
def root():
    return {"message": "Auth API running"}

@app.get("/profile")
def profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }
