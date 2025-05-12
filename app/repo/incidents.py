from fastapi import HTTPException, status
from ..core import db
from ..schemas import user, incident
from gotrue.errors import AuthApiError
from typing import List

def get_all_incidents(token: str) -> List[incident.ShowIncident]:
    
    supabase = db.get_supabase_client(token=token)
    
    try:
        
        response = supabase.table("incident").select("*").execute()
        
        return response.data
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You are not logged in to get all incidents: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting all incidents: {e}"
        )
        
        
def create_incident(incident_data: incident.CreateIncident, token: str, user_id: str):
    
    supabase = db.get_supabase_client(token=token)
    
    try:
        
        response = supabase.table('incident').insert({
            "content": incident_data.content,
            "user_id": user_id 
        }).execute()
        
        return response.data
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You are not logged in to create an incident: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating an incident: {e}"
        )
        
def get_incident_by_id(incident_id: int, token: str, user_id: str):
    
    supabase = db.get_supabase_client(token=token)
    
    try:
        
        response = supabase.rpc(
            "get_particular_incident_stats",
            {
                'p_incident_id': incident_id,
                'p_user_id': user_id
            }
        ).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident not found with id: {incident_id}"
            )
            
        return response.data
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You are not logged in to get an incident: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting an incident: {e}"
        )
        
def incident_home(token: str, user_id: str):
    
    supabase = db.get_supabase_client(token=token)
    
    try:
        
        response = supabase.rpc(
            "get_incidents_with_stats",
            {
                'p_user_id': user_id
            }
        ).order("created_at", desc=True).execute()
        
        return response.data
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You are not logged in to get incidents: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting incidents: {e}"
        )