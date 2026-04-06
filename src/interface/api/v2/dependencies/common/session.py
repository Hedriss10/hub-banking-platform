from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import (
    get_unverified_session,
    get_verified_session,
)

UnverifiedSessionDep = Annotated[AsyncSession, Depends(get_unverified_session)]
VerifiedSessionDep = Annotated[AsyncSession, Depends(get_verified_session)]
