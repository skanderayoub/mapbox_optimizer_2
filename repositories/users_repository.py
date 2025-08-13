from typing import List, Optional

from models.user import User
from repositories.base_repository import save_object, get_object, get_all_objects

COLLECTION_NAME = "users"

def save_user(user: User) -> None:
    save_object(user, COLLECTION_NAME)


def get_user(user_id: str) -> Optional[User]:
    return get_object(User, user_id, COLLECTION_NAME)


def get_all_users() -> List[User]:
    return get_all_objects(User, COLLECTION_NAME)


