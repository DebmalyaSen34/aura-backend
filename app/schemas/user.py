from pydantic import BaseModel
from typing import Optional, Dict

class Auth(BaseModel):
    email: str
    password: str

class User(Auth):
    name: str
    
class ShowUser(BaseModel):
    id: str
    email: str
    user_metadata: Optional[Dict] = None
    
    class Config():
        from_attributes = True