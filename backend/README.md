# Song Score AI - Backend

FastAPI backend for analyzing music tracks generated with SUNO AI.

## Features

- Audio analysis using librosa
- LLM-powered persona evaluations
- RESTful API endpoints
- Async processing
- Multi-persona scoring system

## Setup

### Prerequisites

- Python 3.11 or higher
- pip
- OpenAI API key OR Anthropic API key

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
# Choose your LLM provider
LLM_PROVIDER=openai  # or anthropic

# Add your API key
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=your-key-here
```

### Running the Server

Development mode with auto-reload:
```bash
uvicorn app.main:app --reload
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /api/upload
Upload an MP3 file for analysis.

**Request:**
- Content-Type: multipart/form-data
- Body: MP3 file (max 10MB)

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "message": "Your track is being analyzed..."
}
```

### GET /api/status/{job_id}
Check analysis status.

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "progress": 0.7
}
```

### GET /api/analyze/{job_id}
Get analysis results.

**Response:** See schemas in `app/models/schemas.py`

## Configuration

Edit `backend/app/config.py` or use environment variables:

- `MAX_FILE_SIZE_MB`: Maximum upload size (default: 10)
- `MAX_DURATION_SECONDS`: Maximum track length (default: 600)
- `LLM_PROVIDER`: "openai" or "anthropic"
- `OPENAI_MODEL`: GPT model to use
- `ANTHROPIC_MODEL`: Claude model to use

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── routers/
│   │   └── analyze.py       # API routes
│   ├── services/
│   │   ├── audio_analyzer.py   # Audio processing
│   │   ├── persona_engine.py   # LLM integration
│   │   └── scorer.py           # Scoring logic
│   └── models/
│       ├── personas.py      # Persona definitions
│       └── schemas.py       # Pydantic models
└── requirements.txt
```

## The 10 Personas

1. **Teen TikTok Pop Lover** (16) - Viral potential, fast hooks
2. **Indie/Alternative Nerd** (28) - Originality, authenticity
3. **Mainstream Radio Listener** (35) - Commercial appeal
4. **Clubbing EDM/Techno Lover** (25) - Energy, drops
5. **Hip-hop/Trap Fan** (22) - Flow, beats, bass
6. **Film/Games Music Lover** (30) - Atmosphere, cinematic
7. **Casual Listener** (29) - Chill vibes
8. **Latin/World Music Enthusiast** (27) - Rhythm, groove
9. **Audiophile/Sound Engineer** (40) - Production quality
10. **Music Business A&R** (35) - Commercial viability

## Troubleshooting

### Import Error: librosa
Make sure you have FFmpeg installed:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### API Key Issues
- Verify your API key is correctly set in `.env`
- Check that `LLM_PROVIDER` matches your chosen provider
- Ensure your API key has sufficient credits/quota

### File Upload Issues
- Maximum file size: 10MB
- Only MP3 format supported
- Check file permissions in `temp_uploads/` directory

## License

MIT License
