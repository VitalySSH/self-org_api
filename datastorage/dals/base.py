from sqlalchemy.ext.asyncio import AsyncSession


class DAL:
    """Прослойка между БД и бизнес-логикой."""

    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
