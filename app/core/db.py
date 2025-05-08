import os
from supabase import create_client, Client
from dotenv import load_dotenv
from supabase.client import ClientOptions

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """
    Create a Supabase client instance.
    """
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in environment variables.")
    
    return create_client(url, key)