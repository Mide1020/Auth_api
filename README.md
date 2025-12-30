# My FastAPI Authentication API

# Overview
This project is a backend API for user authentication using  FastAPI and Postgresql as database.  
It includes features like registration, email verification, login, refresh tokens, password reset, protected routes, and logout.  

Built for demo purpose to showcase backend skills.


# Features

1. Register: Users can register with email & password  but it inactive by default.(until email Verification)
2. Email Verification: Users must verify their email to activate their account  
3. Login: User can login by generating access and refresh tokens  
4. Token Refresh: Users can generate new access tokens using a valid refresh token , and it would be invalid once user logout 
5. Protected Routes: Only authenticated users with valid access tokens can access the route.
6. Logout: User can logout . 
7. Password Hashing: password are securely stored and  hashed using Argon2 
8. Optional: it has Forgot/Reset Password routes, where you can change password if forgotten.

---

# Authentication section


Register  Email Verification  Login Access Token  Protected Routes
       Refresh Token  Logout  Refresh Token invalidated.
Access tokens expire after 30 minutes