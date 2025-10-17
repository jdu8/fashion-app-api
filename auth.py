"""
Authentication utilities for Fashion App
Handles JWT verification and user management
"""
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Security scheme for JWT bearer tokens
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Verify JWT token and return current user.

    This function is used as a dependency in protected routes.
    Raises HTTPException if token is invalid.
    """
    token = credentials.credentials

    try:
        # Verify the JWT token with Supabase
        response = supabase.auth.get_user(token)

        if not response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

        return response.user.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}"
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
) -> Optional[dict]:
    """
    Optional authentication - returns None if no token provided.

    Use this for routes that work with or without authentication.
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        response = supabase.auth.get_user(token)

        if not response.user:
            return None

        return response.user.model_dump()
    except Exception:
        return None


def get_user_profile(user_id: str) -> Optional[dict]:
    """
    Get user profile from database.
    """
    try:
        result = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None


def create_user_profile(user_id: str, email: str, display_name: Optional[str] = None, avatar_url: Optional[str] = None) -> dict:
    """
    Create user profile in database after signup.

    This should be called automatically after both email and OAuth signup.
    """
    try:
        # Check if profile already exists
        existing = get_user_profile(user_id)
        if existing:
            return existing

        # Create new profile
        profile_data = {
            "id": user_id,
            "email": email,
            "display_name": display_name or email.split("@")[0],
            "avatar_url": avatar_url,
            "sass_level": 3,  # Default sass level
        }

        result = supabase.table("user_profiles").insert(profile_data).execute()
        return result.data[0]

    except Exception as e:
        print(f"Error creating user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user profile: {str(e)}")


def update_user_profile(user_id: str, updates: dict) -> dict:
    """
    Update user profile with allowed fields only.
    """
    # Only allow updating specific fields
    allowed_fields = [
        "display_name", "avatar_url", "body_type", "height_cm", "weight_kg",
        "gender_style", "notes", "typical_schedule", "default_occasions",
        "works_from_home", "has_dress_code", "dress_code_notes",
        "sass_level", "location", "body_reference_photos"
    ]

    update_data = {k: v for k, v in updates.items() if k in allowed_fields}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    try:
        result = supabase.table("user_profiles").update(update_data).eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")
