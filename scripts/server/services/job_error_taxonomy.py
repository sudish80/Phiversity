"""Stable job error/exit taxonomy and root-cause hint helpers."""

from __future__ import annotations

from dataclasses import dataclass


# Stable stage-level exit/error codes.
JOB_EXIT_SUCCESS = 0
JOB_EXIT_WORKFLOW_ERROR = 1
JOB_EXIT_VALIDATION_ERROR = 2
JOB_EXIT_ARTIFACT_ERROR = 3
JOB_EXIT_TIMEOUT = 124


STAGE_VALIDATION = "validation"
STAGE_QUEUE = "queue"
STAGE_ORCHESTRATION = "orchestration"
STAGE_PIPELINE = "pipeline"
STAGE_ARTIFACT = "artifact"
STAGE_WORKFLOW = "workflow"


DEFAULT_STAGE_HINTS = {
    STAGE_VALIDATION: "Verify request payload JSON and required fields before queueing.",
    STAGE_QUEUE: "Increase MAX_CONCURRENT_JOBS or reduce active queue load.",
    STAGE_ORCHESTRATION: "Review orchestrator output and model/provider configuration.",
    STAGE_PIPELINE: "Inspect pipeline output for the first rendering/toolchain error.",
    STAGE_ARTIFACT: "Check output paths and ensure final artifact files are produced.",
    STAGE_WORKFLOW: "Review stack trace and command output around the reported worker error.",
}


@dataclass(frozen=True)
class HintPattern:
    needle: str
    hint: str


ROOT_CAUSE_HINT_PATTERNS: list[HintPattern] = [
    HintPattern("ffmpeg", "FFmpeg appears missing or misconfigured. Verify ffmpeg is installed and on PATH."),
    HintPattern("moviepy", "MoviePy failed. Verify codecs and ffmpeg runtime dependencies."),
    HintPattern("401", "Authentication failure detected. Verify API keys/tokens for the provider."),
    HintPattern("403", "Authorization failure detected. Verify account/project permissions."),
    HintPattern("quota", "Quota/rate-limit issue detected. Check provider quotas and retry with backoff."),
    HintPattern("rate limit", "Rate-limit issue detected. Retry with backoff and check request volume."),
    HintPattern("disk", "Disk/storage issue detected. Check free space and writable directories."),
    HintPattern("no space left", "Disk full. Free disk space and retry."),
    HintPattern("connection refused", "Network/service connection failed. Check service endpoints and network access."),
    HintPattern("timed out", "Timeout detected. Increase JOB_TIMEOUT or reduce workload complexity."),
]


def infer_root_cause_hint(stage: str, output_text: str | None, exit_code: int) -> str:
    text = (output_text or "").lower()
    for pattern in ROOT_CAUSE_HINT_PATTERNS:
        if pattern.needle in text:
            return pattern.hint

    if exit_code == JOB_EXIT_TIMEOUT:
        return "Timeout detected. Increase JOB_TIMEOUT or reduce workload complexity."

    return DEFAULT_STAGE_HINTS.get(stage, DEFAULT_STAGE_HINTS[STAGE_WORKFLOW])
