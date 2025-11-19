# Song Score AI - Architecture Plan

## Overview
A webapp that analyzes music tracks (MP3) generated with SUNO AI and provides:
- Success potential scoring
- Reactions from 10 diverse personas
- Technical audio quality assessment
- Actionable improvement suggestions

---

## 1. System Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
│   - Upload UI   │
│   - Results     │
│   - Radar Chart │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend       │
│   (FastAPI)     │
│   - File Upload │
│   - Audio Proc  │
│   - LLM Engine  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│Audio │  │ LLM  │
│Analy │  │(GPT) │
│sis  │  │      │
└──────┘  └──────┘
```

---

## 2. Core Components

### 2.1 Frontend (Next.js + React)

**Pages:**
- `/` - Landing page with upload interface
- `/results/[id]` - Analysis results page

**Key Features:**
- Drag & drop MP3 upload (max 10MB)
- Real-time processing status
- Interactive radar chart (Chart.js/Recharts)
- Responsive design (mobile-first)
- Dark/Light theme

**Tech Stack:**
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- Recharts (for radar chart)
- React Hook Form (upload validation)

### 2.2 Backend (Python + FastAPI)

**Endpoints:**
```
POST   /api/upload          - Upload MP3 file
GET    /api/analyze/{id}    - Get analysis results
GET    /api/status/{id}     - Check processing status
```

**Tech Stack:**
- FastAPI (async web framework)
- Python 3.11+
- Uvicorn (ASGI server)
- Redis (job queue - optional for v1)

### 2.3 Audio Analysis Module

**Library:** librosa + pydub

**Metrics Extracted:**
- Loudness (LUFS approximation)
- Dynamic range (RMS analysis)
- Frequency balance (spectral centroid, rolloff)
- Tempo & beat strength
- Voice clarity (using spectral contrast)
- Clipping detection
- Duration & structure

**Output:**
```json
{
  "technical_score": 85,
  "loudness_lufs": -14.2,
  "dynamic_range": 8.5,
  "frequency_balance": {
    "bass": 0.7,
    "mid": 0.8,
    "high": 0.6
  },
  "clarity": 0.82,
  "issues": ["Slight clipping detected at 2:15"]
}
```

### 2.4 LLM Persona Engine

**Model:** OpenAI GPT-4 or Claude API

**Process:**
1. Extract audio features (tempo, genre estimate, mood)
2. Generate text summary of track characteristics
3. Send to LLM with 10 persona prompts
4. Parse structured responses

**Persona Definitions:**
```python
PERSONAS = [
    {
        "id": "tiktok_teen",
        "name": "Teen TikTok Pop Lover",
        "age": 16,
        "description": "Loves fast-paced tracks, immediate hooks, first 20s crucial",
        "weights": {"hook": 0.9, "originality": 0.5, "production": 0.6}
    },
    {
        "id": "indie_nerd",
        "name": "Indie/Alternative Nerd",
        "age": 28,
        "description": "Values originality, lyrics, non-mainstream arrangements",
        "weights": {"hook": 0.5, "originality": 0.95, "production": 0.7}
    },
    # ... 8 more personas
]
```

**LLM Prompt Structure:**
```
You are a {persona.name}, {persona.age} years old. {persona.description}

Analyze this track:
- Genre: {genre}
- Tempo: {tempo} BPM
- Mood: {mood}
- Duration: {duration}
- Structure: {structure}
- Technical Quality: {quality_score}/100

Provide:
1. Rating (0-100)
2. Playlist likelihood (0-100)
3. Brief comment (1-2 sentences)

Respond in JSON format.
```

---

## 3. Scoring System

### 3.1 Audio Quality Score (0-100)

**Calculation:**
```python
score = weighted_average([
    (loudness_score, 0.25),      # Target: -14 LUFS
    (dynamic_range_score, 0.20),  # Not over-compressed
    (frequency_balance, 0.25),    # Balanced spectrum
    (clarity_score, 0.20),        # Voice audibility
    (no_artifacts, 0.10)          # No clipping/noise
])
```

**Output:**
- Score: 0-100
- 3 improvement suggestions

### 3.2 Artistic Appeal Score (0-100)

**Dimensions:**
- Hook memorability (from LLM + repetition analysis)
- Structure appropriateness (intro length, chorus placement)
- Coherence (style consistency)
- Originality (compared to reference tracks)
- Emotional impact (LLM evaluation)

### 3.3 Hit Potential Score (0-100)

**Calculation:**
```python
hit_score = weighted_average([
    (mainstream_personas_avg, 0.4),  # Radio, TikTok, A&R
    (all_personas_avg, 0.3),
    (technical_score, 0.15),
    (artistic_score, 0.15)
])
```

**Persona Weights:**
- Mainstream Radio: 2x
- TikTok Teen: 2x
- A&R: 2.5x
- Others: 1x

### 3.4 Final Output

```json
{
  "overall_score": 78,
  "scores": {
    "audio_quality": 85,
    "artistic_appeal": 72,
    "hit_potential": 76
  },
  "radar_chart": {
    "hook": 80,
    "originality": 65,
    "emotion": 75,
    "radio_friendly": 82,
    "sound_design": 85
  },
  "personas": [
    {
      "name": "Teen TikTok Pop Lover",
      "rating": 85,
      "playlist_likelihood": 90,
      "comment": "Love the catchy hook! First 20 seconds grab attention perfectly."
    }
    // ... 9 more
  ],
  "suggestions": [
    "Shorten intro from 25s to 15s for better engagement",
    "Boost vocal presence in chorus by 2-3dB",
    "Add slight compression to drums for more punch"
  ]
}
```

---

## 4. Data Flow

### Upload → Analysis → Results

```
1. User uploads MP3
   ↓
