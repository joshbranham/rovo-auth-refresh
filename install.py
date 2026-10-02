#!/usr/bin/python3
"""Install a user LaunchAgent. Run --dry-run to inspect its plist first."""

import argparse
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys


LABEL = "com.jbranham.rovo-auth-refresh"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schedule", choices=("weekdays", "daily", "8hours"), default="weekdays",
        help="weekdays/daily at 09:00, or daily at 08:00/16:00/00:00 (local time)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    codex = shutil.which("codex")
    if not codex:
        parser.error("codex is not on PATH")

    user_dir = Path.home()
    support = user_dir / "Library/Application Support/rovo-auth-refresh"
    agent = user_dir / "Library/LaunchAgents" / (LABEL + ".plist")
    schedules = {
        "weekdays": [{"Weekday": day, "Hour": 9, "Minute": 0} for day in range(1, 6)],
        "daily": {"Hour": 9, "Minute": 0},
        "8hours": [{"Hour": hour, "Minute": 0} for hour in (0, 8, 16)],
    }
    definition = {
        "Label": LABEL,
        "ProgramArguments": ["/usr/bin/python3", str(support / "refresh.py"), codex],
        "WorkingDirectory": str(user_dir),
        "LimitLoadToSessionType": "Aqua",
        "StartCalendarInterval": schedules[args.schedule],
        "RunAtLoad": False,
        "ProcessType": "Background",
        "Umask": 0o077,
        "EnvironmentVariables": {
            "PATH": str(Path(codex).parent) + ":/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        },
    }
    if os.environ.get("CODEX_HOME"):
        definition["EnvironmentVariables"]["CODEX_HOME"] = os.environ["CODEX_HOME"]
    plist = plistlib.dumps(definition)
    if args.dry_run:
        sys.stdout.buffer.write(plist)
        return

    os.umask(0o077)
    support.mkdir(parents=True, exist_ok=True)
    agent.parent.mkdir(parents=True, exist_ok=True)
    domain = "gui/" + str(os.getuid())
    service = domain + "/" + LABEL
    loaded = subprocess.run(
        ["/bin/launchctl", "print", service], capture_output=True,
    ).returncode == 0
    if loaded:
        subprocess.run(["/bin/launchctl", "bootout", service], check=True)
    shutil.copyfile(Path(__file__).with_name("refresh.py"), support / "refresh.py")
    agent.write_bytes(plist)
    subprocess.run(["/usr/bin/plutil", "-lint", str(agent)], check=True)
    subprocess.run(["/bin/launchctl", "enable", service], check=True)
    subprocess.run(["/bin/launchctl", "bootstrap", domain, str(agent)], check=True)
    print("Installed schedule: " + args.schedule + " (Mac's local time).")
    print("Login will run at the next scheduled time. Log: " + str(support / "refresh.log"))
    print("Run now: launchctl kickstart " + service)


if __name__ == "__main__":
    main()
