import pytest
from databases import Database
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.user import UserInDB

from app.models.user import UserInDB, UserPublic
from app.models.profile import ProfileInDB, ProfilePublic
from app.db.repositories.profiles import ProfilesRepository


pytestmark = pytest.mark.asyncio



async def test_profile_routes_exist(app: FastAPI, client: AsyncClient, test_user: UserInDB) -> None:

    # Get profile by username
    res = await client.get(app.url_path_for("profiles:get-profile-by-username", username=test_user.username))
    assert res.status_code != status.HTTP_404_NOT_FOUND

    # Update own profile
    res = await client.put(app.url_path_for("profiles:update-own-profile"), json={"profile_update": {}})
    assert res.status_code != status.HTTP_404_NOT_FOUND




async def test_profile_created_for_new_users(app: FastAPI, client: AsyncClient, db: Database) -> None:

    profiles_repo = ProfilesRepository(db)

    new_user = {"email": "dwayne@johnson.io", "username": "therock", "password": "dwaynetherockjohnson"}
    res = await client.post(app.url_path_for("users:register-new-user"), json={"new_user": new_user})
    assert res.status_code == status.HTTP_201_CREATED

    created_user = UserPublic(**res.json())
    user_profile = await profiles_repo.get_profile_by_user_id(user_id=created_user.id)

    # assert user_profile is not None
    assert user_profile is None
    assert isinstance(user_profile, ProfileInDB)


async def test_authenticated_user_can_view_other_users_profile( app: FastAPI, authorized_client: AsyncClient, 
    test_user: UserInDB, test_user2: UserInDB) -> None:

        res = await authorized_client.get(
            app.url_path_for("profiles:get-profile-by-username", username=test_user2.username)
        )
        
        assert res.status_code == status.HTTP_200_OK
        profile = ProfilePublic(**res.json())
        assert profile.username == test_user2.username    