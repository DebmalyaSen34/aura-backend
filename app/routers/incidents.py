from fastapi import APIRouter, Depends, HTTPException, status
from ..core import db, dependencies
from ..schemas import user, incident
from gotrue.errors import AuthApiError
from typing import List

router = APIRouter(
    tags=["incidents"],
    prefix="/incidents",
)

@router.get("/get_incidents")
def get_all_incidents(current_user: user.User = Depends(dependencies.get_current_user)):
    return True

@router.post("/create_incident")
def create_incident(incident_data: incident.CreateIncident, current_user: user.User = Depends(dependencies.get_current_user)):
    
    supabase = db.get_supabase_client()
    
    try:
        response = supabase.table("incident").insert({
            "content": incident_data.content,
            "user_id": current_user.id  
        }).execute()
        
        return response.data
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incident creation failed: {e}",
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"Error details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )

@router.get("/incident-home", status_code=status.HTTP_200_OK, response_model=List[incident.ShowIncident])
def incident_home(current_user: user.User = Depends(dependencies.get_current_user)):
    
    supabase = db.get_supabase_client()
    
    try:
        
        response = supabase.rpc(
            "get_incidents_with_stats",
            {
                'p_user_id': current_user.id
            }
        ).order("created_at", desc=True).execute()
        
        return response.data
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incident retrieval failed: {e}",
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"Error details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )