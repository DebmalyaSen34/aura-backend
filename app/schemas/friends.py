from pydantic import BaseModel

class Friend(BaseModel):
    id: int
    user_id: str
    friend_id: str
    
class FriendRequest(BaseModel):
    reciever_id: str
    
class FriendRequestResponse(BaseModel):
    id: str
    status: str # pending, accepted, rejected
    
class ShowFriend(BaseModel):
    id: int
    friend_id: str
    friend_name: str
    friend_username: str
    friend_profile_picture: str
    became_friend_at: str
    