from app.core.config import settings
from supabase import Client, create_client


def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client instance.
    """
    url: str = settings.SUPABASE_URL
    key: str = settings.SUPABASE_KEY
    
    return create_client(url, key)
