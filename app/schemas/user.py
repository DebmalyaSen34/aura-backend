from pydantic import BaseModel
from typing import Optional, Dict

class Auth(BaseModel):
    email: str
    password: str

class User(Auth):
    name: str
    
class ShowUser(BaseModel):
    id: str
    name: str
    created_at: str
    incidents: int    
    class Config():
        from_attributes = True
        
class UpdateUser(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None