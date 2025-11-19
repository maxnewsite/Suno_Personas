"""Analysis API routes."""
import os
import uuid
import time
import asyncio
from pathlib import Path
from typing import Dict
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.schemas import (
    UploadResponse,
    AnalysisResult,
    StatusResponse,
    ErrorResponse,
)
from app.services import AudioAnalyzer, PersonaEngine, Scorer
from app.config import settings

router = APIRouter(prefix="/api", tags=["analysis"])

# In-memory job storage (in production, use Redis or database)
jobs: Dict[str, Dict] = {}


async def process_audio_file(job_id: str, file_path: str):
    """
    Background task to process audio file.

    Args:
        job_id: Unique job identifier
        file_path: Path to uploaded file
    """
    try:
        start_time = time.time()

        # Update status
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 0.1

        # Initialize services
        audio_analyzer = AudioAnalyzer()
        persona_engine = PersonaEngine()
        scorer = Scorer()

        # Step 1: Analyze audio (30% progress)
        jobs[job_id]["progress"] = 0.3
        features, quality, characteristics = audio_analyzer.analyze_file(file_path)

        # Step 2: Get persona evaluations (70% progress)
        jobs[job_id]["progress"] = 0.7
        persona_evaluations = await persona_engine.evaluate_all_personas(
            features, quality, characteristics
        )

        # Step 3: Calculate scores (90% progress)
        jobs[job_id]["progress"] = 0.9

        # Artistic score
        artistic_score = persona_engine.calculate_artistic_score(
            persona_evaluations, features
        )

        # Hit potential
        hit_potential = scorer.calculate_hit_potential(
            persona_evaluations,
            quality.score,
            artistic_score
        )

        # Overall score
        overall_score = scorer.calculate_overall_score(
            quality.score,
            artistic_score,
            hit_potential
        )

        # Radar chart
        radar_data = scorer.create_radar_chart_data(
            persona_evaluations,
            quality,
            characteristics,
            features
        )

        # Score breakdown
        score_breakdown = scorer.create_score_breakdown(
            quality.score,
            artistic_score,
            hit_potential
        )

        # Generate suggestions
        suggestions = scorer.generate_suggestions(
            quality,
            features,
            persona_evaluations,
            radar_data
        )

        # Create result
        processing_time = time.time() - start_time

        result = AnalysisResult(
            job_id=job_id,
            overall_score=overall_score,
            scores=score_breakdown,
            radar_chart=radar_data,
            personas=persona_evaluations,
            audio_quality=quality,
            characteristics=characteristics,
            suggestions=suggestions,
            processing_time=processing_time
        )

        # Store result
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 1.0
        jobs[job_id]["result"] = result.model_dump()

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

    finally:
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass


@router.post("/upload", response_model=UploadResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload an MP3 file for analysis.

    Args:
        file: MP3 file to analyze

    Returns:
        Upload response with job ID
    """
    # Validate file type
    if not file.filename.endswith('.mp3'):
        raise HTTPException(
            status_code=400,
            detail="Only MP3 files are supported"
        )

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save file temporarily
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{job_id}.mp3"

    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

    # Initialize job
    jobs[job_id] = {
        "status": "queued",
        "progress": 0.0,
        "filename": file.filename
    }

    # Start background processing
    background_tasks.add_task(process_audio_file, job_id, str(file_path))

    return UploadResponse(
        job_id=job_id,
        status="processing",
        message="Your track is being analyzed. This usually takes 30-60 seconds."
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """
    Check the status of an analysis job.

    Args:
        job_id: Job identifier

    Returns:
        Status response
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job = jobs[job_id]

    return StatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress"),
        message=job.get("message"),
        error=job.get("error")
    )


@router.get("/analyze/{job_id}")
async def get_analysis(job_id: str):
    """
    Get analysis results for a completed job.

    Args:
        job_id: Job identifier

    Returns:
        Analysis results
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job = jobs[job_id]

    if job["status"] == "processing" or job["status"] == "queued":
        return JSONResponse(
            status_code=202,
            content={
                "status": "processing",
                "progress": job.get("progress", 0),
                "message": "Analysis in progress..."
            }
        )

    if job["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail=job.get("error", "Analysis failed")
        )

    if job["status"] == "completed":
        return job["result"]

    raise HTTPException(
        status_code=500,
        detail="Unknown job status"
    )


@router.delete("/analyze/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its results.

    Args:
        job_id: Job identifier

    Returns:
        Success message
    """
    if job_id in jobs:
        del jobs[job_id]

    return {"message": "Job deleted successfully"}
