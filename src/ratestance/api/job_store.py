"""In-memory job store for tracking refresh operations.

This module provides a simple in-memory storage for job status tracking.
For production use, consider Redis or a database for persistence.
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from loguru import logger


class JobStore:
    """In-memory store for job status tracking.

    This is a simple implementation suitable for single-instance deployments.
    For production use with multiple workers, use Redis or a database.

    Attributes:
        _jobs: Dictionary mapping job_id to job status data
    """

    def __init__(self) -> None:
        """Initialize an empty job store."""
        self._jobs: dict[UUID, dict[str, Any]] = {}

    def create_job(self) -> UUID:
        """Create a new job entry and return its ID.

        Returns:
            Unique identifier for the new job
        """
        job_id = uuid4()
        now = datetime.utcnow().isoformat()

        self._jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "stage": "initializing",
            "message": "Job created, waiting to start...",
            "created_at": now,
            "updated_at": now,
        }

        logger.info(f"Created job {job_id}")
        return job_id

    def update_job(
        self,
        job_id: UUID,
        status: str | None = None,
        progress: int | None = None,
        stage: str | None = None,
        message: str | None = None,
    ) -> bool:
        """Update job status fields.

        Args:
            job_id: Job identifier to update
            status: New status value (pending|running|completed|error)
            progress: Progress percentage (0-100)
            stage: Current pipeline stage name
            message: Status message

        Returns:
            True if job was found and updated, False otherwise
        """
        if job_id not in self._jobs:
            logger.warning(f"Job {job_id} not found for update")
            return False

        job = self._jobs[job_id]

        if status is not None:
            job["status"] = status
        if progress is not None:
            job["progress"] = max(0, min(100, progress))
        if stage is not None:
            job["stage"] = stage
        if message is not None:
            job["message"] = message

        job["updated_at"] = datetime.utcnow().isoformat()

        logger.debug(f"Updated job {job_id}: {job['status']} - {job['progress']}%")
        return True

    def get_job(self, job_id: UUID) -> dict[str, Any] | None:
        """Get job status by ID.

        Args:
            job_id: Job identifier to retrieve

        Returns:
            Job status dict if found, None otherwise
        """
        return self._jobs.get(job_id)

    def list_jobs(self) -> list[dict[str, Any]]:
        """Get all jobs, sorted by creation time (newest first).

        Returns:
            List of job status dicts
        """
        jobs = list(self._jobs.values())
        jobs.sort(key=lambda j: j["created_at"], reverse=True)
        return jobs

    def delete_job(self, job_id: UUID) -> bool:
        """Delete a job from the store.

        Args:
            job_id: Job identifier to delete

        Returns:
            True if job was found and deleted, False otherwise
        """
        if job_id in self._jobs:
            del self._jobs[job_id]
            logger.info(f"Deleted job {job_id}")
            return True
        return False


# Global singleton instance
job_store = JobStore()
