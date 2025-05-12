from fastapi import HTTPException, status, Depends
from ..schemas import votes, user
from ..core import dependencies, db
from gotrue.errors import AuthApiError
from supabase import Client

def check_incident_exists(incident_id: int, supabase: Client) -> bool:
    
    response = supabase.table("incident").select("*").eq("id", incident_id).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found.",
        )
    
    return True

def get_user_vote(incident_id: int, user_id: str, supabase: Client):
    
    response = supabase.table("votes").select("*").eq("incident_id", incident_id).eq("voter_id", user_id).execute()

    return response

def create_vote(incident_id: int, user_id: str, upvotes: int, downvotes: int, supabase: Client):
    
    response = supabase.table("votes").insert({
        "incident_id": incident_id,
        "voter_id": user_id,
        "upvote": upvotes,
        "downvote": downvotes
    }).execute()
    
    return response.data

def update_vote(incident_id: int, user_id: str, upvotes: int, downvotes: int, supabase: Client):
    
    response = supabase.table("votes").update({
        "upvote": upvotes,
        "downvote": downvotes
    }).eq("incident_id", incident_id).eq("voter_id", user_id).execute()
    
    return response.data

def vote(vote_data: votes.Votes, current_user: user.User = Depends(dependencies.get_current_user)):
    
    supabase = db.get_supabase_client()
    
    try:
        
        check_incident_exists(vote_data.incident_id, supabase)
        
        vote_response = get_user_vote(vote_data.incident_id, current_user.id, supabase)
        
        if vote_response.data:
            return update_vote(vote_data.incident_id, current_user.id, vote_data.upvotes, vote_data.downvotes, supabase)
        else:
            return create_vote(vote_data.incident_id, current_user.id, vote_data.upvotes, vote_data.downvotes, supabase)
        
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Vote creation failed: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vote creation failed: {e}",
        )