from datastorage.crud.interfaces.base import T
from datastorage.database.models import User
from datastorage.interfaces import SchemaInstance


def update_object_by_likes(obj: T, current_user: User) -> SchemaInstance:
    likes_count, dislikes_count, current_user_like = None, None, None
    if obj.likes:
        likes_count = len(list(filter(lambda it: it.is_like is True, obj.likes)))
        dislikes_count = len(list(filter(lambda it: it.is_like is False, obj.likes)))
        current_user_like = bool(list(filter(
            lambda it: it.creator_id == current_user.id, obj.likes)))

    read_schema = obj.to_read_schema()
    read_schema['attributes']['likes_count'] = likes_count
    read_schema['attributes']['dislikes_count'] = dislikes_count
    read_schema['attributes']['current_user_like'] = current_user_like

    return read_schema
