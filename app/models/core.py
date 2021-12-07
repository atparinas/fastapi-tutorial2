from pydantic import BaseModel

class CoreModel(BaseModel):
    """
    Any Common logic to be share by all model
    """
    pass


class IDModelMixin(BaseModel):
    id: int