from typing import Dict, Any, Optional
from models.user import User
import firebase

class UserService:
    def create(self, data: Dict[str, Any]) -> User:
        user = User()
        for k, v in data.items():
            setattr(user, k, v)
        firebase.save_user(user)
        return user

    def get(self, user_id: str) -> Optional[User]:
        return firebase.get_user(user_id)

    def update(self, user_id: str, data: Dict[str, Any]) -> User:
        user = firebase.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        for k, v in data.items():
            setattr(user, k, v)
        firebase.save_user(user)
        return user

user_service = UserService()