from typing import Any
from app.db.repositories.base import BaseRepository
from app.models.cleaning import CleaningCreate, CleaningUpdate, CleaningInDB


CREATE_CLEANING_QUERY = """
    INSERT INTO cleanings (name, description, price, cleaning_type)
    VALUES (:name, :description, :price, :cleaning_type)
"""

GET_CLEANING_QUERY = """
    SELECT * FROM cleanings WHERE cleanings.id = :id
"""


class CleaningsRepository(BaseRepository):
    """"
    All database actions associated with the Cleaning resource
    """
    async def create_cleaning(self, *, new_cleaning: CleaningCreate) -> CleaningInDB:
        query_values = new_cleaning.dict()
        cleaning_id = await self.db.execute(query=CREATE_CLEANING_QUERY, values=query_values)

        # Fetch the newly created back from the db
        cleaning_from_db = await self.db.fetch_one(query=GET_CLEANING_QUERY, values={"id": cleaning_id})

        return CleaningInDB(**cleaning_from_db)