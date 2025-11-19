'use client';

interface ScoreDisplayProps {
  label: string;
  score: number;
  description?: string;
  large?: boolean;
}

const getScoreColor = (score: number): string => {
  if (score >= 75) return 'from-green-500 to-emerald-500';
  if (score >= 50) return 'from-yellow-500 to-orange-500';
  return 'from-red-500 to-pink-500';
};

const getScoreLabel = (score: number): string => {
  if (score >= 85) return 'Excellent';
  if (score >= 75) return 'Great';
  if (score >= 60) return 'Good';
  if (score >= 50) return 'Fair';
  return 'Needs Work';
};

export default function ScoreDisplay({ label, score, description, large = false }: ScoreDisplayProps) {
  const colorClass = getScoreColor(score);
  const scoreLabel = getScoreLabel(score);

  if (large) {
    return (
      <div className="text-center">
        <div className="inline-block relative">
          <div className={`w-32 h-32 rounded-full bg-gradient-to-br ${colorClass} flex items-center justify-center`}>
            <div className="w-28 h-28 rounded-full bg-slate-900 flex flex-col items-center justify-center">
              <div className="text-4xl font-bold text-white">{score.toFixed(0)}</div>
              <div className="text-xs text-gray-400">/ 100</div>
            </div>
          </div>
        </div>
        <div className="mt-4">
          <div className="text-2xl font-bold text-white">{label}</div>
          <div className={`text-sm font-medium bg-gradient-to-r ${colorClass} text-transparent bg-clip-text`}>
            {scoreLabel}
          </div>
          {description && (
            <div className="text-sm text-gray-400 mt-2">{description}</div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-lg p-5 border border-white/10">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-gray-400">{label}</h4>
        <span className={`text-2xl font-bold bg-gradient-to-r ${colorClass} text-transparent bg-clip-text`}>
          {score.toFixed(0)}
        </span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full bg-gradient-to-r ${colorClass} transition-all`}
          style={{ width: `${score}%` }}
        ></div>
      </div>
      <div className="text-xs text-gray-400">{scoreLabel}</div>
      {description && (
        <div className="text-xs text-gray-500 mt-2">{description}</div>
      )}
    </div>
  );
}
