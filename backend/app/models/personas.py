"""Persona definitions for music evaluation."""
from typing import Dict, List
from pydantic import BaseModel


class PersonaWeights(BaseModel):
    """Evaluation weights for different aspects."""
    hook: float
    originality: float
    production: float
    emotion: float
    radio_friendly: float


class Persona(BaseModel):
    """Represents a listener persona."""
    id: str
    name: str
    age: int
    description: str
    weights: PersonaWeights
    priority_weight: float = 1.0  # For hit potential calculation


# Define the 10 personas
PERSONAS: List[Persona] = [
    Persona(
        id="tiktok_teen",
        name="Teen TikTok Pop Lover",
        age=16,
        description="Loves fast-paced tracks with immediate hooks. First 20 seconds are crucial. "
                    "Looks for viral potential and danceable beats. Attention span is short.",
        weights=PersonaWeights(
            hook=0.95,
            originality=0.5,
            production=0.6,
            emotion=0.6,
            radio_friendly=0.7
        ),
        priority_weight=2.0  # High weight for hit potential
    ),
    Persona(
        id="indie_nerd",
        name="Indie/Alternative Nerd",
        age=28,
        description="Values originality, meaningful lyrics, and non-mainstream arrangements. "
                    "Appreciates experimental sounds and authenticity. Dislikes over-production.",
        weights=PersonaWeights(
            hook=0.5,
            originality=0.95,
            production=0.7,
            emotion=0.85,
            radio_friendly=0.3
        ),
        priority_weight=1.0
    ),
    Persona(
        id="mainstream_radio",
        name="Mainstream Radio Listener",
        age=35,
        description="Listens in car, Spotify Top 50. Wants strong chorus, clean production, "
                    "2:30-3:30 duration. Values familiarity and catchiness.",
        weights=PersonaWeights(
            hook=0.9,
            originality=0.4,
            production=0.85,
            emotion=0.7,
            radio_friendly=0.95
        ),
        priority_weight=2.0  # High weight for hit potential
    ),
    Persona(
        id="edm_clubber",
        name="Clubbing EDM/Techno Lover",
        age=25,
        description="Focused on energy, build-ups, drops, and danceability. "
                    "Wants strong kick, bass, and progression. Less concerned with lyrics.",
        weights=PersonaWeights(
            hook=0.7,
            originality=0.6,
            production=0.9,
            emotion=0.5,
            radio_friendly=0.4
        ),
        priority_weight=1.0
    ),
    Persona(
        id="hiphop_trap",
        name="Hip-hop/Trap Fan",
        age=22,
        description="Cares about flow, beat quality, bass weight, and lyrical punchlines. "
                    "Authenticity and credibility are important.",
        weights=PersonaWeights(
            hook=0.75,
            originality=0.7,
            production=0.85,
            emotion=0.6,
            radio_friendly=0.5
        ),
        priority_weight=1.5
    ),
    Persona(
        id="cinematic_lover",
        name="Film/Games Music Lover",
        age=30,
        description="Seeks atmosphere, cinematic quality, evolution, and sound design. "
                    "Appreciates instrumental complexity and emotional journey.",
        weights=PersonaWeights(
            hook=0.4,
            originality=0.8,
            production=0.95,
            emotion=0.9,
            radio_friendly=0.3
        ),
        priority_weight=0.8
    ),
    Persona(
        id="chill_casual",
        name="Casual Listener - Chill/Study",
        age=29,
        description="Background listening for work/study. Wants smooth, non-aggressive sound. "
                    "No jarring elements or sudden changes.",
        weights=PersonaWeights(
            hook=0.5,
            originality=0.5,
            production=0.75,
            emotion=0.6,
            radio_friendly=0.6
        ),
        priority_weight=1.0
    ),
    Persona(
        id="latin_world",
        name="Latin/World Music Enthusiast",
        age=27,
        description="Loves rhythm, groove, sensuality, and danceable beats. "
                    "Appreciates cultural authenticity and infectious energy.",
        weights=PersonaWeights(
            hook=0.8,
            originality=0.7,
            production=0.7,
            emotion=0.8,
            radio_friendly=0.6
        ),
        priority_weight=1.2
    ),
    Persona(
        id="audiophile",
        name="Audiophile/Sound Engineer",
        age=40,
        description="Critically analyzes mix quality, stereo image, dynamics, and mastering. "
                    "Detects technical flaws easily. Values production excellence.",
        weights=PersonaWeights(
            hook=0.5,
            originality=0.6,
            production=0.98,
            emotion=0.7,
            radio_friendly=0.5
        ),
        priority_weight=1.0
    ),
    Persona(
        id="anr_executive",
        name="Music Business A&R",
        age=35,
        description="Evaluates commercial viability, playlist potential, and market fit. "
                    "Considers current trends and monetization potential.",
        weights=PersonaWeights(
            hook=0.85,
            originality=0.65,
            production=0.85,
            emotion=0.75,
            radio_friendly=0.9
        ),
        priority_weight=2.5  # Highest weight for hit potential
    ),
]


def get_persona_by_id(persona_id: str) -> Persona:
    """Get a persona by its ID."""
    for persona in PERSONAS:
        if persona.id == persona_id:
            return persona
    raise ValueError(f"Persona with ID '{persona_id}' not found")


def get_all_personas() -> List[Persona]:
    """Get all personas."""
    return PERSONAS


def calculate_weighted_persona_score(persona_ratings: Dict[str, float]) -> float:
    """
    Calculate weighted average of persona ratings for hit potential.

    Args:
        persona_ratings: Dict mapping persona_id to rating (0-100)

    Returns:
        Weighted score (0-100)
    """
    total_weight = sum(p.priority_weight for p in PERSONAS)
    weighted_sum = sum(
        persona_ratings.get(p.id, 0) * p.priority_weight
        for p in PERSONAS
    )
    return weighted_sum / total_weight if total_weight > 0 else 0
