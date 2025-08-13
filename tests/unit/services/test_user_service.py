from services.user_service import user_service
from repositories.users_repository import get_user, save_user
from models.user import User


def test_user_service_create(patch_repositories_db):
    created = user_service.create({})
    assert get_user(created.id) is not None


def test_user_service_update(patch_repositories_db):
    u = User(save_object=False)
    save_user(u)
    updated = user_service.update(u.id, {"firstName": "John", "lastName": "Doe"})
    assert updated.firstName == "John"
    assert updated.lastName == "Doe"


