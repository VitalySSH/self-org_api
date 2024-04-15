from datastorage.crud.interfaces.base import T, SchemaReadInstance
from datastorage.database.models import User


def update_instance_by_likes(instance: T, current_user: User) -> SchemaReadInstance:
    likes_count, dislikes_count, current_user_like = None, None, None
    if instance.likes:
        likes_count = len(list(filter(lambda it: it.is_like is True, instance.likes)))
        dislikes_count = len(list(filter(lambda it: it.is_like is False, instance.likes)))
        current_user_like = bool(list(filter(
            lambda it: it.creator_id == current_user.id, instance.likes)))

    read_schema = instance.to_read_schema()
    read_schema['readonly']['likes_count'] = likes_count
    read_schema['readonly']['dislikes_count'] = dislikes_count
    read_schema['readonly']['current_user_like'] = current_user_like

    return read_schema
