from typing import List, Optional

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# base class that has common properties for reading/writing
class UserBase(BaseModel):
    name: str
    email: str
    user_type: str
    is_active: Optional[bool] = None

# writing class includes password
class UserInDB(UserBase):
    password: str

class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True



# This is because there is table Item in the tutorial
# class ItemBase(BaseModel):
#     title: str
#     description: Optional[str] = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True