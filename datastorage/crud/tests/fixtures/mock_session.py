import pytest
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_session():
    """Создаёт мок для асинхронной сессии SQLAlchemy."""
    return MagicMock(spec=AsyncSession)
