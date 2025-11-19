"""Scoring and aggregation service."""
from typing import List, Dict
from app.models.schemas import (
    PersonaEvaluation,
    RadarChartData,
    ScoreBreakdown,
    AudioQualityAnalysis,
    MusicCharacteristics,
    AudioFeatures,
)
from app.models.personas import PERSONAS, calculate_weighted_persona_score
from app.config import settings


class Scorer:
    """Handles all scoring and aggregation logic."""

    def calculate_hit_potential(
        self,
        persona_evaluations: List[PersonaEvaluation],
        audio_quality_score: float,
        artistic_score: float
    ) -> float:
        """
        Calculate overall hit potential score.

        Args:
            persona_evaluations: List of persona evaluations
            audio_quality_score: Audio quality score (0-100)
            artistic_score: Artistic appeal score (0-100)

        Returns:
            Hit potential score (0-100)
        """
        # Get weighted persona score
        persona_ratings = {
            eval.persona_id: eval.rating
            for eval in persona_evaluations
        }
        weighted_persona_score = calculate_weighted_persona_score(persona_ratings)

        # Calculate hit potential using configured weights
        hit_score = (
            weighted_persona_score * settings.persona_weight +
            audio_quality_score * settings.audio_quality_weight +
            artistic_score * settings.artistic_appeal_weight
        )

        return min(100, max(0, hit_score))

    def calculate_overall_score(
        self,
        audio_quality_score: float,
        artistic_score: float,
        hit_potential_score: float
    ) -> float:
        """
        Calculate overall final score.

        This is a weighted combination emphasizing hit potential.
        """
        overall = (
            hit_potential_score * 0.5 +
            artistic_score * 0.3 +
            audio_quality_score * 0.2
        )
        return min(100, max(0, overall))

    def create_radar_chart_data(
        self,
        persona_evaluations: List[PersonaEvaluation],
        audio_quality: AudioQualityAnalysis,
        characteristics: MusicCharacteristics,
        features: AudioFeatures
    ) -> RadarChartData:
        """
        Create data for radar chart visualization.

        Dimensions:
        - Hook: How catchy/memorable
        - Originality: How unique/fresh
        - Emotion: Emotional impact
        - Radio-friendly: Commercial appeal
        - Sound Design: Production quality
        """

        # Hook score - based on structure and mainstream personas
        hook_score = self._calculate_hook_score(persona_evaluations, features)

        # Originality - based on indie/alternative personas and tempo uniqueness
        originality_score = self._calculate_originality_score(persona_evaluations, features)

        # Emotion - based on emotional personas and dynamic range
        emotion_score = self._calculate_emotion_score(persona_evaluations, audio_quality)

        # Radio-friendly - based on mainstream personas and duration
        radio_friendly_score = self._calculate_radio_friendly_score(persona_evaluations, features)

        # Sound design - primarily from audio quality
        sound_design_score = audio_quality.score

        return RadarChartData(
            hook=hook_score,
            originality=originality_score,
            emotion=emotion_score,
            radio_friendly=radio_friendly_score,
            sound_design=sound_design_score
        )

    def _calculate_hook_score(
        self,
        persona_evaluations: List[PersonaEvaluation],
        features: AudioFeatures
    ) -> float:
        """Calculate hook/catchiness score."""

        # Personas that care about hooks
        hook_personas = ["tiktok_teen", "mainstream_radio", "anr_executive", "hiphop_trap"]
        hook_ratings = [
            ev.rating for ev in persona_evaluations
            if ev.persona_id in hook_personas
        ]

        base_score = sum(hook_ratings) / len(hook_ratings) if hook_ratings else 50

        # Bonus for appropriate tempo (catchy songs often in 120-130 range)
        if 115 <= features.tempo <= 135:
            base_score *= 1.1

        return min(100, base_score)

    def _calculate_originality_score(
        self,
        persona_evaluations: List[PersonaEvaluation],
        features: AudioFeatures
    ) -> float:
        """Calculate originality score."""

        # Personas that value originality
        originality_personas = ["indie_nerd", "cinematic_lover", "hiphop_trap"]
        originality_ratings = [
            ev.rating for ev in persona_evaluations
            if ev.persona_id in originality_personas
        ]

        base_score = sum(originality_ratings) / len(originality_ratings) if originality_ratings else 50

        # Unusual tempos might indicate originality
        if features.tempo < 80 or features.tempo > 150:
            base_score *= 1.05

        return min(100, base_score)

    def _calculate_emotion_score(
        self,
        persona_evaluations: List[PersonaEvaluation],
        audio_quality: AudioQualityAnalysis
    ) -> float:
        """Calculate emotional impact score."""

        # Personas sensitive to emotion
        emotion_personas = ["indie_nerd", "cinematic_lover", "chill_casual"]
        emotion_ratings = [
            ev.rating for ev in persona_evaluations
            if ev.persona_id in emotion_personas
        ]

        base_score = sum(emotion_ratings) / len(emotion_ratings) if emotion_ratings else 50

        # Dynamic range contributes to emotional expression
        if audio_quality.dynamic_range > 0.08:
            base_score *= 1.1

        return min(100, base_score)

    def _calculate_radio_friendly_score(
        self,
        persona_evaluations: List[PersonaEvaluation],
        features: AudioFeatures
    ) -> float:
        """Calculate radio-friendliness score."""

        # Mainstream personas
        radio_personas = ["mainstream_radio", "anr_executive", "tiktok_teen"]
        radio_ratings = [
            ev.rating for ev in persona_evaluations
            if ev.persona_id in radio_personas
        ]

        base_score = sum(radio_ratings) / len(radio_ratings) if radio_ratings else 50

        # Ideal duration for radio (2:30 - 3:30)
        if 150 <= features.duration <= 210:
            base_score *= 1.15
        elif features.duration > 240:
            base_score *= 0.9

        return min(100, base_score)

    def generate_suggestions(
        self,
        audio_quality: AudioQualityAnalysis,
        features: AudioFeatures,
        persona_evaluations: List[PersonaEvaluation],
        radar_data: RadarChartData
    ) -> List[str]:
        """
        Generate actionable suggestions for improvement.

        Returns top 5-7 suggestions based on analysis.
        """
        suggestions = []

        # Add audio quality suggestions (already generated)
        suggestions.extend(audio_quality.suggestions[:2])

        # Duration suggestions
        if features.duration < 120:
            suggestions.append("Track is quite short - consider extending to 2:30-3:00 for better commercial appeal")
        elif features.duration > 240:
            suggestions.append("Track is long - consider shortening to 3:00-3:30 for better engagement")

        # Structure suggestions based on features
        if features.duration > 0:
            # Estimate intro percentage (rough)
            intro_threshold = 15  # seconds
            if intro_threshold / features.duration > 0.15:
                suggestions.append(f"Consider shortening intro to under 12 seconds for faster hook engagement")

        # Hook suggestions based on radar chart
        if radar_data.hook < 60:
            suggestions.append("Strengthen the hook/chorus - make it more memorable and repetitive")

        # Originality suggestions
        if radar_data.originality < 50:
            suggestions.append("Add unique elements to stand out - experiment with unexpected sounds or arrangements")

        # Radio-friendly suggestions
        if radar_data.radio_friendly < 60 and features.duration > 180:
            suggestions.append("For radio play, aim for 2:45-3:15 duration with clear verse-chorus structure")

        # Persona-specific suggestions
        low_rated_personas = [ev for ev in persona_evaluations if ev.rating < 50]
        if len(low_rated_personas) >= 7:
            suggestions.append("Track has polarizing elements - consider broader appeal or lean into niche audience")

        # Emotion suggestions
        if radar_data.emotion < 55:
            suggestions.append("Increase emotional impact through dynamics, vocal delivery, or melodic expression")

        # Return top suggestions (limit to 5-7)
        return suggestions[:7]

    def create_score_breakdown(
        self,
        audio_quality_score: float,
        artistic_score: float,
        hit_potential_score: float
    ) -> ScoreBreakdown:
        """Create score breakdown object."""
        return ScoreBreakdown(
            audio_quality=audio_quality_score,
            artistic_appeal=artistic_score,
            hit_potential=hit_potential_score
        )
