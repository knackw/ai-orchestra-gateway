from app.core.config import settings
from supabase import Client, create_client


def get_supabase_client(use_service_role: bool = False) -> Client:
    """
    Initialize and return a Supabase client instance.
    
    Args:
        use_service_role: If True, uses the service role key (bypasses RLS).
                         Default is False (uses anon key).
    """
    url: str = settings.SUPABASE_URL
    key: str = settings.SUPABASE_SERVICE_ROLE_KEY if use_service_role else settings.SUPABASE_KEY
    
    return create_client(url, key)
