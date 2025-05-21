from fastapi import APIRouter, Depends, status, HTTPException
from ..core import dependencies, db
from ..schemas import user, friends
from gotrue.errors import AuthApiError
from datetime import datetime

router = APIRouter(
    tags=["friends"],
    prefix="/friends",
)

@router.get("/get_friends", status_code=status.HTTP_200_OK)
def get_friends(current_user: user.User = Depends(dependencies.get_current_user)):
    
    token = current_user.token
    
    supabase = db.get_supabase_client(token=token)
    
    user_id = current_user.id
    
    response = supabase.table("request").select("*").eq("from_id", user_id).execute()
    
    if not response.data:
        return {"message": "No friends found"}
    
    friends = []
    
    for friend in response.data:
        friends.append(friend)
    
    return friends
            
            
@router.post("/send_friend_request", status_code=status.HTTP_200_OK)
def send_friend_request(friend_request: friends.FriendRequest, current_user: user.User = Depends(dependencies.get_current_user)):
    
    token=current_user.token
    supabase = db.get_supabase_client(token=token)
    
    try:
        response = supabase.table("request").insert({
            "sender_id": current_user.id,
            "reciever_id": friend_request.reciever_id,
            "status": "pending"
        }).execute()
    
        if not response.data:
            return {"message": "Failed to send friend request"}
        
        return {"message": "Friend request sent"}
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )
        

@router.get("/get_friend_requests", status_code=status.HTTP_200_OK)
def get_friend_requests(current_user: user.User = Depends(dependencies.get_current_user)):
    
    token=current_user.token
    
    supabase = db.get_supabase_client(token=token)
    

    try: 
        response = supabase.table("request").select("""
            *,
            sender:profiles!sender_id(id, username, name, profile_image),
            receiver:profiles!reciever_id(id, username, name, profile_image)
        """).eq("reciever_id", current_user.id).eq("status", "pending").execute()
        
        if not response.data:
            return {"message": "No friend requests found"}
        
        return response.data
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )

@router.post("/respond_to_friend_request", status_code=status.HTTP_200_OK)
def response_to_friend_request(friend_request: friends.FriendRequestResponse, current_user: user.User = Depends(dependencies.get_current_user)):
    token=current_user.token
    supabase = db.get_supabase_client(token=token)
    
    try:
        
        response = supabase.table("request").update({
            "status": friend_request.status,
            "responed_at": datetime.now().isoformat()
        }).eq("id", friend_request.id).execute()
        
        if not response.data:
            return {"message": "Failed to respond to friend request"}
        
        return {"message": "Friend request responded"}
    
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )
    
    
    
    
    