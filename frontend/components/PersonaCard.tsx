'use client';

import { PersonaEvaluation } from '@/lib/api';

interface PersonaCardProps {
  persona: PersonaEvaluation;
}

const getScoreColor = (score: number): string => {
  if (score >= 75) return 'text-green-400';
  if (score >= 50) return 'text-yellow-400';
  return 'text-red-400';
};

const getScoreBackground = (score: number): string => {
  if (score >= 75) return 'bg-green-500/20 border-green-500/50';
  if (score >= 50) return 'bg-yellow-500/20 border-yellow-500/50';
  return 'bg-red-500/20 border-red-500/50';
};

export default function PersonaCard({ persona }: PersonaCardProps) {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-lg p-5 border border-white/10 hover:border-white/20 transition-all">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-white">{persona.persona_name}</h4>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-bold border ${getScoreBackground(persona.rating)}`}>
          <span className={getScoreColor(persona.rating)}>{persona.rating.toFixed(0)}</span>
        </div>
      </div>

      <p className="text-sm text-gray-300 mb-3 min-h-[60px]">
        {persona.comment}
      </p>

      <div className="flex items-center gap-2 text-xs">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-gray-400">Playlist Chance</span>
            <span className={`font-medium ${getScoreColor(persona.playlist_likelihood)}`}>
              {persona.playlist_likelihood.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-1.5">
            <div
              className={`h-1.5 rounded-full transition-all ${
                persona.playlist_likelihood >= 75
                  ? 'bg-green-500'
                  : persona.playlist_likelihood >= 50
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${persona.playlist_likelihood}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
