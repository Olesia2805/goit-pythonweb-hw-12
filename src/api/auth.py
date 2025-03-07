from fastapi import (  # type: ignore
    APIRouter,
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    Request,
)
from sqlalchemy.orm import Session  # type: ignore
from src.schemas.users import UserCreate, Token, User, UserLogin, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.services.email import send_email
from src.database.db import get_db

from src.configuration import messages

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Args:
        user_data (UserCreate): User data to create a new user.
        background_tasks (BackgroundTasks): Background tasks for sending emails.
        request (Request): Current request object.
        db (Session): Database session.
    """

    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_EMAIL_EXISTS,
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_USERNAME_EXISTS,
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url, type="verify"
    )
    return new_user


@router.post("/login", response_model=Token, status_code=status.HTTP_201_CREATED)
async def login_user(body: UserLogin, db: Session = Depends(get_db)):
    """
    Login a user.

    Args:
        body (UserLogin): User data to login.
        db (Session): Database session.
    """

    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user and not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.USER_NOT_CONFIRMED
        )
    if not user or not Hash().verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.USER_NOT_FOUND,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/request_email", status_code=status.HTTP_201_CREATED)
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request email verification for a user.

    Args:
        body (RequestEmail): User's email to send the verification email.
        background_tasks (BackgroundTasks): Background tasks for sending emails.
        request (Request): Current request object.
        db (Session): Database session.
    """

    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": messages.USER_EMAIL_CONFIRMED_ALREADY}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url, type="verify"
        )
    return {"message": messages.CHECK_YOUR_EMAIL}


@router.get("/confirmed_email/{token}", status_code=status.HTTP_200_OK)
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm user's email.

    Args:
        token (str): Token from the email verification link.
        db (Session): Database session.
    """

    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": messages.USER_EMAIL_CONFIRMED_ALREADY}
    await user_service.confirmed_email(email)
    return {"message": messages.USER_EMAIL_CONFIRMED}


@router.post("/reset_password", status_code=status.HTTP_201_CREATED)
async def reset_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Reset user's password.

    Args:
        body (RequestEmail): User's email to reset password.
        background_tasks (BackgroundTasks): Background tasks for sending emails.
        request (Request): Current request object.
        db (Session): Database session.
    """

    user_service = UserService(db)
    user = user_service.get_user_by_email(body.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.USER_NOT_FOUND
        )
    background_tasks.add_task(
        send_email, user.email, user.username, request.base_url, type="reset"
    )
    return {"message": messages.CHECK_YOUR_EMAIL}


@router.patch("/update_password/{token}", status_code=status.HTTP_200_OK)
async def update_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Update user's password.

    Args:
        token (str): Token from the password reset link.
        new_password (str): New password to update.
        db (Session): Database session.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.CONTACT_NOT_FOUND
        )
    new_password = Hash().get_password_hash(new_password)
    await user_service.update_password(email, new_password)
    return {"message": messages.USER_PASSWORD_UPDATED}
