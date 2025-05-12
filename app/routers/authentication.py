# Authentication routes for user signup, login, and logout

from ..schemas import user
from ..core import db, dependencies
from ..utilities import user_utility
from gotrue.errors import AuthApiError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    tags=["authentication"],
    prefix="/auth",
)

# Signup endpoint
@router.post("/signup")
def register(request: user.User):
    
    # Supabase client
    supabase = db.get_supabase_client()
    
    # Create user and sign up them
    try:
        auth_response = supabase.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
                "options": {
                    "data": {
                        "display_name": request.name,
                    }
                }
            }
        )
        
        supabase_with_token = db.get_supabase_client(token=auth_response.session.access_token)
        
        # Create a profile for the user
        supabase_with_token.table("profiles").insert({
            "id": auth_response.user.id,
            "created_at": auth_response.user.created_at.isoformat(),
            "name": auth_response.user.user_metadata["display_name"],
        }).execute()

        return auth_response

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {e}",
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )
    
    return user_utility.get_cleaned_user_data(auth_response.user)

# Login endpoint
@router.post("/login", status_code=status.HTTP_200_OK)
def login(request: OAuth2PasswordRequestForm = Depends()):
    
    # Supabase client
    supabase = db.get_supabase_client()
    
    # Sign in user
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": request.username,
                "password": request.password,
            }
        )
        
        # Get the access token and token type
        access_token = response.session.access_token
        
        supabase_with_token = db.get_supabase_client(token=access_token)
        
        # Return the access token and token type
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    except AuthApiError as e: # Handle authentication errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e: # Handle other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )


@router.post("/logout")
def logout(current_user: user.User = Depends(dependencies.get_current_user)):
    # Supabase client
    
    token = current_user.session.access_token if hasattr(current_user, 'session') else None
    
    supabase = db.get_supabase_client(token=token)

    try:
        # Sign out user
        response = supabase.auth.sign_out()        
        return True
    except AuthApiError as e: # Handle authentication errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You are not logged in to logout: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e: # Handle other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )

# Get user endpoint
@router.get("/user")
def get_user(current_user: user.User = Depends(dependencies.get_current_user)):
    
    token = current_user.token
    supabase = db.get_supabase_client(token=token)
    
    try:
        
        user_data = supabase.table("profiles").select("*").eq("id", current_user.id).single().execute()
        
        return user_data
        
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You are not logged in to get user data: {e}",
        )
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )