from fastapi import APIRouter, Depends, HTTPException, status
from ..core import db, dependencies
from ..schemas import user, incident, votes
from gotrue.errors import AuthApiError

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote_incident(vote_data: votes.Votes, current_user: user.User = Depends(dependencies.get_current_user)):
    
    token = current_user.token
    
    supabase = db.get_supabase_client(token)
    
    try:
        # Check if the incident exists
        incident_response = supabase.table("incident").select("*").eq("id", vote_data.incident_id).execute()
        
        # If not then raise an exception
        if not incident_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident with ID {vote_data.incident_id} not found.",
            )
        
        # Check if the user has already voted
        vote_response = supabase.table("votes").select("*").eq("incident_id", vote_data.incident_id).eq("voter_id", current_user.id).execute()
        
        if vote_response.data:
            update_vote_response = supabase.table("votes").update({
                "upvote": vote_data.upvotes,
                "downvote": vote_data.downvotes
            }).eq("incident_id", vote_data.incident_id).eq("voter_id", current_user.id).execute()
        
            return update_vote_response.data
        else:
            insert_vote_response = supabase.table("votes").insert({
                "incident_id": vote_data.incident_id,
                "voter_id": current_user.id,
                "upvote": vote_data.upvotes,
                "downvote": vote_data.downvotes
            }).execute()
            
            return insert_vote_response.data
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vote creation failed: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}"
        )