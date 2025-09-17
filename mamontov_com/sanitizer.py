from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional


class MessageSanitizer:
    """Runs the C++ sanitizer binary to clean message content."""

    def __init__(self) -> None:
        self._binary_path = self._ensure_compiled()

    @staticmethod
    def _source_path() -> Path:
        return Path(__file__).resolve().parent.parent / "cpp" / "message_sanitizer.cpp"

    @staticmethod
    def _binary_dir() -> Path:
        return Path(__file__).resolve().parent.parent / "cpp" / "build"

    def _ensure_compiled(self) -> Optional[Path]:
        binary_dir = self._binary_dir()
        binary_dir.mkdir(parents=True, exist_ok=True)
        binary_name = "message_sanitizer.exe" if os.name == "nt" else "message_sanitizer"
        binary_path = binary_dir / binary_name

        if binary_path.exists():
            return binary_path

        source_path = self._source_path()
        compile_cmd = [
            "g++",
            "-std=c++17",
            "-O2",
            str(source_path),
            "-o",
            str(binary_path),
        ]

        try:
            subprocess.run(compile_cmd, check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            return None

        return binary_path if binary_path.exists() else None

    def sanitize(self, message: str) -> str:
        if not message:
            return ""

        if not self._binary_path:
            return self._python_sanitize(message)

        try:
            completed = subprocess.run(
                [str(self._binary_path)],
                input=message.encode("utf-8"),
                check=True,
                capture_output=True,
            )
            output = completed.stdout.decode("utf-8", errors="ignore")
            return output.strip()
        except subprocess.SubprocessError:
            return self._python_sanitize(message)

    @staticmethod
    def _python_sanitize(message: str) -> str:
        sanitized = message.replace("\r", " ").replace("\n", " ")
        sanitized = " ".join(sanitized.split())
        return sanitized[:500]


sanitizer = MessageSanitizer()


def sanitize_message(message: str) -> str:
    return sanitizer.sanitize(message)
