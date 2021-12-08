from app.db.repositories.base import BaseRepository
from app.models.user import UserCreate, UserUpdate, UserInDB
from pydantic import EmailStr


GET_USER_BY_EMAIL_QUERY = """
    SELECT id, username, email, email_verified, password, salt, is_active, is_superuser, created_at, updated_at
    FROM users
    WHERE email = :email;
"""

GET_USER_BY_USERNAME_QUERY = """
    SELECT id, username, email, email_verified, password, salt, is_active, is_superuser, created_at, updated_at
    FROM users
    WHERE username = :username;
"""

REGISTER_NEW_USER_QUERY = """
    INSERT INTO users (username, email, password, salt)
    VALUES (:username, :email, :password, :salt)
    RETURNING id, username, email, email_verified, password, salt, is_active, is_superuser, created_at, updated_at;
"""


class UsersRepository(BaseRepository):

    async def register_new_user(self, *, new_user: UserCreate) -> UserInDB:
        return None

    async def get_user_by_email(self, *, email: EmailStr) -> UserInDB:

        user_record = await self.db.fetch_one(query=GET_USER_BY_EMAIL_QUERY, values={"email": email})

        if not user_record:
            return None
            
        return UserInDB(**user_record)

    async def get_user_by_username(self, *, username: str) -> UserInDB:
        user_record = await self.db.fetch_one(query=GET_USER_BY_USERNAME_QUERY, values={"username": username})
        if not user_record:
            return None
        return UserInDB(**user_record)