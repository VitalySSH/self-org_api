from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette import status
from starlette.responses import FileResponse

from auth.auth import auth_service

from datastorage.database.models import FileMetaData
from auth.models.user import User
from filestorage.filestorage import FileStorageApp
from filestorage.schemas import FileMetaRead

file_router = APIRouter()


@file_router.get(
    '/metadata/{file_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=FileMetaRead,
    status_code=200,
)
async def get_file_metadata(
    file_id: str,
) -> FileMetaRead:
    fs = FileStorageApp[FileMetaData](model=FileMetaData)
    async with fs.session_scope(read_only=True):
        file_metadata = await fs.get_file_metadata(file_id)
        if not file_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Метаданные файла с id: {file_id} не найдены',
            )

        return FileMetaRead(
            id=file_metadata.id,
            name=file_metadata.name,
            mimetype=file_metadata.mimetype,
            created=file_metadata.created,
            updated=file_metadata.updated,
        )


@file_router.post(
    '/create',
    status_code=201,
)
async def create_file(
        file: UploadFile = File(),
        current_user: User = Depends(auth_service.get_current_user),
) -> FileMetaRead:
    fs = FileStorageApp[FileMetaData](model=FileMetaData)
    async with fs.session_scope():
        file_metadata = await fs.create_file(
            file=file,
            user_id=current_user.id
        )

        return FileMetaRead(
            id=file_metadata.id,
            name=file_metadata.name,
            mimetype=file_metadata.mimetype,
            created=file_metadata.created,
            updated=file_metadata.updated,
        )


@file_router.patch(
    '/{file_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_file(
        file_id: str,
        file: UploadFile = File(),
):
    fs = FileStorageApp[FileMetaData](model=FileMetaData)
    async with fs.session_scope():
        await fs.update_file(file=file, file_id=file_id)


@file_router.delete(
    '/{file_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_file(
        file_id: str,
):
    fs = FileStorageApp[FileMetaData](model=FileMetaData)
    async with fs.session_scope():
        await fs.delete_file(file_id)


@file_router.get(
    '/stream/{file_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=200,
)
async def get_file_stream(
    file_id: str,
) -> FileResponse:
    fs = FileStorageApp[FileMetaData](model=FileMetaData)
    async with fs.session_scope(read_only=True):
        file_metadata = await fs.get_file_metadata(file_id)
        if not file_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Метаданные файла с id: {file_id} не найдены',
            )

        return FileResponse(
            path=fs.get_file_path(file_metadata),
            filename=file_metadata.name,
            media_type=file_metadata.mimetype
        )
