import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from datastorage.crud.exceptions import CRUDConflict


@pytest.mark.asyncio
async def test_create_success(crud_storage, mock_session):
    instance = MagicMock()
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    result = await crud_storage.create(instance)

    assert result == instance
    mock_session.add.assert_called_once_with(instance)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(instance)
    assert instance.id is not None


@pytest.mark.asyncio
async def test_create_integrity_error(crud_storage, mock_session):
    instance = MagicMock()
    mock_session.add = AsyncMock(side_effect=IntegrityError("Mock error", None, None))

    with pytest.raises(CRUDConflict):
        await crud_storage.create(instance)