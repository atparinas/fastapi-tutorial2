from typing import Optional
from datetime import datetime

from pydantic import BaseModel, validator

class CoreModel(BaseModel):
    """
    Any Common logic to be share by all model
    """
    pass

class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    @validator("created_at", "updated_at", pre=True)
    def default_datetime(cls, value: datetime) -> datetime:
        return value or datetime.datetime.now()

class IDModelMixin(BaseModel):
    id: int