from fastapi import APIRouter, Depends, Request, FastAPI, File, UploadFile  # type: ignore
from slowapi import Limiter  # type: ignore
from slowapi.util import get_remote_address  # type: ignore
from slowapi.middleware import SlowAPIMiddleware  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from src.schemas.users import User
from src.services.auth import get_current_user, get_current_user_role
from src.database.db import get_db
from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.configuration.config import settings

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.add_middleware(SlowAPIMiddleware)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Return the current authenticated user.

    Args:
        request (Request): FastAPI request object.
        user (User): User object representing the authenticated user.

    Returns:
        User: The current authenticated user.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user_role),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar URL of the authenticated user.

    Args:
        file (UploadFile): UploadFile object containing the user's avatar image.
        user (User): User object representing the authenticated user.
        db (AsyncSession): Database session object.

    Returns:
        User: The updated user with the new avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
