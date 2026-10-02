# Periodic Rovo login

This macOS user LaunchAgent runs `codex mcp login atlassian-rovo` using your
existing Codex configuration and credential storage. It may open your browser
and require Atlassian sign-in or consent. It schedules login attempts; it cannot
guarantee unattended authentication or that credentials never expire.

Install from the repository directory in a normal terminal (no sudo):

```sh
rtk proxy /usr/bin/python3 ./install.py
```

The default is Monday–Friday at 09:00 in your Mac's local timezone. Alternatively,
append `--schedule daily` (09:00 every day) or `--schedule 8hours`
(00:00, 08:00, 16:00 every day). Append `--dry-run` to print the LaunchAgent
definition without installing anything. Re-running the installer replaces this
job's schedule and stops any login attempt currently started by this job.

The agent loads when you log into macOS and runs while your GUI session exists.
Calendar events missed during sleep run once on wake. It does not run at install
time or immediately on macOS login. A failed or unanswered attempt waits until
the next scheduled event; each attempt has a ten-minute timeout. Launchd prevents
overlapping scheduled instances. A separate manual login can still overlap.

The installer copies the runner into
`~/Library/Application Support/rovo-auth-refresh/` and the LaunchAgent into
`~/Library/LaunchAgents/com.jbranham.rovo-auth-refresh.plist`, so the workspace
copy is not needed after installation. It uses `/usr/bin/python3` (available on
this Mac through Apple's developer tools) and the current `codex` executable
path. Run the installer again if that executable moves.

Check the job or trigger a login now:

```sh
rtk proxy launchctl print "gui/$(id -u)/com.jbranham.rovo-auth-refresh"
rtk proxy launchctl kickstart "gui/$(id -u)/com.jbranham.rovo-auth-refresh"
```

Read the status log:

```sh
rtk proxy tail -20 "$HOME/Library/Application Support/rovo-auth-refresh/refresh.log"
```

Logs record success, failure, and timeout, rotate at 256 KiB, and omit Codex's
OAuth output. For detailed login errors, run the original command in a terminal.

Remove the schedule (keeps your Codex credentials and the status logs):

```sh
rtk proxy launchctl bootout "gui/$(id -u)/com.jbranham.rovo-auth-refresh"
rtk proxy rm "$HOME/Library/LaunchAgents/com.jbranham.rovo-auth-refresh.plist"
```

Codex documents MCP OAuth login in the
[official MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
