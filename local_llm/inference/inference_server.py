"""
Fast inference server for fine-tuned persona model using vLLM.

Provides REST API for persona-based music evaluation.
"""

import json
import argparse
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vllm import LLM, SamplingParams
import uvicorn


class TrackProfile(BaseModel):
    """Track characteristics for evaluation."""
    genre: str
    tempo: float
    mood: str
    energy: str
    duration: float
    quality_score: float
    loudness_lufs: float
    structure: str
    clarity_score: float


class PersonaRequest(BaseModel):
    """Request for persona evaluation."""
    persona_id: str
    persona_name: str
    persona_age: int
    persona_description: str
    track_profile: TrackProfile


class PersonaResponse(BaseModel):
    """Persona evaluation response."""
    rating: float
    playlist_likelihood: float
    comment: str


class InferenceServer:
    """vLLM-based inference server for persona model."""

    def __init__(self, model_path: str, tensor_parallel_size: int = 1):
        """Initialize model and server."""
        print(f"🔧 Loading model from {model_path}...")

        self.llm = LLM(
            model=model_path,
            tensor_parallel_size=tensor_parallel_size,
            dtype="half",  # FP16 for speed
            max_model_len=1024,
            gpu_memory_utilization=0.9,
        )

        self.sampling_params = SamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=200,
            stop=["<|eot_id|>"]
        )

        print("✅ Model loaded successfully!")

    def format_prompt(self, request: PersonaRequest) -> str:
        """Format request into model prompt."""
        track = request.track_profile

        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a music evaluation persona. Analyze tracks and respond with JSON only.<|eot_id|><|start_header_id|>user<|end_header_id|>

You are {request.persona_name}, age {request.persona_age}.

Your profile: {request.persona_description}

Analyze this track and provide your evaluation:

Track Characteristics:
- Genre: {track.genre}
- Tempo: {track.tempo} BPM
- Mood: {track.mood}
- Energy: {track.energy}
- Duration: {track.duration} seconds
- Structure: {track.structure}
- Quality Score: {track.quality_score}/100
- Loudness: {track.loudness_lufs} LUFS
- Clarity: {int(track.clarity_score * 100)}%

Respond with JSON: {{"rating": 0-100, "playlist_likelihood": 0-100, "comment": "your reaction"}}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    def parse_response(self, text: str) -> PersonaResponse:
        """Parse model output into structured response."""
        try:
            # Extract JSON from response
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            # Clean whitespace
            text = text.strip()

            # Parse JSON
            data = json.loads(text)

            return PersonaResponse(
                rating=float(data["rating"]),
                playlist_likelihood=float(data["playlist_likelihood"]),
                comment=str(data["comment"])
            )

        except Exception as e:
            print(f"⚠️  Parse error: {e}")
            print(f"Raw output: {text}")
            # Fallback response
            return PersonaResponse(
                rating=50.0,
                playlist_likelihood=50.0,
                comment="Unable to generate evaluation"
            )

    def evaluate(self, request: PersonaRequest) -> PersonaResponse:
        """Evaluate a single persona."""
        prompt = self.format_prompt(request)
        outputs = self.llm.generate([prompt], self.sampling_params)
        response_text = outputs[0].outputs[0].text
        return self.parse_response(response_text)

    def evaluate_batch(self, requests: List[PersonaRequest]) -> List[PersonaResponse]:
        """Evaluate multiple personas in batch (faster)."""
        prompts = [self.format_prompt(req) for req in requests]
        outputs = self.llm.generate(prompts, self.sampling_params)
        responses = [
            self.parse_response(output.outputs[0].text)
            for output in outputs
        ]
        return responses


# FastAPI app
app = FastAPI(title="Song Score LLM Inference API")
server = None


@app.on_event("startup")
async def startup():
    """Initialize server on startup."""
    global server
    model_path = app.state.model_path
    tensor_parallel = app.state.tensor_parallel_size
    server = InferenceServer(model_path, tensor_parallel)


@app.post("/evaluate", response_model=PersonaResponse)
async def evaluate_single(request: PersonaRequest):
    """Evaluate single persona."""
    try:
        return server.evaluate(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate_batch", response_model=List[PersonaResponse])
async def evaluate_batch(requests: List[PersonaRequest]):
    """Evaluate multiple personas in batch."""
    try:
        return server.evaluate_batch(requests)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "ready"}


@app.get("/metrics")
async def metrics():
    """Model performance metrics."""
    # TODO: Implement metrics tracking
    return {
        "total_requests": 0,
        "average_latency": 0.0,
        "error_rate": 0.0
    }


def main():
    parser = argparse.ArgumentParser(description="Start inference server")
    parser.add_argument(
        "--model-path",
        type=str,
        required=True,
        help="Path to fine-tuned model"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Server port"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server host"
    )
    parser.add_argument(
        "--tensor-parallel-size",
        type=int,
        default=1,
        help="Number of GPUs for tensor parallelism"
    )

    args = parser.parse_args()

    # Store config in app state
    app.state.model_path = args.model_path
    app.state.tensor_parallel_size = args.tensor_parallel_size

    print(f"\n🚀 Starting inference server on {args.host}:{args.port}")
    print(f"📁 Model: {args.model_path}\n")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
