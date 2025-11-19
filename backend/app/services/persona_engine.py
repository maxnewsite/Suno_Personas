"""LLM-powered persona evaluation engine."""
import json
import asyncio
from typing import List, Dict
from openai import OpenAI
from anthropic import Anthropic

from app.config import settings
from app.models.personas import PERSONAS, Persona
from app.models.schemas import (
    PersonaEvaluation,
    MusicCharacteristics,
    AudioFeatures,
    AudioQualityAnalysis,
)


class PersonaEngine:
    """Manages persona-based evaluations using LLM."""

    def __init__(self):
        self.llm_provider = settings.llm_provider
        if self.llm_provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        elif self.llm_provider == "anthropic":
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    async def evaluate_all_personas(
        self,
        features: AudioFeatures,
        quality: AudioQualityAnalysis,
        characteristics: MusicCharacteristics
    ) -> List[PersonaEvaluation]:
        """
        Evaluate track from all persona perspectives.

        Args:
            features: Audio features
            quality: Audio quality analysis
            characteristics: Music characteristics

        Returns:
            List of persona evaluations
        """
        # Create evaluation tasks for all personas
        tasks = [
            self._evaluate_single_persona(persona, features, quality, characteristics)
            for persona in PERSONAS
        ]

        # Execute all evaluations concurrently
        evaluations = await asyncio.gather(*tasks)
        return evaluations

    async def _evaluate_single_persona(
        self,
        persona: Persona,
        features: AudioFeatures,
        quality: AudioQualityAnalysis,
        characteristics: MusicCharacteristics
    ) -> PersonaEvaluation:
        """Evaluate track from a single persona's perspective."""

        # Build the prompt
        prompt = self._build_persona_prompt(persona, features, quality, characteristics)

        # Get LLM response
        response = await self._call_llm(prompt)

        # Parse response
        evaluation = self._parse_evaluation_response(response, persona)

        return evaluation

    def _build_persona_prompt(
        self,
        persona: Persona,
        features: AudioFeatures,
        quality: AudioQualityAnalysis,
        characteristics: MusicCharacteristics
    ) -> str:
        """Build evaluation prompt for a persona."""

        prompt = f"""You are roleplaying as: {persona.name}, age {persona.age}.

Your profile: {persona.description}

You've just listened to a music track with these characteristics:

MUSICAL CHARACTERISTICS:
- Genre: {characteristics.genre}
- Mood: {characteristics.mood}
- Energy Level: {characteristics.energy}
- Tempo: {features.tempo:.0f} BPM
- Duration: {features.duration:.0f} seconds
- Structure: {characteristics.structure}

TECHNICAL QUALITY:
- Audio Quality Score: {quality.score:.0f}/100
- Loudness: {quality.loudness_lufs:.1f} LUFS
- Dynamic Range: {'High' if features.dynamic_range > 0.1 else 'Medium' if features.dynamic_range > 0.05 else 'Low'}
- Frequency Balance: Bass {quality.frequency_balance.bass*100:.0f}%, Mid {quality.frequency_balance.mid*100:.0f}%, High {quality.frequency_balance.high*100:.0f}%
- Clarity: {quality.clarity_score*100:.0f}%

IMPORTANT: Respond ONLY with a valid JSON object in this exact format:
{{
  "rating": <number 0-100>,
  "playlist_likelihood": <number 0-100>,
  "comment": "<your 1-2 sentence comment>"
}}

Your evaluation should reflect your persona's specific preferences and perspective.
- Rating: How much you like this track overall (0-100)
- Playlist Likelihood: Would you save this to your playlist? (0=never, 100=definitely)
- Comment: Brief reaction from your perspective (1-2 sentences)

Be authentic to your persona. Don't try to be overly nice or critical - just honest from your perspective."""

        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM API and return response."""

        if self.llm_provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a music listener providing honest feedback. "
                                   "Always respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content

        elif self.llm_provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.7,
                system="You are a music listener providing honest feedback. Always respond with valid JSON only.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

    def _parse_evaluation_response(self, response: str, persona: Persona) -> PersonaEvaluation:
        """Parse LLM response into PersonaEvaluation."""

        try:
            # Extract JSON from response
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            data = json.loads(response)

            return PersonaEvaluation(
                persona_id=persona.id,
                persona_name=persona.name,
                rating=float(data.get("rating", 50)),
                playlist_likelihood=float(data.get("playlist_likelihood", 50)),
                comment=str(data.get("comment", "No comment provided."))
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback if parsing fails
            return PersonaEvaluation(
                persona_id=persona.id,
                persona_name=persona.name,
                rating=50.0,
                playlist_likelihood=50.0,
                comment=f"[Evaluation unavailable - {str(e)}]"
            )

    def calculate_artistic_score(
        self,
        persona_evaluations: List[PersonaEvaluation],
        features: AudioFeatures
    ) -> float:
        """
        Calculate artistic appeal score based on persona evaluations.

        This aggregates evaluations weighted by persona characteristics.
        """
        # Average all persona ratings
        avg_rating = sum(p.rating for p in persona_evaluations) / len(persona_evaluations)

        # Factor in tempo consistency (songs with very appropriate tempo for genre score higher)
        tempo_factor = 1.0
        if 90 <= features.tempo <= 140:
            tempo_factor = 1.1  # Sweet spot for most genres

        # Duration appropriateness
        duration_factor = 1.0
        if 150 <= features.duration <= 240:  # 2:30 - 4:00
            duration_factor = 1.1
        elif features.duration < 120 or features.duration > 300:
            duration_factor = 0.9

        artistic_score = avg_rating * tempo_factor * duration_factor
        return min(100, max(0, artistic_score))
