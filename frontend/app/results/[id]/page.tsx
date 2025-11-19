'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { apiClient, AnalysisResult } from '@/lib/api';
import RadarChart from '@/components/RadarChart';
import PersonaCard from '@/components/PersonaCard';
import ScoreDisplay from '@/components/ScoreDisplay';
import Suggestions from '@/components/Suggestions';

export default function ResultsPage() {
  const params = useParams();
  const jobId = params.id as string;

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!jobId) return;

    const fetchResults = async () => {
      try {
        const data = await apiClient.pollForResults(jobId, (p) => {
          setProgress(p * 100);
        });
        setResult(data);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results');
        setLoading(false);
      }
    };

    fetchResults();
  }, [jobId]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <div className="text-6xl mb-6">🎵</div>
          <h1 className="text-3xl font-bold text-white mb-4">Analyzing Your Track...</h1>
          <p className="text-gray-400 mb-8">
            This usually takes 30-60 seconds. Please don't close this page.
          </p>
          <div className="w-full bg-gray-700 rounded-full h-3 mb-2">
            <div
              className="h-3 rounded-full bg-gradient-to-r from-primary-500 to-purple-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500">{progress.toFixed(0)}% complete</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <div className="text-6xl mb-6">❌</div>
          <h1 className="text-3xl font-bold text-white mb-4">Analysis Failed</h1>
          <p className="text-red-400 mb-8">{error}</p>
          <a
            href="/"
            className="inline-block px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
          >
            Try Again
          </a>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <p className="text-gray-400">No results found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">Analysis Complete!</h1>
          <p className="text-gray-400">
            Processed in {result.processing_time.toFixed(1)}s
          </p>
        </div>

        {/* Overall Score */}
        <div className="mb-12">
          <ScoreDisplay
            label="Overall Score"
            score={result.overall_score}
            description="Combined assessment of quality, artistry, and hit potential"
            large
          />
        </div>

        {/* Score Breakdown */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <ScoreDisplay
            label="Audio Quality"
            score={result.scores.audio_quality}
            description="Technical sound quality and production"
          />
          <ScoreDisplay
            label="Artistic Appeal"
            score={result.scores.artistic_appeal}
            description="Creativity and musical expression"
          />
          <ScoreDisplay
            label="Hit Potential"
            score={result.scores.hit_potential}
            description="Predicted commercial success"
          />
        </div>

        {/* Track Info */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 mb-12">
          <h3 className="text-xl font-semibold text-white mb-4">Track Characteristics</h3>
          <div className="grid md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-gray-400 mb-1">Genre</div>
              <div className="text-white font-medium">{result.characteristics.genre}</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Mood</div>
              <div className="text-white font-medium">{result.characteristics.mood}</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Energy</div>
              <div className="text-white font-medium capitalize">{result.characteristics.energy}</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Structure</div>
              <div className="text-white font-medium">{result.characteristics.structure}</div>
            </div>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="mb-12">
          <RadarChart data={result.radar_chart} />
        </div>

        {/* Audio Quality Details */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 mb-12">
          <h3 className="text-xl font-semibold text-white mb-4">Audio Quality Details</h3>
          <div className="grid md:grid-cols-3 gap-6 mb-4">
            <div>
              <div className="text-gray-400 text-sm mb-1">Loudness</div>
              <div className="text-white font-medium">{result.audio_quality.loudness_lufs.toFixed(1)} LUFS</div>
              <div className="text-xs text-gray-500">Target: -14 LUFS</div>
            </div>
            <div>
              <div className="text-gray-400 text-sm mb-1">Dynamic Range</div>
              <div className="text-white font-medium">{result.audio_quality.dynamic_range.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-gray-400 text-sm mb-1">Clarity</div>
              <div className="text-white font-medium">{(result.audio_quality.clarity_score * 100).toFixed(0)}%</div>
            </div>
          </div>

          <div className="mb-4">
            <div className="text-gray-400 text-sm mb-2">Frequency Balance</div>
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-500">Bass</span>
                  <span className="text-white">{(result.audio_quality.frequency_balance.bass * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-blue-500"
                    style={{ width: `${result.audio_quality.frequency_balance.bass * 100}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-500">Mid</span>
                  <span className="text-white">{(result.audio_quality.frequency_balance.mid * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-green-500"
                    style={{ width: `${result.audio_quality.frequency_balance.mid * 100}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-500">High</span>
                  <span className="text-white">{(result.audio_quality.frequency_balance.high * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-yellow-500"
                    style={{ width: `${result.audio_quality.frequency_balance.high * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {result.audio_quality.clipping_detected && (
            <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg">
              <p className="text-red-400 text-sm">⚠️ Clipping detected - audio peaks exceed maximum level</p>
            </div>
          )}

          {result.audio_quality.issues.length > 0 && (
            <div className="mt-4">
              <div className="text-gray-400 text-sm mb-2">Issues Found:</div>
              <ul className="space-y-1">
                {result.audio_quality.issues.map((issue, i) => (
                  <li key={i} className="text-sm text-yellow-400">• {issue}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Suggestions */}
        <div className="mb-12">
          <Suggestions suggestions={result.suggestions} />
        </div>

        {/* Persona Evaluations */}
        <div className="mb-12">
          <h3 className="text-2xl font-bold text-white mb-6">Listener Reactions</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {result.personas.map((persona) => (
              <PersonaCard key={persona.persona_id} persona={persona} />
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="text-center">
          <a
            href="/"
            className="inline-block px-8 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
          >
            Analyze Another Track
          </a>
        </div>
      </div>
    </div>
  );
}