2. Backend validates file (size, format)
   ↓
3. Generate unique job ID
   ↓
4. Audio Analysis Module processes file
   ├─ Extract technical features
   ├─ Detect genre, tempo, mood
   └─ Calculate audio quality score
   ↓
5. LLM Persona Engine
   ├─ Generate 10 persona evaluations
   └─ Calculate artistic & hit scores
   ↓
6. Aggregate results
   ├─ Combine all scores
   ├─ Generate suggestions
   └─ Create radar chart data
   ↓
7. Return results to frontend
   ↓
8. Display interactive results page
```

---

## 5. Tech Stack Summary

### Frontend
- **Framework:** Next.js 14+ (TypeScript)
- **Styling:** Tailwind CSS
- **Charts:** Recharts
- **Forms:** React Hook Form + Zod
- **HTTP Client:** Fetch API / Axios

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Audio:** librosa, pydub, soundfile
- **LLM:** OpenAI API / Anthropic Claude
- **Validation:** Pydantic
- **Server:** Uvicorn

### Infrastructure (MVP)
- **Hosting:** Vercel (frontend) + Railway/Fly.io (backend)
- **Storage:** Local file system (temp files)
- **Database:** JSON files (for MVP) → PostgreSQL (later)

---

## 6. File Structure

```
song-score-ai/
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Upload page
│   │   ├── results/
│   │   │   └── [id]/page.tsx     # Results page
│   │   └── layout.tsx
│   ├── components/
│   │   ├── UploadForm.tsx
│   │   ├── RadarChart.tsx
│   │   ├── PersonaCard.tsx
│   │   ├── ScoreDisplay.tsx
│   │   └── Suggestions.tsx
│   ├── lib/
│   │   └── api.ts                # API client
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app
│   │   ├── routers/
│   │   │   └── analyze.py        # Analysis endpoints
│   │   ├── services/
│   │   │   ├── audio_analyzer.py # Audio processing
│   │   │   ├── persona_engine.py # LLM integration
│   │   │   └── scorer.py         # Scoring logic
│   │   ├── models/
│   │   │   ├── personas.py       # Persona definitions
│   │   │   └── schemas.py        # Pydantic models
│   │   └── config.py
│   ├── requirements.txt
│   └── README.md
├── docs/
│   └── ARCHITECTURE.md
└── README.md
```

---

## 7. MVP Features (Phase 1)

**Must Have:**
- ✅ MP3 upload (max 10MB)
- ✅ Audio quality analysis
- ✅ 10 persona evaluations
- ✅ 3 core scores (Quality, Artistic, Hit Potential)
- ✅ Radar chart visualization
- ✅ Top 3 improvement suggestions
- ✅ Responsive UI

**Nice to Have (Phase 2):**
- User accounts & history
- Compare multiple tracks
- Genre-specific analysis
- Downloadable PDF report
- Batch processing
- A/B testing suggestions

---

## 8. Development Phases

### Phase 1: Core MVP (Week 1-2)
1. Set up project structure
2. Backend: Audio analysis module
3. Backend: LLM persona integration
4. Frontend: Upload UI
5. Frontend: Results display
6. Integration & testing

### Phase 2: Enhancement (Week 3)
1. Improve UI/UX
2. Add radar chart interactivity
3. Optimize LLM prompts
4. Performance improvements
5. Error handling & validation

### Phase 3: Polish (Week 4)
1. Documentation
2. Deployment setup
3. Analytics integration
4. User feedback loop
5. Launch preparation

---

## 9. Key Challenges & Solutions

### Challenge 1: Accurate Audio Analysis
**Solution:** Use librosa for robust feature extraction + validate against known reference tracks

### Challenge 2: LLM Cost & Speed
**Solution:** Batch persona prompts, use GPT-4-mini for speed, cache common patterns

### Challenge 3: Large File Uploads
**Solution:** Client-side validation, streaming upload, temporary storage with cleanup

### Challenge 4: Consistent Scoring
**Solution:** Normalize scores against reference dataset, use weighted averages

---

## 10. API Endpoints Detail

### POST /api/upload
```
Request:
- multipart/form-data
- file: MP3 (max 10MB)

Response:
{
  "job_id": "uuid-string",
  "status": "processing",
  "estimated_time": 30
}
```

### GET /api/analyze/{job_id}
```
Response:
{
  "status": "completed",
  "results": { /* full analysis object */ }
}
```

---

## 11. Security & Validation

- File size limit: 10MB
- File type validation: MP3 only
- Duration limit: 10 minutes max
- Rate limiting: 10 uploads/hour per IP (MVP)
- Input sanitization for all file names
- Temporary file cleanup after processing

---

## 12. Performance Targets

- Upload processing: < 30 seconds
- Audio analysis: < 10 seconds
- LLM evaluation: < 20 seconds
- Total time: < 1 minute per track
- Frontend load time: < 2 seconds

---

## 13. Monitoring & Analytics

**Track:**
- Upload success/failure rate
- Average processing time
- Most common score ranges
- Persona distribution patterns
- User engagement metrics

---

This architecture provides a solid foundation for building a production-ready Song Score AI webapp that can scale and evolve based on user feedback.
