from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from routes import auth  # Import auth router

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

app = FastAPI(
    title="Fashion App API",
    description="Backend API for wardrobe management, virtual try-on, and AI-powered fashion recommendations",
    version="0.2.0"
)

# CORS middleware - allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Fashion App API is running",
        "status": "healthy",
        "shade_says": "Looking for fashion advice? You're in the right place."
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    db_status = "not configured"

    if supabase:
        try:
            # Test connection by checking if we can access the database
            # This will fail if credentials are wrong
            response = supabase.table('_test_connection').select("*").limit(1).execute()
            db_status = "connected"
        except Exception as e:
            # Even if table doesn't exist, connection works if we get a proper error
            if "does not exist" in str(e) or "relation" in str(e):
                db_status = "connected (no tables yet)"
            else:
                db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "database": db_status,
        "version": "0.1.0",
        "supabase_configured": supabase is not None
    }

@app.get("/api/test-db")
async def test_database():
    """Test Supabase connection"""
    if not supabase:
        return {
            "success": False,
            "message": "Supabase not configured. Check your .env file."
        }

    try:
        # Simple connection test
        response = supabase.table('_test').select("*").limit(1).execute()
        return {
            "success": True,
            "message": "Supabase connection successful!",
            "shade_says": "Database is connected. Now let's actually build something."
        }
    except Exception as e:
        error_str = str(e)
        # If table doesn't exist, that's actually fine - means connection works
        if ("does not exist" in error_str or
            "relation" in error_str or
            "PGRST205" in error_str or
            "Could not find the table" in error_str):
            return {
                "success": True,
                "message": "Supabase connection successful! (No tables created yet)",
                "shade_says": "Connected to the database. Empty closet, but we're connected."
            }
        return {
            "success": False,
            "message": f"Connection failed: {error_str}"
        }
