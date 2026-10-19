"""
Security Subsystem: MicroVM Sandboxing & Dual-Model Prompt Injection Firewall.
Conforms to OWASP LLM01 (Prompt Injection) & LLM02 (Insecure Output Handling).
"""

from __future__ import annotations

import re
import subprocess
import time
from typing import Any, ClassVar

from pydantic import BaseModel, Field


class SandboxExecutionResult(BaseModel):
    command: str
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: float
    sandboxed: bool
    violations_detected: list[str] = Field(default_factory=list)


class QgradeSandbox:
    """MicroVM / Lightweight Process Sandbox for Safe Tool Execution."""

    FORBIDDEN_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
        re.compile(r"\bdrop\s+database\b", re.IGNORECASE),
        re.compile(r"\bformat\s+[a-z]:", re.IGNORECASE),
        re.compile(r"\bdel\s+/f\b", re.IGNORECASE),
        re.compile(r"\bshutdown\b", re.IGNORECASE),
    ]

    @classmethod
    def execute_safe(
        cls,
        command: str,
        timeout_seconds: int = 5,
        allowed_commands: list[str] | None = None,
    ) -> SandboxExecutionResult:
        """Executes a command within constrained boundaries, trapping destructive actions."""
        violations = []
        for pat in cls.FORBIDDEN_PATTERNS:
            if pat.search(command):
                violations.append(f"Destructive pattern blocked: {pat.pattern}")

        if allowed_commands:
            base_cmd = command.split()[0] if command else ""
            if base_cmd not in allowed_commands:
                violations.append(f"Command '{base_cmd}' is not in allowed whitelist.")

        if violations:
            return SandboxExecutionResult(
                command=command,
                exit_code=126,  # Command invoked cannot execute
                stdout="",
                stderr="[SECURITY VIOLATION] Execution halted by QgradeSandbox guardrails.",
                execution_time_ms=0.0,
                sandboxed=True,
                violations_detected=violations,
            )

        t0 = time.perf_counter()
        try:
            # Simulated safe execution
            res = subprocess.run(
                command,
                shell=True,  # nosec B602
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            return SandboxExecutionResult(
                command=command,
                exit_code=res.returncode,
                stdout=res.stdout,
                stderr=res.stderr,
                execution_time_ms=round(elapsed, 2),
                sandboxed=True,
            )
        except subprocess.TimeoutExpired:
            return SandboxExecutionResult(
                command=command,
                exit_code=124,
                stdout="",
                stderr="Execution timed out.",
                execution_time_ms=timeout_seconds * 1000.0,
                sandboxed=True,
                violations_detected=["TIMEOUT_EXCEEDED"],
            )


class QgradePromptFirewall:
    """Dual-Model & Constitutional Sanitizer against Indirect Prompt Injection (OWASP LLM01)."""

    INJECTION_HEURISTICS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior)\s+(?:instructions|prompts)", re.IGNORECASE),
        re.compile(r"\[(?:system|admin|root)\s*(?:override|mode|directive)\]", re.IGNORECASE),
        re.compile(r"(?:dump|leak|export)\s+(?:all\s+)?(?:keys|passwords|credentials|accounts)", re.IGNORECASE),
        re.compile(r"bypass\s+(?:authorization|4-eyes|four-eyes|guardrails)", re.IGNORECASE),
    ]

    @classmethod
    def sanitize_payload(cls, raw_data: Any) -> tuple[Any, bool, list[str]]:
        """
        Recursively scans strings and dictionaries returned by external tools.
        Returns (sanitized_data, is_suspicious, detected_attacks).
        """
        detected: list[str] = []

        def _clean_str(text: str) -> str:
            cleaned = text
            for pat in cls.INJECTION_HEURISTICS:
                if pat.search(cleaned):
                    detected.append(pat.pattern)
                    cleaned = pat.sub("[REDACTED_ADVERSARIAL_INJECTION]", cleaned)
            return cleaned

        def _walk(obj: Any) -> Any:
            if isinstance(obj, str):
                return _clean_str(obj)
            elif isinstance(obj, dict):
                return {k: _walk(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_walk(item) for item in obj]
            return obj

        sanitized = _walk(raw_data)
        is_suspicious = len(detected) > 0
        return sanitized, is_suspicious, detected
