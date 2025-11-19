"""
Generate synthetic training data for persona fine-tuning.

Uses GPT-4 to create diverse track profiles and corresponding
persona evaluations for training a local LLM.
"""

import json
import random
import argparse
from pathlib import Path
from typing import List, Dict
import asyncio
from openai import AsyncOpenAI
from tqdm import tqdm
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))
from app.models.personas import PERSONAS


class SyntheticDataGenerator:
    """Generates synthetic training data for persona model."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.personas = PERSONAS

    async def generate_track_profile(self) -> Dict:
        """Generate a random but realistic track profile."""

        genres = [
            "Pop", "EDM", "Hip-hop", "Trap", "Indie", "Alternative", "Rock",
            "Electronic", "House", "Techno", "R&B", "Soul", "Ballad",
            "Latin", "Reggaeton", "Afrobeat", "K-Pop", "Lo-fi", "Ambient"
        ]

        moods = [
            "Energetic & Bright", "Dark & Atmospheric", "Uplifting",
            "Melancholic", "Calm & Peaceful", "Aggressive", "Romantic",
            "Nostalgic", "Euphoric", "Mysterious", "Playful", "Intense"
        ]

        energies = ["low", "medium", "high"]
        structures = [
            "Short intro, Standard format",
            "Long intro, Extended format",
            "No intro, Straight to hook",
            "Medium intro, Standard format"
        ]

        return {
            "genre": random.choice(genres),
            "tempo": random.randint(60, 180),
            "mood": random.choice(moods),
            "energy": random.choice(energies),
            "duration": random.randint(120, 300),
            "quality_score": random.randint(40, 95),
            "loudness_lufs": round(random.uniform(-18, -8), 1),
            "dynamic_range": round(random.uniform(0.03, 0.15), 2),
            "structure": random.choice(structures),
            "clarity_score": round(random.uniform(0.5, 0.95), 2),
            "hook_strength": random.randint(30, 95),
            "originality": random.randint(30, 95)
        }

    async def generate_persona_response(
        self,
        track_profile: Dict,
        persona
    ) -> Dict:
        """Generate a persona's response to a track using GPT-4."""

        prompt = f"""You are {persona.name}, age {persona.age}.

Your profile: {persona.description}

You're evaluating a music track with these characteristics:

TRACK DETAILS:
- Genre: {track_profile['genre']}
- Tempo: {track_profile['tempo']} BPM
- Mood: {track_profile['mood']}
- Energy: {track_profile['energy']}
- Duration: {track_profile['duration']} seconds ({track_profile['duration']//60}:{track_profile['duration']%60:02d})
- Structure: {track_profile['structure']}
- Audio Quality Score: {track_profile['quality_score']}/100
- Loudness: {track_profile['loudness_lufs']} LUFS
- Clarity: {int(track_profile['clarity_score'] * 100)}%

Based on your persona, provide an evaluation in this EXACT JSON format:
{{
  "rating": <number 0-100>,
  "playlist_likelihood": <number 0-100>,
  "comment": "<your authentic 1-2 sentence reaction>"
}}

Be true to your persona. Don't be generic - show your specific perspective and preferences.
For example:
- If you're the TikTok teen, focus on virality and hooks
- If you're the audiophile, critique technical quality
- If you're the A&R, think commercial potential

IMPORTANT: Return ONLY the JSON, nothing else."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a music evaluation persona. Always respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher for diversity
                max_tokens=150
            )

            content = response.choices[0].message.content.strip()

            # Clean JSON extraction
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            evaluation = json.loads(content)

            return {
                "rating": float(evaluation["rating"]),
                "playlist_likelihood": float(evaluation["playlist_likelihood"]),
                "comment": evaluation["comment"]
            }

        except Exception as e:
            print(f"Error generating response for {persona.name}: {e}")
            # Fallback to random but valid response
            return {
                "rating": random.randint(40, 85),
                "playlist_likelihood": random.randint(30, 80),
                "comment": f"[Fallback] This track is interesting from my perspective."
            }

    async def generate_training_example(self) -> Dict:
        """Generate one complete training example (track + 10 persona responses)."""

        track_profile = await self.generate_track_profile()

        # Generate responses for all 10 personas
        tasks = [
            self.generate_persona_response(track_profile, persona)
            for persona in self.personas
        ]

        persona_responses = await asyncio.gather(*tasks)

        # Create training examples for each persona
        examples = []
        for persona, response in zip(self.personas, persona_responses):
            examples.append({
                "track_profile": track_profile,
                "persona_id": persona.id,
                "persona_name": persona.name,
                "persona_age": persona.age,
                "persona_description": persona.description,
                "response": response
            })

        return examples

    def format_for_training(self, example: Dict) -> Dict:
        """Format example for instruction tuning."""

        track = example["track_profile"]
        persona_id = example["persona_id"]
        persona_name = example["persona_name"]
        persona_age = example["persona_age"]
        persona_desc = example["persona_description"]
        response = example["response"]

        instruction = f"""You are {persona_name}, age {persona_age}.

