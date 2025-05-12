from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from gotrue.errors import AuthApiError
from . import db

# OAuth2PasswordBearer is a class that provides a way to extract the token from the request
#* It is used to extract the token from the request and validate it.
# The tokenUrl parameter is the URL where the token can be obtained.
#* In this case, it is set to "/auth/login", which is the login endpoint of the application.
#* This means that the token will be obtained from the login endpoint.
# The token will be passed as a Bearer token in the Authorization header of the request.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    supabase = db.get_supabase_client(token=token)
    
    try:
        user_response = supabase.auth.get_user(token)
        
        user = user_response.user
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not Found: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        class UserWithSession:
            
            def __init__(self, user, token):
                self.user = user
                self.token = token
                
                for key, value in user.__dict__.items():
                    setattr(self, key, value)        
        
        return UserWithSession(user, token)
        
    except AuthApiError as e:
        raise credentials_exception
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )