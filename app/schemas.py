from typing import Optional
from datetime import  datetime
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
    is_active: Optional[bool] = None

# writing class includes password
class UserCreate(UserBase):
    password: str
    user_type: str

class User(UserBase):
    user_id: int
    user_type: int

    class Config:
        orm_mode = True

class IssuerCreate(BaseModel):
    issuer_user: int
    issuer_name: str

class Issuer(IssuerCreate):
    issuer_id: int
    key_lifetime: int
    public_key: str
    expiry: datetime

    class Config:
        orm_mode = True

class ResourceBase(BaseModel):
    issuer: int
    origin: str
    resource_name: str
    resource_description: str
    resource_url: str

class ResourceCreate(ResourceBase):
    interface: str

class Resource(ResourceBase):
    resource_id: int
    interface: int
    creation_date: datetime
    major_release: int
    minor_release:int
    patch: int

    class Config:
        orm_mode = True

class GrantCreate(BaseModel):
    user_id: int
    origin: str
    resource_id: int
    grant_duration: int
    qdb: bool
    values: bool
    update: bool
    has_quota: bool
    token_quota: int
    token_count: int
    query_count: int

class Grant(GrantCreate):
    grant_id: int
    creation_date: datetime
    expires: datetime

    class Config:
        orm_mode = True