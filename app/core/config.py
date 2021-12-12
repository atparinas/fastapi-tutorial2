from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret


config = Config('.env')

PROJECT_NAME = "phresh"
VERSION = "1.0.0"
API_PREFIX = "/api"
SECRET_KEY = config("SECRET_KEY", cast=Secret, default="CHANGEME")
DATABASE_USER = config("DATABASE_USER", cast=str)
DATABASE_PASSWORD = config("DATABASE_PASSWORD", cast=Secret)
DATABASE_SERVER = config("DATABASE_SERVER", cast=str, default="localhost")
DATABASE_PORT = config("DATABASE_PORT", cast=str, default="3306")
DATABASE_DB = config("DATABASE_DB", cast=str)
DATABASE_URL = config(
  "DATABASE_URL",
  cast=DatabaseURL,
  default=f"mysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_DB}"
)

SECRET_KEY = config("SECRET_KEY", cast=Secret)
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    cast=int,
    default=7 * 24 * 60  # one week
)
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")
JWT_AUDIENCE = config("JWT_AUDIENCE", cast=str, default="phresh:auth")
JWT_TOKEN_PREFIX = config("JWT_TOKEN_PREFIX", cast=str, default="Bearer")