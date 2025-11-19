"""
Hybrid persona evaluation engine.

Intelligently routes requests between local LLM and cloud APIs
for optimal cost/quality balance.
"""

import asyncio
from typing import List, Optional
from app.models.schemas import (
    PersonaEvaluation,
    AudioFeatures,
    AudioQualityAnalysis,
    MusicCharacteristics,
)
from app.models.personas import PERSONAS, Persona
from app.services.persona_engine import PersonaEngine
from app.services.local_llm_client import LocalLLMClient
from app.config import settings


class HybridPersonaEngine:
    """
    Hybrid engine that uses local LLM when possible, cloud APIs when needed.

    Strategy:
    1. Try local model first (fast, cheap)
    2. Fall back to cloud for critical personas if local quality is poor
    3. Cache results aggressively
    """

    def __init__(self):
        self.cloud_engine = PersonaEngine()
        self.local_client = None

        # Initialize local client if configured
        if hasattr(settings, 'local_llm_url') and settings.local_llm_url:
            self.local_client = LocalLLMClient(settings.local_llm_url)

        # Define critical personas that should use cloud if local quality is poor
        self.critical_personas = {"anr_executive", "mainstream_radio", "tiktok_teen"}

    async def evaluate_all_personas(
        self,
        features: AudioFeatures,
        quality: AudioQualityAnalysis,
        characteristics: MusicCharacteristics,
        tier: str = "free"  # "free" or "paid"
    ) -> List[PersonaEvaluation]:
        """
        Evaluate track from all personas using hybrid approach.

        Free tier: 3 personas (Mainstream, TikTok, A&R)
        Paid tier: 10 personas (all)
        """

        # Select personas based on tier
        if tier == "free":
            selected_personas = [
                p for p in PERSONAS
                if p.id in {"mainstream_radio", "tiktok_teen", "anr_executive"}
            ]
        else:
            selected_personas = PERSONAS

        # Check if local model is available
        local_available = False
        if self.local_client:
            local_available = await self.local_client.health_check()

        if local_available:
            # Try local model first
            evaluations = await self._evaluate_with_hybrid(
                selected_personas,
                features,
                quality,
                characteristics
            )
        else:
            # Fall back to cloud only
            print("⚠️  Local model unavailable, using cloud API")
            evaluations = await self.cloud_engine.evaluate_all_personas(
                features,
                quality,
                characteristics
            )
            # Filter to selected personas
            evaluations = [
                ev for ev in evaluations
                if any(p.id == ev.persona_id for p in selected_personas)
            ]

        return evaluations

    async def _evaluate_with_hybrid(
        self,
        personas: List[Persona],
        features: AudioFeatures,
        quality: AudioQualityAnalysis,
        characteristics: MusicCharacteristics
    ) -> List[PersonaEvaluation]:
        """
        Hybrid evaluation strategy.

        1. Try all personas with local model (batch)
        2. For critical personas, validate quality
        3. Re-run critical personas with cloud if quality is poor
        """

        # Step 1: Batch evaluate with local model
        local_results = await self.local_client.evaluate_batch(
            personas,
            features,
            characteristics,
            quality.score
        )

        # Step 2: Check which failed or need cloud backup
        final_results = []
        cloud_tasks = []

        for i, (persona, local_result) in enumerate(zip(personas, local_results)):
            if local_result is None:
                # Local failed, must use cloud
                cloud_tasks.append((i, persona))
            elif persona.id in self.critical_personas:
                # Critical persona - validate quality
                if self._is_quality_acceptable(local_result):
                    final_results.append((i, local_result))
                else:
                    # Quality too low, re-run with cloud
                    cloud_tasks.append((i, persona))
            else:
                # Non-critical persona, accept local result
                final_results.append((i, local_result))

        # Step 3: Run cloud API for failed/critical personas
        if cloud_tasks:
            cloud_results = await asyncio.gather(*[
                self.cloud_engine._evaluate_single_persona(
                    persona,
                    features,
                    quality,
                    characteristics
                )
                for _, persona in cloud_tasks
            ])

            for (idx, _), result in zip(cloud_tasks, cloud_results):
                final_results.append((idx, result))

        # Sort by original index and return
        final_results.sort(key=lambda x: x[0])
        return [result for _, result in final_results]

    def _is_quality_acceptable(self, evaluation: PersonaEvaluation) -> bool:
        """
        Check if local model response quality is acceptable.

        Basic heuristics:
        - Rating is in valid range
        - Comment is not empty or generic
        - Playlist likelihood makes sense relative to rating
        """

        if not (0 <= evaluation.rating <= 100):
            return False

        if not (0 <= evaluation.playlist_likelihood <= 100):
            return False

        if not evaluation.comment or len(evaluation.comment) < 20:
            return False

        # Check for generic fallback responses
        if "unable to generate" in evaluation.comment.lower():
            return False

        # Rating and playlist likelihood should be correlated
        rating_diff = abs(evaluation.rating - evaluation.playlist_likelihood)
        if rating_diff > 40:  # Too different
            return False

        return True

    async def close(self):
        """Clean up resources."""
        if self.local_client:
            await self.local_client.close()
