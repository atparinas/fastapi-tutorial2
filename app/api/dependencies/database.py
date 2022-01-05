from typing import Callable, Type
from databases import Database
from fastapi import Depends
from starlette.requests import Request
from app.db.repositories.base import BaseRepository
from pprint import pprint

def get_database(request: Request) -> Database:
    pprint(vars(request.app.state))
    return request.app.state._db

    
def get_repository(Repo_type: Type[BaseRepository]) -> Callable:
    def get_repo(db: Database = Depends(get_database)) -> Type[BaseRepository]:
        return Repo_type(db)
    return get_repo