from app.db.repositories.base import BaseRepository
from app.models.profile import ProfileCreate, ProfileUpdate, ProfileInDB


CREATE_PROFILE_FOR_USER_QUERY = """
    INSERT INTO profiles (full_name, phone_number, bio, image, user_id)
    VALUES (:full_name, :phone_number, :bio, :image, :user_id);
"""

GET_PROFILE_BY_USER_ID_QUERY = """
    SELECT id, full_name, phone_number, bio, image, user_id, created_at, updated_at
    FROM profiles
    WHERE user_id = :user_id;
"""


GET_PROFILE_BY_ID_QUERY = """
    SELECT id, full_name, phone_number, bio, image, user_id, created_at, updated_at
    FROM profiles
    WHERE user_id = :profile_id;
"""


GET_PROFILE_BY_USERNAME_QUERY = """
    SELECT p.id,
           u.email AS email,
           u.username AS username,
           full_name,
           phone_number,
           bio,
           image,
           user_id,
           p.created_at,
           p.updated_at
    FROM profiles p
        INNER JOIN users u 
        ON p.user_id = u.id
    WHERE user_id = (SELECT id FROM users WHERE username = :username);
"""


class ProfilesRepository(BaseRepository):


    async def create_profile_for_user(self, *, profile_create: ProfileCreate) -> ProfileInDB:
        profile_id = await self.db.execute(query=CREATE_PROFILE_FOR_USER_QUERY, values=profile_create.dict())

        created_profile = await self.db.fetch_one(query=GET_PROFILE_BY_ID_QUERY, values={"profile_id": profile_id})

        return created_profile



    async def get_profile_by_user_id(self, *, user_id: int) -> ProfileInDB:
        profile_record = await self.db.fetch_one(query=GET_PROFILE_BY_USER_ID_QUERY, values={"user_id": user_id})

        if not profile_record:
            return None

        return ProfileInDB(**profile_record)



    async def get_profile_by_username(self, *, username: str) -> ProfileInDB:
        profile_record = await self.db.fetch_one(query=GET_PROFILE_BY_USERNAME_QUERY, values={"username": username})
        
        if profile_record:
            return ProfileInDB(**profile_record)
