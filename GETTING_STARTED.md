# Getting Started with Song Score AI

Complete setup guide for running the Song Score AI webapp locally.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **FFmpeg** - Required for audio processing
- **API Key** - OpenAI or Anthropic (for persona evaluations)

### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Suno_Personas
```

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `backend/.env` and add your API key:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

**OR** if using Anthropic:
```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
```

### 3. Set Up Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
```

Edit `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # If not already activated
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Open Your Browser

Visit: **http://localhost:3000**

You should see the upload page!

## Usage

1. **Upload an MP3**: Drag and drop or click to browse
2. **Wait for Analysis**: Usually takes 30-60 seconds
3. **View Results**: See scores, personas, and suggestions

## API Keys

### Getting an OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy it to your `.env` file

### Getting an Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Get your API key
4. Copy it to your `.env` file

## Troubleshooting

### Backend Issues

**Error: "No module named 'librosa'"**
```bash
pip install -r requirements.txt
```

**Error: "FFmpeg not found"**
- Install FFmpeg (see Prerequisites above)
- Restart your terminal after installation

**Error: "Invalid API key"**
- Check your API key in `.env`
- Ensure no extra spaces or quotes
- Verify the key is active in your provider's dashboard

### Frontend Issues

**Error: "Module not found"**
```bash
rm -rf node_modules
npm install
```

**Error: "Cannot connect to backend"**
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify no firewall is blocking the connection

**Build errors:**
```bash
rm -rf .next
npm run dev
```

### Upload Issues

**Error: "File too large"**
- Maximum file size is 10MB
- Try compressing your MP3

**Error: "Only MP3 files supported"**
- Convert your file to MP3 format
- Use online tools or FFmpeg:
  ```bash
  ffmpeg -i input.wav output.mp3
  ```

## Configuration

### Backend Configuration

Edit `backend/app/config.py` or use environment variables:

```python
# File Upload
MAX_FILE_SIZE_MB = 10
MAX_DURATION_SECONDS = 600  # 10 minutes

# LLM
LLM_PROVIDER = "openai"  # or "anthropic"
OPENAI_MODEL = "gpt-4-turbo-preview"
ANTHROPIC_MODEL = "claude-3-sonnet-20240229"

# CORS
CORS_ORIGINS = "http://localhost:3000,http://localhost:3001"
```

### Frontend Configuration

Edit `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, change to your deployed backend URL.

## File Structure

```
Suno_Personas/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # API app
│   │   ├── routers/     # API routes
│   │   ├── services/    # Business logic
│   │   └── models/      # Data models
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── app/            # Pages
│   ├── components/     # React components
│   ├── lib/            # Utilities
│   └── package.json
├── ARCHITECTURE.md     # System architecture
├── README.md           # Project overview
└── GETTING_STARTED.md  # This file
```

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Check [backend/README.md](./backend/README.md) for API docs
- Check [frontend/README.md](./frontend/README.md) for component docs

## Production Deployment

### Backend

**Option 1: Railway**
```bash
railway up
```

**Option 2: Fly.io**
```bash
fly launch
```

**Option 3: Docker**
```bash
docker build -t song-score-ai-backend ./backend
docker run -p 8000:8000 song-score-ai-backend
```

### Frontend

**Vercel (Recommended):**
```bash
cd frontend
vercel
```

**Netlify:**
```bash
cd frontend
npm run build
# Deploy the .next folder
```

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the architecture documentation
- Open an issue on GitHub

## License

MIT License - See LICENSE file for details

---

**Happy analyzing!** 🎵
