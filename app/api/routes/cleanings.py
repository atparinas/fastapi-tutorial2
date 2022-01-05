from typing import List
from fastapi import APIRouter, Depends, Body, HTTPException, Path, status
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from starlette.status import HTTP_201_CREATED  
from app.models.cleaning import CleaningCreate, CleaningPublic, CleaningUpdate
from app.models.user import UserInDB

from app.db.repositories.cleanings import CleaningsRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()

"""
GET list of Cleanings
"""
@router.get("/", response_model=List[CleaningPublic], name="cleanings:list-all-user-cleanings")
async def get_all_cleanings(
    current_user: UserInDB = Depends(get_current_active_user),
    cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))) -> List[CleaningPublic]:
    return await cleanings_repo.list_all_user_cleanings(requesting_user=current_user)

"""
CREATE new cleaning
If we want it to expect JSON with a key new_cleaning and inside of it 
the model contents, we use the special Body parameter embed in the parameter default.
"""
@router.post("/", response_model=CleaningPublic, name="cleanings:create-cleaning", status_code=HTTP_201_CREATED)
async def create_new_cleaning(
    new_cleaning: CleaningCreate = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_active_user),
    cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository)),
) -> CleaningPublic:
    created_cleaning = await cleanings_repo.create_cleaning(new_cleaning=new_cleaning, requesting_user=current_user)
    return created_cleaning

"""
GET Cleaning by Id
"""
@router.get("/{id}/", response_model=CleaningPublic, name="cleanings:get-cleaning-by-id")
async def get_cleaning_by_id( 
    id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))
) -> CleaningPublic:
    
    cleaning = await cleanings_repo.get_cleaning_by_id(id=id, requesting_user=current_user)
    if not cleaning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cleaning found with that id.")
    return cleaning


"""
UPDATE Cleaning by Id
"""
@router.put("/{id}/",  response_model=CleaningPublic, name="cleanings:update-cleaning-by-id")
async def update_cleaning_by_id( 
    id: int = Path(..., ge=1, title="The ID of the cleaning to update."),
    current_user: UserInDB = Depends(get_current_active_user),
    cleaning_update: CleaningUpdate = Body(..., embed=True),
    cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository)),
) -> CleaningPublic:

    updated_cleaning = await cleanings_repo.update_cleaning( id=id, cleaning_update=cleaning_update, requesting_user=current_user)

    if not updated_cleaning:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, 
            detail="No cleaning found with that id.",
        )
        
    return updated_cleaning


"""
DELETE Cleaning by Id
"""
@router.delete("/{id}/", response_model=int, name="cleanings:delete-cleaning-by-id")
async def delete_cleaning_by_id(
    id: int = Path(..., ge=1, title="The ID of the cleaning to delete."),
    cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository)),
) -> int:
    deleted_id = await cleanings_repo.delete_cleaning_by_id(id=id)
    if not deleted_id:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, 
            detail="No cleaning found with that id.",
        )
    return deleted_id