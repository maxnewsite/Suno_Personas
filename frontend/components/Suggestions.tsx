'use client';

interface SuggestionsProps {
  suggestions: string[];
}

export default function Suggestions({ suggestions }: SuggestionsProps) {
  if (suggestions.length === 0) {
    return (
      <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
        <h3 className="text-xl font-semibold text-white mb-4">Suggestions</h3>
        <p className="text-gray-400">No specific suggestions - your track is solid!</p>
      </div>
    );
  }

  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
      <h3 className="text-xl font-semibold text-white mb-4">
        💡 Suggestions for Improvement
      </h3>
      <ul className="space-y-3">
        {suggestions.map((suggestion, index) => (
          <li key={index} className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center text-sm font-bold">
              {index + 1}
            </span>
            <span className="text-gray-300 flex-1">{suggestion}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
