from pydantic import BaseModel, Field

class UpdateProfileSchema(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)