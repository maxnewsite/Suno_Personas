/**
 * API client for Song Score AI backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface UploadResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface StatusResponse {
  job_id: string;
  status: string;
  progress?: number;
  message?: string;
  error?: string;
}

export interface PersonaEvaluation {
  persona_id: string;
  persona_name: string;
  rating: number;
  playlist_likelihood: number;
  comment: string;
}

export interface RadarChartData {
  hook: number;
  originality: number;
  emotion: number;
  radio_friendly: number;
  sound_design: number;
}

export interface ScoreBreakdown {
  audio_quality: number;
  artistic_appeal: number;
  hit_potential: number;
}

export interface FrequencyBalance {
  bass: number;
  mid: number;
  high: number;
}

export interface AudioQualityAnalysis {
  score: number;
  loudness_lufs: number;
  dynamic_range: number;
  frequency_balance: FrequencyBalance;
  clarity_score: number;
  clipping_detected: boolean;
  issues: string[];
  suggestions: string[];
}

export interface MusicCharacteristics {
  genre: string;
  mood: string;
  energy: string;
  structure: string;
}

export interface AnalysisResult {
  job_id: string;
  overall_score: number;
  scores: ScoreBreakdown;
  radar_chart: RadarChartData;
  personas: PersonaEvaluation[];
  audio_quality: AudioQualityAnalysis;
  characteristics: MusicCharacteristics;
  suggestions: string[];
  processing_time: number;
}

export class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Upload an MP3 file for analysis
   */
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  /**
   * Check the status of an analysis job
   */
  async getStatus(jobId: string): Promise<StatusResponse> {
    const response = await fetch(`${this.baseURL}/api/status/${jobId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get status');
    }

    return response.json();
  }

  /**
   * Get analysis results
   */
  async getAnalysis(jobId: string): Promise<AnalysisResult> {
    const response = await fetch(`${this.baseURL}/api/analyze/${jobId}`);

    if (response.status === 202) {
      // Still processing
      throw new Error('PROCESSING');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get analysis');
    }

    return response.json();
  }

  /**
   * Poll for results until complete
   */
  async pollForResults(
    jobId: string,
    onProgress?: (progress: number) => void
  ): Promise<AnalysisResult> {
    const maxAttempts = 60; // 60 * 2 = 120 seconds max
    const pollInterval = 2000; // 2 seconds

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const result = await this.getAnalysis(jobId);
        return result;
      } catch (error) {
        if (error instanceof Error && error.message === 'PROCESSING') {
          // Still processing, check status
          const status = await this.getStatus(jobId);
          if (onProgress && status.progress) {
            onProgress(status.progress);
          }

          // Wait before next poll
          await new Promise(resolve => setTimeout(resolve, pollInterval));
          continue;
        }
        throw error;
      }
    }

    throw new Error('Analysis timeout - please try again');
  }
}

// Export singleton instance
export const apiClient = new APIClient();
