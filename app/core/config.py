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