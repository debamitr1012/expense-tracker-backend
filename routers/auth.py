from fastapi import APIRouter, HTTPException, status

from models import User
from schemas import AuthResponseDto, LoginDto, RegisterDto
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

    if user is None or not verify_password(dto.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return AuthResponseDto(token=create_token(user), name=user.name, username=user.username)
