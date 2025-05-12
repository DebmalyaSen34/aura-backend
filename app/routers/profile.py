from fastapi import APIRouter, Depends, HTTPException, status
from ..core import db, dependencies
from ..schemas import user, incident
from gotrue.errors import AuthApiError
from typing import List

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_user(current_user: user.User = Depends(dependencies.get_current_user)):
    
    token = current_user.token
    
    supabase = db.get_supabase_client(token=token)
    
    try:
        user_data = supabase.table("profiles").select("""
            *,
            incident:incident(
                id,
                content,
                created_at
            )
        """).eq("id", current_user.id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return user_data.data
    
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Authentication Error: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Error: {str(e)}")
        
@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=user.ShowUser)
def get_user_by_id(user_id: str, current_user: user.User = Depends(dependencies.get_current_user)):
    
    supabase = db.get_supabase_client()
    
    try:
        user_data = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        
        if not user_data.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found with id: {user_id}")
            
        return user_data.data
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication Error: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Error: {str(e)}")
        
@router.put("/", status_code=status.HTTP_200_OK)
def update_user(request: user.UpdateUser, current_user: user.User = Depends(dependencies.get_current_user)):
    
    supabase = db.get_supabase_client()
    
    try:
        
        user_data = supabase.table("profiles").update(request.model_dump(exclude_unset=True)).eq("id", current_user.id).execute()
        
        if not user_data.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return user_data.data
    
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Error: {str(e)}"
        )