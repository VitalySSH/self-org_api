import pytest

from datastorage.crud.datastorage import CRUDDataStorage


@pytest.fixture
def crud_storage(mock_session):
    """Создает экземпляр CRUDDataStorage с мок-сессией."""
    class MockModel:
        id = None

    storage = CRUDDataStorage(MockModel)
    storage._session = mock_session

    return storage