Your profile: {persona_desc}

Analyze this track and provide your evaluation:

Track Characteristics:
- Genre: {track['genre']}
- Tempo: {track['tempo']} BPM
- Mood: {track['mood']}
- Energy: {track['energy']}
- Duration: {track['duration']} seconds
- Structure: {track['structure']}
- Quality Score: {track['quality_score']}/100
- Loudness: {track['loudness_lufs']} LUFS
- Clarity: {int(track['clarity_score'] * 100)}%

Respond with JSON: {{"rating": 0-100, "playlist_likelihood": 0-100, "comment": "your reaction"}}"""

        output = json.dumps(response)

        return {
            "instruction": instruction,
            "output": output,
            "persona_id": persona_id,
            "metadata": {
                "genre": track["genre"],
                "tempo": track["tempo"],
                "mood": track["mood"]
            }
        }

    async def generate_dataset(
        self,
        num_examples: int,
        output_dir: Path
    ):
        """Generate complete dataset and save to files."""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        all_examples = []

        print(f"Generating {num_examples} training examples...")
        print(f"This will create {num_examples * 10} persona-specific examples.")
        print(f"Estimated cost: ${num_examples * 0.06:.2f}\n")

        # Generate examples with progress bar
        for i in tqdm(range(num_examples)):
            try:
                examples = await self.generate_training_example()
                all_examples.extend(examples)

                # Save checkpoint every 100 examples
                if (i + 1) % 100 == 0:
                    checkpoint_file = output_dir / f"checkpoint_{i+1}.jsonl"
                    self._save_examples(all_examples, checkpoint_file)

            except Exception as e:
                print(f"\nError at example {i}: {e}")
                continue

        # Shuffle and split into train/val/test
        random.shuffle(all_examples)

        total = len(all_examples)
        train_size = int(total * 0.8)
        val_size = int(total * 0.1)

        train_data = all_examples[:train_size]
        val_data = all_examples[train_size:train_size + val_size]
        test_data = all_examples[train_size + val_size:]

        # Format for training
        train_formatted = [self.format_for_training(ex) for ex in train_data]
        val_formatted = [self.format_for_training(ex) for ex in val_data]
        test_formatted = [self.format_for_training(ex) for ex in test_data]

        # Save datasets
        self._save_examples(train_formatted, output_dir / "train.jsonl")
        self._save_examples(val_formatted, output_dir / "val.jsonl")
        self._save_examples(test_formatted, output_dir / "test.jsonl")

        print(f"\n✅ Dataset generated successfully!")
        print(f"Train: {len(train_formatted)} examples")
        print(f"Val: {len(val_formatted)} examples")
        print(f"Test: {len(test_formatted)} examples")
        print(f"Saved to: {output_dir}")

    def _save_examples(self, examples: List[Dict], filepath: Path):
        """Save examples to JSONL file."""
        with open(filepath, 'w') as f:
            for example in examples:
                f.write(json.dumps(example) + '\n')


async def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic training data for persona model"
    )
    parser.add_argument(
        "--num-examples",
        type=int,
        default=500,
        help="Number of track profiles to generate (each creates 10 persona responses)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="../data",
        help="Output directory for datasets"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key required. Set OPENAI_API_KEY or use --api-key")
        return

    # Generate data
    generator = SyntheticDataGenerator(api_key=api_key)
    await generator.generate_dataset(
        num_examples=args.num_examples,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    import os
    asyncio.run(main())
