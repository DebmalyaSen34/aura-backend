from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreateIncident(BaseModel):
    content: str
    
class ShowIncident(BaseModel):
    incident_id: int
    content: str
    user_id:str
    display_name: str
    username: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime
    total_upvotes: int = 0
    total_downvotes: int = 0
    total_comments: int = 0
    is_upvoted: bool = False
    is_downvoted: bool = False
    
    class Config:
        from_attributes = True