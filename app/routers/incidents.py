from fastapi import APIRouter, Depends, status
from ..core import dependencies
from ..schemas import user, incident
from typing import List
from ..repo import incidents

router = APIRouter(
    tags=["incidents"],
    prefix="/incidents",
)

@router.get("/get_incidents", status_code=status.HTTP_200_OK)
def get_all_incidents(current_user: user.User = Depends(dependencies.get_current_user)):
    
    token = current_user.token
    
    return incidents.get_all_incidents(token=token)

@router.post("/create_incident", status_code=status.HTTP_201_CREATED)
def create_incident(incident_data: incident.CreateIncident, current_user: user.User = Depends(dependencies.get_current_user)):
    
    token = current_user.token
    
    return incidents.create_incident(incident_data, token, current_user.id)

@router.get("/incident-home", status_code=status.HTTP_200_OK, response_model=List[incident.ShowIncident])
def incident_home(current_user: user.User = Depends(dependencies.get_current_user)):
    
    token = current_user.token
    
    return incidents.incident_home(token, current_user.id)

@router.get("/{incident_id}", status_code=status.HTTP_200_OK, response_model=incident.ShowIncident)
def get_incident_by_id(incident_id: int, current_user: user.User = Depends(dependencies.get_current_user)):
    
    token = current_user.token
    
    return incidents.get_incident_by_id(incident_id, token, current_user.id)