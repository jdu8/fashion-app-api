from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Fashion App API",
    description="Backend API for wardrobe management and virtual try-on",
    version="0.1.0"
)

# CORS middleware - allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {
        "status": "ok",
        "database": "not configured yet",
        "version": "0.1.0"
    }
