from fastapi import APIRouter, HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token

from config import settings
from models import User
from schemas import AuthResponseDto, GoogleLoginDto, LoginDto, RegisterDto
from security import create_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponseDto)
async def register(dto: RegisterDto) -> AuthResponseDto:
    username = dto.username.strip().lower()

    existing = await User.find_one(User.username == username)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken.",
        )

    user = User(
        name=dto.name.strip(),
        username=username,
        password_hash=hash_password(dto.password),
    )
    await user.insert()

    return AuthResponseDto(token=create_token(user), name=user.name, username=user.username)


@router.post("/login", response_model=AuthResponseDto)
async def login(dto: LoginDto) -> AuthResponseDto:
    username = dto.username.strip().lower()
    user = await User.find_one(User.username == username)

    if user is None or user.password_hash is None or not verify_password(dto.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return AuthResponseDto(token=create_token(user), name=user.name, username=user.username)


@router.post("/google", response_model=AuthResponseDto)
async def google_login(dto: GoogleLoginDto) -> AuthResponseDto:
    """Verify Google's ID token before issuing this app's access token."""
    if not settings.google_client_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Google sign-in has not been configured on the server.")
    try:
        identity = id_token.verify_oauth2_token(dto.credential, requests.Request(), settings.google_client_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google credential.")
    if not identity.get("email_verified") or not identity.get("sub") or not identity.get("email"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google account email is not verified.")

    google_id = identity["sub"]
    email = identity["email"].strip().lower()
    user = await User.find_one(User.google_id == google_id)
    if user is None:
        if await User.find_one(User.username == email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An existing account uses this email. Contact support to link it to Google.")
        user = User(name=identity.get("name", email).strip()[:100], username=email, google_id=google_id)
        await user.insert()
    return AuthResponseDto(token=create_token(user), name=user.name, username=user.username)
