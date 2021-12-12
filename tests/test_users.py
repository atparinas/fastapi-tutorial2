import pytest
import jwt
from typing import List, Union, Type, Optional
from httpx import AsyncClient
from fastapi import FastAPI

from databases import Database
from app.db.repositories.users import UsersRepository

from starlette.status import (
    HTTP_200_OK, 
    HTTP_201_CREATED, 
    HTTP_400_BAD_REQUEST, 
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND, 
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from pydantic import ValidationError
from starlette.datastructures import Secret


from app.core.config import SECRET_KEY, JWT_ALGORITHM, JWT_AUDIENCE, JWT_TOKEN_PREFIX, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.token import JWTMeta, JWTCreds, JWTPayload

from app.models.user import UserCreate, UserInDB
from app.services import auth_service


pytestmark = pytest.mark.asyncio


async def test_user_routes_exist(app: FastAPI, client: AsyncClient) -> None:
    new_user = {"email": "test@email.io", "username": "test_username", "password": "testpassword"}
    res = await client.post(app.url_path_for("users:register-new-user"), json={"new_user": new_user})
    assert res.status_code != HTTP_404_NOT_FOUND


"""
TEST REGISTER USER - SUCCESS
"""
async def test_users_can_register_successfully(app: FastAPI, client: AsyncClient,db: Database,) -> None:

    user_repo = UsersRepository(db)
    new_user = {"email": "shakira@shakira.io", "username": "shakirashakira", "password": "chantaje"}
    
    # make sure user doesn't exist yet
    user_in_db = await user_repo.get_user_by_email(email=new_user["email"])
    assert user_in_db is None        
    
    # send post request to create user and ensure it is successful
    res = await client.post(app.url_path_for("users:register-new-user"), json={"new_user": new_user})
    assert res.status_code == HTTP_201_CREATED
    
    # ensure that the user now exists in the db
    user_in_db = await user_repo.get_user_by_email(email=new_user["email"])
    assert user_in_db is not None
    assert user_in_db.email == new_user["email"]
    assert user_in_db.username == new_user["username"]
    
    # check that the user returned in the response is equal to the user in the database
    created_user = UserInDB(**res.json(), password="whatever", salt="123").dict(exclude={"password", "salt"})
    assert created_user == user_in_db.dict(exclude={"password", "salt"})




"""
TEST REGISTER USER - FAILS
"""
@pytest.mark.parametrize(
    "attr, value, status_code",
    (
        ("email", "shakira@shakira.io", 400),            
        ("username", "shakirashakira", 400),
        ("email", "invalid_email@one@two.io", 422),
        ("password", "short", 422),
        ("username", "shakira@#$%^<>", 422),
        ("username", "ab", 422),
    )
)
async def test_user_registration_fails_when_credentials_are_taken(
    app: FastAPI,  client: AsyncClient, db: Database,
    attr: str, value: str, status_code: int,
) -> None: 

    new_user = {"email": "nottaken@email.io", "username": "not_taken_username", "password": "freepassword"}
    new_user[attr] = value

    res = await client.post(app.url_path_for("users:register-new-user"), json={"new_user": new_user})
    assert res.status_code == status_code



"""
TEST PASSWORD HASH
"""
async def test_users_saved_password_is_hashed_and_has_salt(app: FastAPI, client: AsyncClient,  db: Database, ) -> None:
        user_repo = UsersRepository(db)
        new_user = {"email": "beyonce@knowles.io", "username": "queenbey", "password": "destinyschild"}
        # send post request to create user and ensure it is successful
        res = await client.post(app.url_path_for("users:register-new-user"), json={"new_user": new_user})
        assert res.status_code == HTTP_201_CREATED
        # ensure that the users password is hashed in the db
        # and that we can verify it using our auth service
        user_in_db = await user_repo.get_user_by_email(email=new_user["email"])
        assert user_in_db is not None
        assert user_in_db.salt is not None and user_in_db.salt != "123"        
        assert user_in_db.password != new_user["password"]
        assert auth_service.verify_password(
            password=new_user["password"], 
            salt=user_in_db.salt, 
            hashed_pw=user_in_db.password,
        )



async def test_can_create_access_token_successfully(app: FastAPI, client: AsyncClient, test_user: UserInDB
    ) -> None:
        access_token = auth_service.create_access_token_for_user(
            user=test_user,
            secret_key=str(SECRET_KEY),
            audience=JWT_AUDIENCE,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        creds = jwt.decode(access_token, str(SECRET_KEY), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])
        assert creds.get("username") is not None
        assert creds["username"] == test_user.username
        assert creds["aud"] == JWT_AUDIENCE




async def test_token_missing_user_is_invalid(app: FastAPI, client: AsyncClient) -> None:
        access_token = auth_service.create_access_token_for_user(
            user=None,
            secret_key=str(SECRET_KEY),
            audience=JWT_AUDIENCE,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        with pytest.raises(jwt.PyJWTError):
            jwt.decode(access_token, str(SECRET_KEY), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])




@pytest.mark.parametrize(
    "secret_key, jwt_audience, exception",
    (
        ("wrong-secret", JWT_AUDIENCE, jwt.InvalidSignatureError),
        (None, JWT_AUDIENCE, jwt.InvalidSignatureError),
        (SECRET_KEY, "othersite:auth", jwt.InvalidAudienceError),
        (SECRET_KEY, None, ValidationError),
    )
)
async def test_invalid_token_content_raises_error( app: FastAPI, client: AsyncClient,
    test_user: UserInDB, secret_key: Union[str, Secret],
    jwt_audience: str,  exception: Type[BaseException],
) -> None:

    with pytest.raises(exception):

        access_token = auth_service.create_access_token_for_user(
            user=test_user,
            secret_key=str(secret_key),
            audience=jwt_audience,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        jwt.decode(access_token, str(SECRET_KEY), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])





async def test_user_can_login_successfully_and_receives_valid_token( app: FastAPI, client: AsyncClient, test_user: UserInDB,) -> None:
        client.headers["content-type"] = "application/x-www-form-urlencoded"
        login_data = {
            "username": test_user.email,
            "password": "heatcavslakers",  # insert user's plaintext password
        }
        res = await client.post(app.url_path_for("users:login-email-and-password"), data=login_data)
        assert res.status_code == HTTP_200_OK


        # check that token exists in response and has user encoded within it
        token = res.json().get("access_token")
        creds = jwt.decode(token, str(SECRET_KEY), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])
        assert "username" in creds
        assert creds["username"] == test_user.username
        assert "sub" in creds
        assert creds["sub"] == test_user.email


        # check that token is proper type
        assert "token_type" in res.json()
        assert res.json().get("token_type") == "bearer"