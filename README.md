# Fashion App - Backend API

FastAPI backend for wardrobe management, virtual try-on, and AI-powered fashion recommendations featuring **Shade**, your sassy ghost fashion advisor.

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Database**: Supabase (PostgreSQL)
- **AI/ML**:
  - Google Generative AI (image generation)
  - YOLO (clothing segmentation)
  - CLIP (similarity embeddings)
- **Deployment**: Google Cloud Platform

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
├── .env.example         # Environment template
└── venv/                # Virtual environment (not committed)
```

## Getting Started

### Prerequisites
- Python 3.9 or higher
- pip and virtualenv
- Supabase project with credentials

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd backend
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000
```

5. Run the development server:
```bash
uvicorn main:app --reload --port 8000
```

6. Visit the API:
- API Root: [http://localhost:8000](http://localhost:8000)
- Interactive Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Test DB: [http://localhost:8000/api/test-db](http://localhost:8000/api/test-db)

## Current API Endpoints

### `GET /`
Health check endpoint with Shade's greeting.

**Response:**
```json
{
  "message": "Fashion App API is running",
  "status": "healthy",
  "shade_says": "Looking for fashion advice? You're in the right place."
}
```

### `GET /api/health`
Detailed health check including database connection status.

**Response:**
```json
{
  "status": "ok",
  "database": "connected (no tables yet)",
  "version": "0.1.0",
  "supabase_configured": true
}
```

### `GET /api/test-db`
Test Supabase database connection.

**Response:**
```json
{
  "success": true,
  "message": "Supabase connection successful!",
  "shade_says": "Connected to the database. Empty closet, but we're connected."
}
```

## Development Phases

### Phase 1: Foundation ✅ (Current)
- ✅ Project setup with FastAPI and Supabase
- ✅ Basic health check endpoints
- 🚧 Authentication system
- 🚧 Database schema design

### Phase 2: Wardrobe Management (Next)
- Image upload and storage
- YOLO integration for clothing segmentation
- CLIP embeddings for similarity search
- Wardrobe CRUD operations

### Phase 3: Daily Outfit Suggestions
- Outfit generation algorithm
- Weather API integration
- Calendar integration
- Style preference learning

### Phase 4: Virtual Try-On
- Google Generative AI integration
- Avatar processing
- Try-on rendering

### Phase 5: Outfit Search
- Natural language search
- Vector similarity search
- Product catalog integration
- Ranking algorithm

## Character: Shade

Shade is the AI personality that provides fashion advice through LLM-generated responses. The character is:
- **Honest, not mean**: Tells the truth but supportive
- **Witty & sharp**: Quick comebacks, fashion-forward
- **Knowledgeable**: Understands style and trends
- **Secretly caring**: Acts aloof but genuinely helpful

## CORS Configuration

The API allows requests from:
- `http://localhost:3000` (Next.js development server)
- Additional origins can be configured in production

## Dependencies

Current dependencies (Phase 1):
```
fastapi           # Web framework
uvicorn[standard] # ASGI server
python-dotenv     # Environment variable management
supabase          # Supabase client
pydantic          # Data validation
```

Future dependencies will include:
- `ultralytics` (YOLO)
- `transformers` (CLIP)
- `google-generativeai` (Virtual try-on)
- `pillow` (Image processing)

## Development Workflow

1. **Write code** - Implement features incrementally
2. **Test** - Verify endpoints with FastAPI's interactive docs
3. **Document** - Update API documentation
4. **Move on** - Proceed to next feature

## Testing

FastAPI provides automatic interactive documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Use these to test endpoints directly in your browser.

## Deployment

Planned deployment on Google Cloud Platform:
- Cloud Run (containerized FastAPI app)
- Cloud Storage (image storage)
- Vertex AI (ML model serving)

## Related Repositories

- **Frontend**: fashion-app-web (Next.js application)
- **Guidelines**: Internal project documentation (not public)

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Uvicorn Documentation](https://www.uvicorn.org/)
