from typing import Any, List
from app.db.repositories.base import BaseRepository
from fastapi import HTTPException, status
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.models.cleaning import CleaningCreate, CleaningUpdate, CleaningInDB
from app.models.user import UserInDB

from pprint import pprint


CREATE_CLEANING_QUERY = """
    INSERT INTO cleanings (name, description, price, cleaning_type, owner)
    VALUES (:name, :description, :price, :cleaning_type, :owner)
"""

GET_CLEANING_BY_ID_QUERY = """
    SELECT id, name, description, price, cleaning_type, owner, created_at, updated_at
    FROM cleanings
    WHERE id = :id;
"""

GET_ALL_CLEANINGS_QUERY = """
    SELECT id, name, description, price, cleaning_type  
    FROM cleanings;  
"""

UPDATE_CLEANING_BY_ID_QUERY = """
    UPDATE cleanings
    SET name         = :name,
        description  = :description,
        price        = :price,
        cleaning_type = :cleaning_type
    WHERE id = :id AND owner = :owner;
"""

DELETE_CLEANING_BY_ID_QUERY = """
    DELETE FROM cleanings  
    WHERE id = :id;
""" 

LIST_ALL_USER_CLEANINGS_QUERY = """
    SELECT id, name, description, price, cleaning_type, owner, created_at, updated_at
    FROM cleanings
    WHERE owner = :owner;
"""

class CleaningsRepository(BaseRepository):
    """"
    All database actions associated with the Cleaning resource
    """

    """
    CREATE
    """
    async def create_cleaning(self, *, new_cleaning: CleaningCreate, requesting_user: UserInDB) -> CleaningInDB:

        cleaning_id = await self.db.execute(query=CREATE_CLEANING_QUERY, values={**new_cleaning.dict(), "owner": requesting_user.id})

        # Fetch the newly created back from the db
        # cleaning_from_db = await self.db.fetch_one(query=GET_CLEANING_BY_ID_QUERY, values={"id": cleaning_id})
        return await self.get_cleaning_by_id(id=cleaning_id, requesting_user=requesting_user)

        # return CleaningInDB(**cleaning_from_db)

    """
    SHOW
    """
    async def get_cleaning_by_id(self, *, id: int, requesting_user: UserInDB) -> CleaningInDB:
        cleaning = await self.db.fetch_one(query=GET_CLEANING_BY_ID_QUERY, values={"id": id})
        if not cleaning:
            return None
            
        return CleaningInDB(**cleaning)


    """
    LIST
    """
    async def get_all_cleanings(self) -> List[CleaningInDB]:
        cleaning_records = await self.db.fetch_all(
            query=GET_ALL_CLEANINGS_QUERY,
        )
        return [CleaningInDB(**l) for l in cleaning_records]


    async def list_all_user_cleanings(self, requesting_user: UserInDB) -> List[CleaningInDB]:
        cleaning_records = await self.db.fetch_all(
            query=LIST_ALL_USER_CLEANINGS_QUERY, values={"owner": requesting_user.id}
        )
        return [CleaningInDB(**l) for l in cleaning_records]


    """
    UPDATE
    """
    async def update_cleaning(
        self, *, id: int, cleaning_update: CleaningUpdate, requesting_user: UserInDB
    ) -> CleaningInDB:

        cleaning = await self.get_cleaning_by_id(id=id, requesting_user=requesting_user)

        if not cleaning:
            return None

        if cleaning.owner != requesting_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users are only able to update cleanings that they created.",
            )

        cleaning_update_params = cleaning.copy(update=cleaning_update.dict(exclude_unset=True))
        if cleaning_update_params.cleaning_type is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cleaning type. Cannot be None."
            )

        update_success = await self.db.execute(
            query=UPDATE_CLEANING_BY_ID_QUERY,
            values={
                **cleaning_update_params.dict(exclude={"created_at", "updated_at"}),
                "owner": requesting_user.id,
            },
        )

        updated_cleaning = await self.get_cleaning_by_id(id=id, requesting_user=requesting_user)

        return CleaningInDB(**updated_cleaning)


    """
    DELETE
    """
    async def delete_cleaning_by_id(self, *, id: int) -> int:

        cleaning = await self.get_cleaning_by_id(id=id) 

        if not cleaning:
            return None

        try:

            await self.db.execute( query=DELETE_CLEANING_BY_ID_QUERY, values={"id": id}, )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Error Deleting Object",
            )


        return id