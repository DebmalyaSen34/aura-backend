from pydantic import BaseModel


class Votes(BaseModel):
    incident_id: int
    upvotes: int = 0
    downvotes: int = 0
