from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from ..core import db, dependencies
from ..schemas import user, incident
from gotrue.errors import AuthApiError
from typing import List
from ..repo import profiles

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_user(current_user: user.User = Depends(dependencies.get_current_user)):
    return profiles.get_user(current_user.id, current_user.token)
        
@router.get("/get_user_by_id/{user_id}", status_code=status.HTTP_200_OK, response_model=user.ShowUser)
def get_user_by_id(user_id: str, current_user: user.User = Depends(dependencies.get_current_user)):
    return profiles.get_user_by_id(user_id, current_user.token)
        
@router.put("/", status_code=status.HTTP_200_OK)
def update_user(request: user.UpdateUser, current_user: user.User = Depends(dependencies.get_current_user)):
    return profiles.update_user(current_user.id, request, current_user.token)
        
@router.post("/upload-profile-image", status_code=status.HTTP_200_OK)
def upload_profile_image(
    file: UploadFile = File(...),
    current_user: user.User = Depends(dependencies.get_current_user)
):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size (e.g., max 5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    file_size = 0
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size too large. Maximum size is 5MB"
            )
    
    # Reset file pointer after reading
    file.file.seek(0)
    
    return profiles.upload_profile_image(current_user.token, current_user.id, file)

@router.get("/user-liked-incidents", status_code=status.HTTP_200_OK)

def get_liked_incidents(current_user: user.User = Depends(dependencies.get_current_user)):
    
    token = current_user.token
    
    try:
        return profiles.get_liked_incidents(token=token, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )