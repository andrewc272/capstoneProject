#!/usr/bin/env python
"""
Bootstrap helper for local AI agents.

This script attempts to install Ollama (when missing) and pull every model used
by presets that rely on local inference. After it completes successfully, you
can launch Flask (`flask run`) and pick the "Local AI agents" option in the UI.
"""

from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, Set

REPO_ROOT = Path(__file__).resolve().parents[1]
BOT_PROFILES_PATH = REPO_ROOT / "bot_profiles.py"

EXTRA_MODEL_COMMANDS = [
    ["ollama", "pull", "llama3.1:8b"],
    ["ollama", "pull", "llama3.1"],
    ["ollama", "pull", "llama3.2"],
]


def _load_presets() -> Dict[str, dict]:
    spec = importlib.util.spec_from_file_location("bot_profiles", BOT_PROFILES_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to locate bot_profiles.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return getattr(module, "LOCAL_BOT_PRESETS", {})


def _run(command: Iterable[str], *, check: bool = True):
    print(f"[setup] Running: {' '.join(command)}")
    return subprocess.run(command, check=check)


def ensure_ollama_installed() -> bool:
    if shutil.which("ollama"):
        print("[setup] Ollama already available.")
        return True

    system = platform.system().lower()
    try:
        if system == "windows":
            if not shutil.which("winget"):
                print("[setup] winget is required to install Ollama on Windows. "
                      "Please install Ollama manually from https://ollama.com/download/windows.")
                return False
            _run(["winget", "install", "-e", "--id", "Ollama.Ollama"])
        elif system in {"darwin", "linux"}:
            shell_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
            _run(["/bin/sh", "-c", shell_cmd])
        else:
            print(f"[setup] Unsupported OS ({system}). Install Ollama manually.")
            return False
    except subprocess.CalledProcessError as exc:
        print(f"[setup] Failed to install Ollama: {exc}")
        return False

    if shutil.which("ollama"):
        print("[setup] Ollama installed successfully.")
        return True
    print("[setup] Ollama still not detected. Please verify installation.")
    return False


def pull_models(models: Set[str]) -> Set[str]:
    failures: Set[str] = set()
    for model in sorted(models):
        try:
            _run(["ollama", "pull", model])
        except subprocess.CalledProcessError as exc:
            print(f"[setup] Failed to pull {model}: {exc}")
            failures.add(model)
    return failures


def run_extra_pulls():
    print("[setup] Running supplementary Ollama pulls for common llama variants...")
    for command in EXTRA_MODEL_COMMANDS:
        try:
            _run(command, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"[setup] Optional pull failed ({' '.join(command)}): {exc}")


def main():
    presets = _load_presets()
    ollama_models = {
        preset["model"]
        for preset in presets.values()
        if preset.get("engine") == "ollama"
    }
    if not ollama_models:
        print("[setup] No Ollama-based presets detected. Nothing to install.")
        return

    print("[setup] Preparing to install Ollama and pull models:")
    for model in sorted(ollama_models):
        print(f"    - {model}")

    if not ensure_ollama_installed():
        sys.exit(1)

    run_extra_pulls()
    failures = pull_models(ollama_models)
    if failures:
        print(
            "[setup] Some models could not be pulled automatically.\n"
            "Try installing them manually with `ollama pull <model>` or adjust `bot_profiles.py` "
            "to reference a model that exists in your local ollama catalog."
        )
        print("Missing models:", ", ".join(sorted(failures)))
        sys.exit(1)

    print("[setup] All models pulled. You can now run `flask run` and select Local AI agents.")


if __name__ == "__main__":
    main()
