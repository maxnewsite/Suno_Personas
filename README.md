# 🎵 Song Score AI

An AI-powered webapp that analyzes music tracks generated with SUNO AI and provides comprehensive feedback on success potential, audience reactions, and technical quality.

## ✨ Features

- **Success Potential Scoring**: Get a data-driven prediction of your track's hit potential (0-100)
- **10 Diverse Personas**: See how different listener types (TikTok teens, indie nerds, audiophiles, etc.) react to your music
- **Technical Audio Analysis**: Detailed assessment of loudness, dynamic range, frequency balance, and mix quality
- **Actionable Insights**: Receive specific suggestions to improve your track
- **Visual Analytics**: Interactive radar chart showing strengths and weaknesses

## 🎯 What Gets Analyzed

### 1. Audio Quality Score (0-100)
- Loudness (LUFS measurement)
- Dynamic range
- Frequency balance (bass/mid/high)
- Voice clarity
- Clipping and distortion detection

### 2. Artistic Appeal Score (0-100)
- Hook memorability
- Song structure effectiveness
- Musical coherence
- Originality
- Emotional impact

### 3. Hit Potential Score (0-100)
- Aggregated persona ratings
- Market positioning
- Radio-friendliness
- Viral potential

## 👥 The 10 Personas

1. **Teen TikTok Pop Lover** (16) - Fast hooks, viral potential
2. **Indie/Alternative Nerd** (28) - Originality, non-mainstream appeal
3. **Mainstream Radio Listener** (35) - Strong chorus, clean production
4. **Clubbing EDM/Techno Lover** (25) - Energy, build-ups, drops
5. **Hip-hop/Trap Fan** (22) - Flow, beats, bass
6. **Film/Games Music Lover** (30) - Atmosphere, cinematic quality
7. **Casual Listener** (29) - Smooth, chill vibes
8. **Latin/World Music Enthusiast** (27) - Rhythm, groove, danceable
9. **Audiophile/Sound Engineer** (40) - Mix quality, stereo image
10. **Music Business A&R** (35) - Commercial viability, playlist potential

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- OpenAI API key or Anthropic API key (for persona evaluations)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/song-score-ai.git
cd song-score-ai
```

2. **Set up the backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Set up the frontend**
```bash
cd ../frontend
npm install
```

5. **Run the application**

Backend:
```bash
cd backend
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` to use the app!

## 📁 Project Structure

```
song-score-ai/
├── frontend/              # Next.js frontend
│   ├── app/              # App router pages
│   ├── components/       # React components
│   └── lib/              # Utilities and API client
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI application
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic
│   │   └── models/      # Data models
│   └── requirements.txt
├── docs/                 # Documentation
└── README.md
```

## 🎨 Tech Stack

**Frontend:**
- Next.js 14+ (React framework)
- TypeScript
- Tailwind CSS (styling)
- Recharts (data visualization)

**Backend:**
- FastAPI (Python web framework)
- librosa (audio analysis)
- pydub (audio processing)
- OpenAI/Anthropic API (LLM for personas)

## 📊 How It Works

1. **Upload**: User uploads an MP3 file (max 10MB, up to 4 minutes)
2. **Audio Analysis**: Backend extracts technical features using librosa
3. **Persona Evaluation**: AI generates responses from 10 different listener personas
4. **Scoring**: System calculates three main scores plus radar chart metrics
5. **Results**: Interactive dashboard displays all insights and suggestions

## 🎯 Use Cases

- **SUNO/Udio Creators**: Validate your AI-generated tracks before publishing
- **Content Creators**: Check if your audio has viral potential
- **Beatmakers**: Pre-screen tracks before sending demos
- **Music Producers**: Get objective feedback on mix quality
- **Independent Artists**: Understand how different audiences perceive your music

## 🔒 Privacy & Security

- Files are processed temporarily and deleted after analysis
- No tracks are stored permanently
- No user data is collected (in MVP version)
- All processing happens server-side

## 🛣️ Roadmap

### Phase 1: MVP (Current)
- ✅ Core analysis engine
- ✅ 10 persona system
- ✅ Basic UI/UX
- ✅ Radar chart visualization

### Phase 2: Enhancements
- [ ] User accounts & history
- [ ] Compare multiple tracks
- [ ] Genre-specific analysis
- [ ] Downloadable PDF reports
- [ ] Advanced audio fingerprinting

### Phase 3: Advanced Features
- [ ] A/B testing suggestions
- [ ] Mastering recommendations
- [ ] Collaboration features
- [ ] API access for developers
- [ ] Mobile app

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## 💬 Feedback & Support

- Report issues: [GitHub Issues](https://github.com/yourusername/song-score-ai/issues)
- Feature requests: [Discussions](https://github.com/yourusername/song-score-ai/discussions)

## 🙏 Credits

Built with inspiration from music industry A&R practices and modern AI capabilities.

---

**Made with ❤️ for the SUNO AI music community**
