"""
Client for local LLM inference server.

Provides interface to fine-tuned local model with fallback to cloud APIs.
"""

import httpx
import asyncio
from typing import List, Optional
from app.models.schemas import PersonaEvaluation, AudioFeatures, MusicCharacteristics
from app.models.personas import Persona
from app.config import settings


class LocalLLMClient:
    """Client for local LLM inference server."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def evaluate_persona(
        self,
        persona: Persona,
        features: AudioFeatures,
        characteristics: MusicCharacteristics,
        quality_score: float
    ) -> PersonaEvaluation:
        """Evaluate a single persona using local model."""

        request_data = {
            "persona_id": persona.id,
            "persona_name": persona.name,
            "persona_age": persona.age,
            "persona_description": persona.description,
            "track_profile": {
                "genre": characteristics.genre,
                "tempo": features.tempo,
                "mood": characteristics.mood,
                "energy": characteristics.energy,
                "duration": features.duration,
                "quality_score": quality_score,
                "loudness_lufs": features.loudness_db - 3.0,  # Rough LUFS conversion
                "structure": characteristics.structure,
                "clarity_score": 0.75  # Placeholder
            }
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/evaluate",
                json=request_data
            )
            response.raise_for_status()
            data = response.json()

            return PersonaEvaluation(
                persona_id=persona.id,
                persona_name=persona.name,
                rating=data["rating"],
                playlist_likelihood=data["playlist_likelihood"],
                comment=data["comment"]
            )

        except Exception as e:
            print(f"Local LLM error for {persona.name}: {e}")
            # Return None to trigger fallback
            return None

    async def evaluate_batch(
        self,
        personas: List[Persona],
        features: AudioFeatures,
        characteristics: MusicCharacteristics,
        quality_score: float
    ) -> List[Optional[PersonaEvaluation]]:
        """Evaluate multiple personas in batch (faster)."""

        requests_data = []
        for persona in personas:
            requests_data.append({
                "persona_id": persona.id,
                "persona_name": persona.name,
                "persona_age": persona.age,
                "persona_description": persona.description,
                "track_profile": {
                    "genre": characteristics.genre,
                    "tempo": features.tempo,
                    "mood": characteristics.mood,
                    "energy": characteristics.energy,
                    "duration": features.duration,
                    "quality_score": quality_score,
                    "loudness_lufs": features.loudness_db - 3.0,
                    "structure": characteristics.structure,
                    "clarity_score": 0.75
                }
            })

        try:
            response = await self.client.post(
                f"{self.base_url}/evaluate_batch",
                json=requests_data
            )
            response.raise_for_status()
            results = response.json()

            evaluations = []
            for persona, data in zip(personas, results):
                evaluations.append(PersonaEvaluation(
                    persona_id=persona.id,
                    persona_name=persona.name,
                    rating=data["rating"],
                    playlist_likelihood=data["playlist_likelihood"],
                    comment=data["comment"]
                ))

            return evaluations

        except Exception as e:
            print(f"Batch local LLM error: {e}")
            return [None] * len(personas)

    async def health_check(self) -> bool:
        """Check if local model is available."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
