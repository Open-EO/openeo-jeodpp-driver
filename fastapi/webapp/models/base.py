from pydantic import BaseModel


# pydantic
class PydanticBase(BaseModel):
    class Config:
        orm_mode = True
        validate_assignment = True
