"""Audio analysis service using librosa."""
import librosa
import numpy as np
import soundfile as sf
from typing import Tuple, List
from pathlib import Path

from app.models.schemas import (
    AudioFeatures,
    AudioQualityAnalysis,
    FrequencyBalance,
    MusicCharacteristics,
)


class AudioAnalyzer:
    """Analyzes audio files and extracts features."""

    def __init__(self):
        self.sample_rate = 22050  # Standard for librosa

    def analyze_file(self, file_path: str) -> Tuple[AudioFeatures, AudioQualityAnalysis, MusicCharacteristics]:
        """
        Analyze an audio file and extract all features.

        Args:
            file_path: Path to the audio file

        Returns:
            Tuple of (AudioFeatures, AudioQualityAnalysis, MusicCharacteristics)
        """
        # Load audio
        y, sr = librosa.load(file_path, sr=self.sample_rate)

        # Extract features
        features = self._extract_features(y, sr)
        quality = self._analyze_quality(y, sr, features)
        characteristics = self._analyze_characteristics(y, sr, features)

        return features, quality, characteristics

    def _extract_features(self, y: np.ndarray, sr: int) -> AudioFeatures:
        """Extract basic audio features."""
        # Duration
        duration = librosa.get_duration(y=y, sr=sr)

        # Tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # Loudness (approximation)
        rms = librosa.feature.rms(y=y)[0]
        loudness_db = 20 * np.log10(np.mean(rms) + 1e-10)

        # Dynamic range
        dynamic_range = np.max(rms) - np.min(rms)

        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]

        return AudioFeatures(
            duration=float(duration),
            tempo=float(tempo),
            loudness_db=float(loudness_db),
            dynamic_range=float(dynamic_range),
            spectral_centroid=float(np.mean(spectral_centroids)),
            spectral_rolloff=float(np.mean(spectral_rolloff)),
            zero_crossing_rate=float(np.mean(zero_crossing_rate)),
            rms_energy=float(np.mean(rms))
        )

    def _analyze_quality(self, y: np.ndarray, sr: int, features: AudioFeatures) -> AudioQualityAnalysis:
        """Analyze audio quality and provide scores."""

        # Calculate LUFS approximation (simplified)
        lufs = features.loudness_db - 3.0  # Rough conversion

        # Loudness score (target: -14 LUFS for streaming)
        loudness_diff = abs(lufs - (-14.0))
        loudness_score = max(0, 100 - (loudness_diff * 5))

        # Dynamic range score (higher is better, but not too high)
        dr_score = min(100, features.dynamic_range * 1000)
        dr_score = 100 - abs(dr_score - 70) * 1.5  # Target around 70

        # Frequency balance
        freq_balance = self._analyze_frequency_balance(y, sr)
        balance_score = (freq_balance.bass + freq_balance.mid + freq_balance.high) / 3 * 100

        # Clarity (based on spectral contrast)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        clarity = float(np.mean(np.std(spectral_contrast, axis=1)))
        clarity_normalized = min(1.0, clarity / 30.0)

        # Clipping detection
        clipping_detected = np.any(np.abs(y) > 0.99)

        # Overall quality score
        quality_score = (
            loudness_score * 0.25 +
            dr_score * 0.20 +
            balance_score * 0.25 +
            clarity_normalized * 100 * 0.20 +
            (0 if clipping_detected else 10)
        )

        # Generate issues and suggestions
        issues = []
        suggestions = []

        if lufs < -18:
            issues.append(f"Track is too quiet ({lufs:.1f} LUFS)")
            suggestions.append("Increase overall loudness to around -14 LUFS for streaming platforms")
        elif lufs > -10:
            issues.append(f"Track is too loud ({lufs:.1f} LUFS)")
            suggestions.append("Reduce loudness to prevent distortion and listener fatigue")

        if features.dynamic_range < 0.05:
            issues.append("Very compressed - limited dynamic range")
            suggestions.append("Reduce compression to preserve dynamics and musicality")

        if clipping_detected:
            issues.append("Clipping detected - audio peaks exceed maximum level")
            suggestions.append("Lower master volume and check for distortion")

        if freq_balance.bass < 0.3:
            suggestions.append("Consider adding more bass presence for fuller sound")
        elif freq_balance.bass > 0.8:
            suggestions.append("Bass might be overpowering - consider reducing low-end")

        if freq_balance.high < 0.3:
            suggestions.append("Add more high-frequency content for brightness and clarity")

        return AudioQualityAnalysis(
            score=max(0, min(100, quality_score)),
            loudness_lufs=lufs,
            dynamic_range=features.dynamic_range,
            frequency_balance=freq_balance,
            clarity_score=clarity_normalized,
            clipping_detected=clipping_detected,
            issues=issues,
            suggestions=suggestions
        )

    def _analyze_frequency_balance(self, y: np.ndarray, sr: int) -> FrequencyBalance:
        """Analyze frequency spectrum balance."""
        # Compute spectral centroid and rolloff for frequency analysis
        stft = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)

        # Define frequency ranges (Hz)
        bass_range = (20, 250)
        mid_range = (250, 4000)
        high_range = (4000, 20000)

        # Calculate energy in each band
        bass_energy = np.mean(stft[(freqs >= bass_range[0]) & (freqs < bass_range[1])])
        mid_energy = np.mean(stft[(freqs >= mid_range[0]) & (freqs < mid_range[1])])
        high_energy = np.mean(stft[(freqs >= high_range[0]) & (freqs < high_range[1])])

        # Normalize
        total_energy = bass_energy + mid_energy + high_energy
        if total_energy > 0:
            bass_norm = bass_energy / total_energy * 3  # Scale to 0-1 range
            mid_norm = mid_energy / total_energy * 3
            high_norm = high_energy / total_energy * 3
        else:
            bass_norm = mid_norm = high_norm = 0.5

        return FrequencyBalance(
            bass=min(1.0, bass_norm),
            mid=min(1.0, mid_norm),
            high=min(1.0, high_norm)
        )

    def _analyze_characteristics(self, y: np.ndarray, sr: int, features: AudioFeatures) -> MusicCharacteristics:
        """Analyze high-level music characteristics."""

        # Determine energy level
        if features.rms_energy > 0.15:
            energy = "high"
        elif features.rms_energy > 0.08:
            energy = "medium"
        else:
            energy = "low"

        # Estimate genre based on tempo and spectral features
        genre = self._estimate_genre(features)

        # Estimate mood based on various features
        mood = self._estimate_mood(features, energy)

        # Analyze structure
        structure = self._analyze_structure(y, sr, features.duration)

        return MusicCharacteristics(
            genre=genre,
            mood=mood,
            energy=energy,
            structure=structure
        )

    def _estimate_genre(self, features: AudioFeatures) -> str:
        """Estimate genre based on audio features."""
        tempo = features.tempo
        zcr = features.zero_crossing_rate

        if tempo > 140:
            if zcr > 0.1:
                return "EDM/Electronic"
            return "Fast Pop/Dance"
        elif tempo > 120:
            if zcr > 0.08:
                return "Pop/Dance"
            return "Hip-hop/Trap"
        elif tempo > 90:
            return "Pop/Rock"
        else:
            if zcr < 0.05:
                return "Ballad/Slow"
            return "R&B/Soul"

    def _estimate_mood(self, features: AudioFeatures, energy: str) -> str:
        """Estimate mood based on features."""
        # Use spectral centroid and energy as mood indicators
        brightness = features.spectral_centroid / 3000.0  # Normalize

        if energy == "high":
            if brightness > 1.5:
                return "Energetic & Bright"
            return "Energetic & Dark"
        elif energy == "medium":
            if brightness > 1.2:
                return "Uplifting"
            return "Melancholic"
        else:
            if brightness > 1.0:
                return "Calm & Peaceful"
            return "Dark & Atmospheric"

    def _analyze_structure(self, y: np.ndarray, sr: int, duration: float) -> str:
        """Analyze song structure."""
        # Detect beats and analyze structure
        try:
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)

            # Estimate intro length (first ~10% or first significant beat pattern)
            intro_length = min(beat_times[4] if len(beat_times) > 4 else 10, duration * 0.1)

            # Rough structure estimation
            if intro_length > 20:
                structure = f"Long intro (~{int(intro_length)}s)"
            elif intro_length > 10:
                structure = f"Medium intro (~{int(intro_length)}s)"
            else:
                structure = f"Short intro (~{int(intro_length)}s)"

            # Add duration context
            if duration < 150:  # < 2:30
                structure += ", Short format"
            elif duration < 210:  # < 3:30
                structure += ", Standard format"
            else:
                structure += ", Extended format"

            return structure
        except:
            return f"Standard structure (~{int(duration)}s total)"
