from tempfile import NamedTemporaryFile

from typing.io import IO


def create_file(file: bytes, file_name: str) -> IO:
    file_obj = NamedTemporaryFile(prefix=file_name, delete=True)
    file_obj.write(file)
    file_obj.flush()
    file_obj.seek(0)
    return file_obj
