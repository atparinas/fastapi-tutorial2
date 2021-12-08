from typing import Any, List
from app.db.repositories.base import BaseRepository
from app.models.cleaning import CleaningCreate, CleaningUpdate, CleaningInDB
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from pprint import pprint


CREATE_CLEANING_QUERY = """
    INSERT INTO cleanings (name, description, price, cleaning_type)
    VALUES (:name, :description, :price, :cleaning_type)
"""

GET_CLEANING_BY_ID_QUERY = """
    SELECT * FROM cleanings WHERE cleanings.id = :id
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
    WHERE id = :id; 
"""


class CleaningsRepository(BaseRepository):
    """"
    All database actions associated with the Cleaning resource
    """
    async def create_cleaning(self, *, new_cleaning: CleaningCreate) -> CleaningInDB:
        query_values = new_cleaning.dict()
        cleaning_id = await self.db.execute(query=CREATE_CLEANING_QUERY, values=query_values)

        # Fetch the newly created back from the db
        # cleaning_from_db = await self.db.fetch_one(query=GET_CLEANING_BY_ID_QUERY, values={"id": cleaning_id})
        return await self.get_cleaning_by_id(id=cleaning_id)

        # return CleaningInDB(**cleaning_from_db)

    async def get_cleaning_by_id(self, *, id: int) -> CleaningInDB:
        cleaning = await self.db.fetch_one(query=GET_CLEANING_BY_ID_QUERY, values={"id": id})
        if not cleaning:
            return None
        return CleaningInDB(**cleaning)


    async def get_all_cleanings(self) -> List[CleaningInDB]:
        cleaning_records = await self.db.fetch_all(
            query=GET_ALL_CLEANINGS_QUERY,
        )
        return [CleaningInDB(**l) for l in cleaning_records]


    async def update_cleaning( self, *, id: int, cleaning_update: CleaningUpdate, ) -> CleaningInDB:

        cleaning = await self.get_cleaning_by_id(id=id)

        if not cleaning:
            return None


        cleaning_update_params = cleaning.copy(
            update=cleaning_update.dict(exclude_unset=True),
        )

       

        try:
            await self.db.execute(
                query=UPDATE_CLEANING_BY_ID_QUERY, 
                values=cleaning_update_params.dict(),
            )


            updated_cleaning = await self.get_cleaning_by_id(id=id)

            return updated_cleaning

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, 
                detail="Invalid update params.",
            )