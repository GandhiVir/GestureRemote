"""Runs Artemis CLI instructions in the background so the gesture loop never blocks."""

import subprocess
import threading

import config


def dispatch(instruction: str) -> None:
    """Fire a natural-language instruction at Artemis on a background thread."""
    threading.Thread(target=_run, args=(instruction,), daemon=True).start()


def _run(instruction: str) -> None:
    print(f"[artemis] running: {instruction!r}")
    try:
        result = subprocess.run(
            ["uv", "run", "artemis", "run", instruction, "--profile", config.ARTEMIS_PROFILE],
            cwd=config.ARTEMIS_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = (result.stdout or result.stderr).strip()
        print(f"[artemis] done (exit {result.returncode}): {output[-500:]}")
    except FileNotFoundError:
        print("[artemis] error: 'uv' not found. Is Artemis installed and on PATH?")
    except subprocess.TimeoutExpired:
        print("[artemis] error: instruction timed out after 120s")
    except Exception as exc:
        print(f"[artemis] error: {exc}")
