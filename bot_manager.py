import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Dict, List


class LocalBotManager:
    """Manages the lifecycle of locally hosted bot processes."""

    def __init__(self, base_dir: Path, disabled: bool = False):
        self._base_dir = Path(base_dir)
        self._disabled = disabled
        self._lock = threading.Lock()
        self._processes: List[subprocess.Popen] = []
        self._profile_id: str | None = None
        self._desired_count: int = 0
        self._server_url: str | None = None

    def ensure_state(self, profile_id: str, count: int, server_url: str):
        """Start bots that match the desired profile/count and stop old ones."""
        count = max(0, int(count))
        with self._lock:
            self._desired_count = count
            self._profile_id = profile_id
            self._server_url = server_url
            if self._disabled or count == 0 or not profile_id:
                self._stop_locked()
                return

            alive = [p for p in self._processes if p.poll() is None]
            if len(alive) == count and alive:
                self._processes = alive
                return

            self._stop_locked()
            self._start_locked(profile_id, count, server_url)

    def stop(self):
        with self._lock:
            self._stop_locked()

    def status(self) -> Dict[str, object]:
        with self._lock:
            alive = [p for p in self._processes if p.poll() is None]
            self._processes = alive
            return {
                "running": len(alive),
                "profile": self._profile_id,
                "desired": self._desired_count,
                "server": self._server_url,
            }

    def _start_locked(self, profile_id: str, count: int, server_url: str):
        script = self._base_dir / "Bot" / "local_agent.py"
        if not script.exists():
            return

        python_exec = sys.executable
        env_template = os.environ.copy()

        for index in range(count):
            env = env_template.copy()
            env["LOCAL_AGENT_PROFILE"] = profile_id
            env["LOCAL_AGENT_NAME"] = f"LocalBot-{index + 1}"
            env["CAPSTONE_SERVER_URL"] = server_url
            env["LOCAL_AGENT_POSITION"] = str(index + 1)
            command = [python_exec, str(script)]
            try:
                proc = subprocess.Popen(command, cwd=self._base_dir, env=env)
                self._processes.append(proc)
            except Exception:
                # If spawning fails we ensure nothing stale stays around.
                self._stop_locked()
                break

    def _stop_locked(self):
        for proc in self._processes:
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                except Exception:
                    proc.kill()
        self._processes = []
