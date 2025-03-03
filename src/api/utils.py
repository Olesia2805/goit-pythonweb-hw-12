from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

from src.conf import messages

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Check if the database connection is working.

    Args:
        db (AsyncSession): Database session object.

    Returns:
        dict: A message indicating the health status.

    Raises:
        HTTPException: If there is an error connecting to the database.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()
        return {"message": messages.HEALTHCHECKER_MESSAGE}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages.DATABASE_ERROR_CONNECT_MESSAGE,
        )
