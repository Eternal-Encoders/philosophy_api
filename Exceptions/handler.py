from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def handle_fk(
    e: IntegrityError,
    session: AsyncSession
):
    await session.rollback()
    error_msg = str(e.orig)
    if "foreign key constraint" in error_msg.lower():
        raise HTTPException(
            status_code=404,
            detail=error_msg
        )
