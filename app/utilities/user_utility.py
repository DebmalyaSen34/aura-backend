
from ..core import db

def get_cleaned_user_data(user_data):
    
    id = user_data.id
    email = user_data.email
    name = user_data.user_metadata.get("display_name", None)
    
    return {
        "id": id,
        "email": email,
        "name": name
    }