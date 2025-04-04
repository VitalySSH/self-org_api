class CRUDBaseException(Exception):
    status_code: int
    title: str
    description: str


class CRUDException(CRUDBaseException):
    status_code: int = 500
    title: str = 'Неизвестная ошибка CRUD-операции'
    description: str

    def __init__(self, description: str = ''):
        self.description = description


class CRUDOperationError(CRUDException):
    status_code: int = 400
    title: str = 'Ошибка обработки запроса CRUD-операции'


class CRUDNotFound(CRUDException):
    status_code: int = 404
    title: str = 'Объект не найден'


class CRUDConflict(CRUDException):
    status_code: int = 409
    title: str = 'Объект не может быть создан, удалён или изменён'


class CRUDValidationError(CRUDException):
    status_code: int = 422
    title: str = 'Ошибка валидации объекта'
