#!/usr/bin/python3
"""Run the normal Codex OAuth login with bounded runtime and status logging."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import subprocess
import sys


def main():
    log = logging.getLogger("rovo-auth-refresh")
    log.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        Path(__file__).resolve().parent / "refresh.log",
        maxBytes=262144,
        backupCount=1,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(handler)
    log.info("Starting Rovo login; complete browser sign-in if prompted.")
    try:
        result = subprocess.run(
            [sys.argv[1], "mcp", "login", "atlassian-rovo"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=600,
            check=False,
        )
    except subprocess.TimeoutExpired:
        log.error("Login timed out after 10 minutes. Will try at the next scheduled time.")
        return 1
    except OSError as error:
        log.error("Could not start Codex: %s", error)
        return 1
    if result.returncode:
        log.error(
            "Login failed (exit %s). Run 'codex mcp login atlassian-rovo' "
            "in a terminal to see the error.",
            result.returncode,
        )
        return 1
    log.info("Rovo login completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
