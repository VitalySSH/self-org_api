import pytest
from unittest.mock import AsyncMock, MagicMock
from datastorage.crud.exceptions import CRUDNotFound


@pytest.mark.asyncio
async def test_delete_success(crud_storage, mock_session):
    instance_id = "mock_id"
    mock_instance = MagicMock()
    crud_storage.get = AsyncMock(return_value=mock_instance)
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    await crud_storage.delete(instance_id)

    crud_storage.get.assert_called_once_with(instance_id=instance_id)
    mock_session.delete.assert_called_once_with(mock_instance)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(crud_storage):
    instance_id = "mock_id"
    crud_storage.get = AsyncMock(return_value=None)

    with pytest.raises(CRUDNotFound):
        await crud_storage.delete(instance_id)
