"""Models for data refresh API endpoints.

This module defines Pydantic models for job status tracking and responses.
"""

from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(BaseModel):
    """Job status model for tracking refresh operations.

    Attributes:
        job_id: Unique identifier for the job
        status: Current job status (pending, running, completed, error)
        progress: Progress percentage (0-100)
        stage: Current pipeline stage name
        message: Human-readable status message
        created_at: Job creation timestamp
        updated_at: Last update timestamp
    """

    job_id: UUID
    status: str = Field(..., pattern="^(pending|running|completed|error)$")
    progress: int = Field(..., ge=0, le=100)
    stage: str
    message: str
    created_at: str
    updated_at: str

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "running",
                "progress": 45,
                "stage": "aggregating",
                "message": "Aggregating news to daily level...",
                "created_at": "2025-01-27T10:00:00Z",
                "updated_at": "2025-01-27T10:05:00Z",
            }
        }


class JobListResponse(BaseModel):
    """Response model for listing all jobs.

    Attributes:
        jobs: List of job status objects
        total: Total number of jobs
    """

    jobs: list[JobStatus]
    total: int


class JobCreateResponse(BaseModel):
    """Response model for job creation.

    Attributes:
        job_id: Unique identifier for the created job
        status: Initial job status
        message: Confirmation message
    """

    job_id: UUID
    status: str
    message: str

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
                "message": "Data refresh job started successfully",
            }
        }
