from fastapi import APIRouter, Depends, Request, FastAPI, File, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.users import User
from src.services.auth import get_current_user, get_current_user_role
from src.database.db import get_db
from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.conf.config import settings
from src.database.models import Contact

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.add_middleware(SlowAPIMiddleware)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    # user: User = Depends(get_current_user),
    user: User = Depends(get_current_user_role),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
