from __future__ import annotations

import abc
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ResourceLimits(BaseModel):
    max_memory_mb: int = Field(512, ge=64, le=4096, description="Memory limit in megabytes")
    cpu_quota: float = Field(0.5, ge=0.1, le=4.0, description="CPU cores limit")
    max_execution_time_seconds: int = Field(15, ge=1, le=120, description="Max command duration")
    allow_network: bool = Field(False, description="Whether container has outbound network access")
    max_processes: int = Field(64, ge=16, le=256, description="Max fork/process limit")


class ContainerInfo(BaseModel):
    container_id: str
    session_id: str
    status: str
    image: str
    created_at: str
    resource_limits: ResourceLimits


class ExecutionResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False


class BaseExecutionEngine(abc.ABC):
    """
    Abstract interface for isolated execution runtimes (Docker, gVisor, Firecracker).
    Candidate code is NEVER executed inside the main FastAPI process.
    """

    @abc.abstractmethod
    def provision_container(
        self,
        session_id: str,
        image: str = "python:3.11-slim",
        limits: Optional[ResourceLimits] = None,
    ) -> ContainerInfo:
        """Spins up a lightweight isolated container with strict resource limits."""
        pass

    @abc.abstractmethod
    def execute_command(
        self,
        container_id: str,
        command: str,
        timeout_seconds: Optional[int] = None,
    ) -> ExecutionResult:
        """Executes a command inside the container with time and privilege boundaries."""
        pass

    @abc.abstractmethod
    def cleanup_container(self, container_id: str) -> bool:
        """Stops and forcefully removes the container and its transient mounts."""
        pass
