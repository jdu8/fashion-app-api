"""
Authentication routes for Fashion App
Handles email/password signup, login, and user profile management
Google OAuth is handled client-side, this ensures profile creation
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from auth import (
    get_current_user,
    get_user_profile,
    create_user_profile,
    update_user_profile,
    supabase
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    body_type: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    gender_style: Optional[str] = None
    notes: Optional[list[str]] = None
    typical_schedule: Optional[dict] = None
    default_occasions: Optional[list[str]] = None
    works_from_home: Optional[bool] = None
    has_dress_code: Optional[bool] = None
    dress_code_notes: Optional[str] = None
    sass_level: Optional[int] = None
    location: Optional[str] = None
    body_reference_photos: Optional[list[str]] = None


# ============================================================================
# EMAIL/PASSWORD AUTHENTICATION
# ============================================================================

@router.post("/signup")
async def signup_with_email(request: SignupRequest):
    """
    Sign up a new user with email and password.

    Creates both auth user and user profile.
    Returns user data and session info.
    """
    try:
        # Sign up user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Signup failed")

        # Create user profile
        profile = create_user_profile(
            user_id=auth_response.user.id,
            email=request.email,
            display_name=request.display_name
        )

        return {
            "user": auth_response.user.model_dump(),
            "session": auth_response.session.model_dump() if auth_response.session else None,
            "profile": profile,
            "message": "Account created successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login_with_email(request: LoginRequest):
    """
    Log in an existing user with email and password.

    Returns user data, session, and profile.
    """
    try:
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })

        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Get user profile
        profile = get_user_profile(auth_response.user.id)

        return {
            "user": auth_response.user.model_dump(),
            "session": auth_response.session.model_dump() if auth_response.session else None,
            "profile": profile,
            "message": "Logged in successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Log out the current user.

    Requires valid JWT token.
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# OAUTH CALLBACK (ensure profile creation for OAuth users)
# ============================================================================

@router.post("/oauth/callback")
async def oauth_callback(current_user: dict = Depends(get_current_user)):
    """
    Handle OAuth callback - ensure user profile exists.

    This is called after successful Google OAuth on the frontend.
    Creates profile if it doesn't exist (for first-time OAuth users).
    """
    try:
        user_id = current_user.get("id")
        email = current_user.get("email")
        user_metadata = current_user.get("user_metadata", {})

        # Get or create user profile
        profile = get_user_profile(user_id)

        if not profile:
            # Create profile for OAuth user
            profile = create_user_profile(
                user_id=user_id,
                email=email,
                display_name=user_metadata.get("full_name") or email.split("@")[0],
                avatar_url=user_metadata.get("avatar_url")
            )

        return {
            "user": current_user,
            "profile": profile,
            "message": "OAuth authentication successful"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# USER PROFILE MANAGEMENT
# ============================================================================

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get the current user's profile.

    Requires authentication.
    """
    try:
        user_id = current_user.get("id")
        profile = get_user_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {
            "user": current_user,
            "profile": profile
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/me")
async def update_current_user_profile(
    updates: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update the current user's profile.

    Only specified fields will be updated.
    Requires authentication.
    """
    try:
        user_id = current_user.get("id")

        # Convert Pydantic model to dict, excluding None values
        update_data = updates.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        profile = update_user_profile(user_id, update_data)

        return {
            "profile": profile,
            "message": "Profile updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ONBOARDING STATUS
# ============================================================================

@router.get("/onboarding-status")
async def check_onboarding_status(current_user: dict = Depends(get_current_user)):
    """
    Check if user has completed onboarding.

    Returns which steps are complete and which are pending.
    """
    try:
        user_id = current_user.get("id")
        profile = get_user_profile(user_id)

        if not profile:
            return {
                "completed": False,
                "steps": {
                    "display_name": False,
                    "body_photos": False,
                    "preferences": False
                }
            }

        # Check onboarding completion
        has_display_name = bool(profile.get("display_name"))
        has_body_photos = bool(profile.get("body_reference_photos"))
        has_preferences = bool(profile.get("gender_style") or profile.get("location"))

        completed = has_display_name  # Minimum requirement

        return {
            "completed": completed,
            "steps": {
                "display_name": has_display_name,
                "body_photos": has_body_photos,
                "preferences": has_preferences
            },
            "profile": profile
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
