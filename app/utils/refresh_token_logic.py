import uuid

from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model.models import RefreshToken


class RefreshTokenRepository:

    @staticmethod
    async def get_refresh_by_jti(
        db: AsyncSession,
        jti: str,
    ) -> RefreshToken | None:

        stmt = select(RefreshToken).where(
            RefreshToken.jti == jti
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def create_refresh(
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        jti: str,
        expires_at: datetime,
    ) -> RefreshToken:

        refresh = RefreshToken(
            user_id=user_id,
            jti=jti,
            expires_at=expires_at,
        )

        db.add(refresh)

        await db.flush()

        return refresh

    @staticmethod
    async def revoke_refresh(
        refresh: RefreshToken,
    ) -> RefreshToken:

        refresh.is_revoked = True

        return refresh

    @staticmethod
    async def delete_expired(
        db: AsyncSession,
    ) -> int:

        stmt = (
            delete(RefreshToken)
            .where(
                RefreshToken.expires_at
                < datetime.now(timezone.utc)
            )
        )

        result = await db.execute(stmt)

        return result.rowcount or 0

    @staticmethod
    async def rotate_refresh(
        db: AsyncSession,
        *,
        old_refresh: RefreshToken,
        new_jti: str,
        expires_at: datetime,
    ) -> RefreshToken:

        old_refresh.is_revoked = True

        new_refresh = RefreshToken(
            user_id=old_refresh.user_id,
            jti=new_jti,
            expires_at=expires_at,
        )

        db.add(new_refresh)

        await db.flush()

        return new_refresh