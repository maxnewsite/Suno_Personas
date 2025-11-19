# Song Score AI - Frontend

Next.js 14 frontend for the Song Score AI application.

## Features

- Modern React with Next.js 14 (App Router)
- TypeScript for type safety
- Tailwind CSS for styling
- Recharts for data visualization
- Responsive design
- Real-time progress tracking

## Setup

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running the Application

Development mode:
```bash
npm run dev
```

Production build:
```bash
npm run build
npm start
```

The app will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home/upload page
│   ├── globals.css          # Global styles
│   └── results/
│       └── [id]/
│           └── page.tsx     # Results page
├── components/
│   ├── UploadForm.tsx       # File upload component
│   ├── RadarChart.tsx       # Radar chart visualization
│   ├── PersonaCard.tsx      # Persona evaluation card
│   ├── ScoreDisplay.tsx     # Score display component
│   └── Suggestions.tsx      # Suggestions list
├── lib/
│   └── api.ts               # API client
└── package.json
```

## Components

### UploadForm
Handles file selection and upload with drag-and-drop support.

### RadarChart
Displays 5-dimensional performance breakdown using Recharts.

### PersonaCard
Shows individual persona evaluation with rating and comment.

### ScoreDisplay
Displays scores with color-coded progress bars and labels.

### Suggestions
Lists actionable improvement suggestions.

## API Integration

The frontend communicates with the backend via the API client in `lib/api.ts`:

```typescript
import { apiClient } from '@/lib/api';

// Upload file
const response = await apiClient.uploadFile(file);

// Poll for results
const result = await apiClient.pollForResults(jobId, (progress) => {
  console.log(`Progress: ${progress * 100}%`);
});
```

## Customization

### Styling
Modify `tailwind.config.js` to customize the theme:
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      }
    }
  }
}
```

### API URL
Change the backend URL in `.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Building for Production

1. Build the application:
```bash
npm run build
```

2. Start production server:
```bash
npm start
```

## Deployment

### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Other Platforms
Build the static files and deploy the `.next` directory.

Make sure to set the environment variable:
- `NEXT_PUBLIC_API_URL`: Your backend API URL

## Troubleshooting

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings in backend
- Ensure backend is running and accessible

### Build Errors
- Clear `.next` directory: `rm -rf .next`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

## License

MIT License
