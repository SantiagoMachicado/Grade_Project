from pydantic import BaseModel
from typing import Optional

class MySchema(BaseModel):
    name: str
    location_wkt: Optional[str] = None
    model_config = {"from_attributes": True}

class MyModel:
    def __init__(self, name):
        self.name = name

    @property
    def location_wkt(self):
        return "HELLO"

m = MyModel("test")
print(getattr(m, 'location_wkt'))
s = MySchema.model_validate(m)
print(s.model_dump())
