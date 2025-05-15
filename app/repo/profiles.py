from fastapi import HTTPException, status, File, UploadFile
from ..core import db
from gotrue.errors import AuthApiError
from ..schemas import user
from typing import Optional
from supabase import Client

def _handle_db_error(e: Exception) -> None:
    if isinstance(e, AuthApiError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication Error: {str(e)}"
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database Error: {str(e)}"
    )

def _get_supabase_client(token: Optional[str] = None):
    return db.get_supabase_client(token=token)

def get_user(user_id: str, token: str) -> dict:
    try:
        supabase = _get_supabase_client(token)
        # user_data = supabase.table("profiles").select("""
        #     *,
        #     incident:incident(
        #         id,
        #         content,
        #         created_at,
        #         total_upvotes,
        #         total_downvotes,
        #         total_comments
        #     )
        # """).eq("id", user_id).execute()
        
        user_data = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        
        user_incidents_data = supabase.rpc("fetch_user_incidents").execute()
        
        if not user_data.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {
            "user": user_data.data,
            "incidents": user_incidents_data.data
        }
    except Exception as e:
        _handle_db_error(e)

def get_user_by_id(user_id: str, token: str) -> dict:
    try:
        supabase = _get_supabase_client(token)
        response = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return response.data
    except Exception as e:
        _handle_db_error(e)

def update_user(user_id: str, request: user.UpdateUser, token: str) -> dict:
    try:
        supabase = _get_supabase_client(token)
        response = supabase.table("profiles").update(
            request.model_dump(exclude_unset=True)
        ).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return response.data
    except Exception as e:
        _handle_db_error(e)
        
        
def _store_profile_image(file_content: bytes, file_content_type: str, unique_filename: str, supabase: Client) -> str:
    try:
        supabase.storage.from_("profile-pics").remove([unique_filename])
    except Exception:
        pass
        
    response = supabase.storage.from_("profile-pics").upload(
        unique_filename,
        file_content,
        file_options={
            "content-type": file_content_type,
        }
    )
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to upload image to storage"
        )
    
    # Get the public URL correctly according to Supabase documentation
    result = supabase.storage.from_("profile-pics").get_public_url(unique_filename)
    
    # For older versions of Supabase client, the structure might be different
    if isinstance(result, dict) and 'publicUrl' in result:
        return result['publicUrl']
    elif hasattr(result, 'publicUrl'):
        return result.publicUrl
    elif isinstance(result, dict) and 'data' in result and 'publicUrl' in result['data']:
        return result['data']['publicUrl']
    else:
        # Construct manually as a fallback
        project_ref = supabase.supabase_url.split('https://')[1].split('.')[0]
        return f"https://{project_ref}.supabase.co/storage/v1/object/public/profile-pics/{unique_filename}"

def _insert_profile_image(user_id: str, profile_image_url: str, supabase: Client) -> dict:
    try:
        response = supabase.table("profiles").update(
            {'profile_image': profile_image_url}
        ).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update the profile image in the database"
            )
        
        return {
            "message": "Image uploaded successfully",
            "url": profile_image_url
        }
    except Exception as e:
        _handle_db_error(e)

def upload_profile_image(token: str, user_id: str, file: UploadFile = File(...)) -> dict:
    supabase = _get_supabase_client(token)
    
    try:
        file_content = file.file.read()
        
        # Validate file extension
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        unique_filename = f"{user_id}/profile.{file_extension}"
        
        profile_image_url = _store_profile_image(
            file_content=file_content,
            file_content_type=file.content_type,
            unique_filename=unique_filename,
            supabase=supabase
        )
        
        return _insert_profile_image(
            user_id=user_id,
            profile_image_url=profile_image_url,
            supabase=supabase
        )
        
    except Exception as e:
        _handle_db_error(e)
        
        
def get_liked_incidents(token: str, user_id: str) -> dict:
    
    supabase = _get_supabase_client(token)
    
    try:
        
        
        response = supabase.rpc(
            "fetch_user_upvoted_incidents",
            params={
                'request_user_id': user_id,
            }
        ).execute()
        
    
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No liked incidents found"
            )
        
        return response.data
        
    except Exception as e:
        _handle_db_error(e)