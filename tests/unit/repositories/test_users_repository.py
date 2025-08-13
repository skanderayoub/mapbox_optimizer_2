from repositories.users_repository import save_user, get_user, get_all_users
from models.user import User


def test_save_and_get_user(patch_repositories_db):
    user = User(save_object=False)
    save_user(user)

    fetched = get_user(user.id)
    assert fetched is not None
    assert fetched.id == user.id
    assert isinstance(get_all_users(), list)


