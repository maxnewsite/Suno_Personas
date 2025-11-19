"""Pydantic schemas for API requests and responses."""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class AudioFeatures(BaseModel):
    """Technical audio features extracted from analysis."""
    duration: float
    tempo: float
    loudness_db: float
    dynamic_range: float
    spectral_centroid: float
    spectral_rolloff: float
    zero_crossing_rate: float
    rms_energy: float


class FrequencyBalance(BaseModel):
    """Frequency spectrum balance."""
    bass: float = Field(..., ge=0, le=1)
    mid: float = Field(..., ge=0, le=1)
    high: float = Field(..., ge=0, le=1)


class AudioQualityAnalysis(BaseModel):
    """Audio quality analysis results."""
    score: float = Field(..., ge=0, le=100)
    loudness_lufs: float
    dynamic_range: float
    frequency_balance: FrequencyBalance
    clarity_score: float = Field(..., ge=0, le=1)
    clipping_detected: bool
    issues: List[str] = []
    suggestions: List[str] = []


class PersonaEvaluation(BaseModel):
    """Evaluation from a single persona."""
    persona_id: str
    persona_name: str
    rating: float = Field(..., ge=0, le=100)
    playlist_likelihood: float = Field(..., ge=0, le=100)
    comment: str


class RadarChartData(BaseModel):
    """Data for radar chart visualization."""
    hook: float = Field(..., ge=0, le=100)
    originality: float = Field(..., ge=0, le=100)
    emotion: float = Field(..., ge=0, le=100)
    radio_friendly: float = Field(..., ge=0, le=100)
    sound_design: float = Field(..., ge=0, le=100)


class ScoreBreakdown(BaseModel):
    """Breakdown of all scores."""
    audio_quality: float = Field(..., ge=0, le=100)
    artistic_appeal: float = Field(..., ge=0, le=100)
    hit_potential: float = Field(..., ge=0, le=100)


class MusicCharacteristics(BaseModel):
    """High-level music characteristics."""
    genre: str
    mood: str
    energy: str  # low, medium, high
    structure: str  # description of song structure


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    job_id: str
    overall_score: float = Field(..., ge=0, le=100)
    scores: ScoreBreakdown
    radar_chart: RadarChartData
    personas: List[PersonaEvaluation]
    audio_quality: AudioQualityAnalysis
    characteristics: MusicCharacteristics
    suggestions: List[str]
    processing_time: float


class UploadResponse(BaseModel):
    """Response after file upload."""
    job_id: str
    status: str = "processing"
    message: str = "Your track is being analyzed..."


class StatusResponse(BaseModel):
    """Status check response."""
    job_id: str
    status: str  # processing, completed, failed
    progress: Optional[float] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    job_id: Optional[str] = None
