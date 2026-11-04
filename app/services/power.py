import platform
import shutil
import subprocess
from typing import Literal

PowerAction = Literal["shutdown", "restart", "sleep", "hibernate", "lock", "cancel"]

OS_WINDOWS = "windows"
OS_LINUX = "linux"
OS_MACOS = "darwin"


class UnsupportedActionError(RuntimeError):
    """Raised when the current OS cannot perform the requested power action."""


def detect_os() -> str:
    return platform.system().lower()


def _run(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        stderr = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(stderr or f"Command failed with code {result.returncode}: {' '.join(command)}")


def _first_available(commands: list[list[str]]) -> list[str]:
    for command in commands:
        if shutil.which(command[0]):
            return command
    raise RuntimeError(
        "No supported command found. Tried: " + ", ".join(cmd[0] for cmd in commands)
    )


def _seconds_to_shutdown_minutes(delay_seconds: int) -> int:
    """Unix `shutdown` uses minutes; keep at least 1 minute when a delay is requested."""
    if delay_seconds <= 0:
        return 0
    return max(1, (delay_seconds + 59) // 60)


def _windows_command(action: PowerAction, delay_seconds: int) -> list[str]:
    delay = max(0, delay_seconds)
    commands: dict[PowerAction, list[str]] = {
        "shutdown": ["shutdown", "/s", "/t", str(delay)],
        "restart": ["shutdown", "/r", "/t", str(delay)],
        "sleep": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
        "hibernate": ["shutdown", "/h"],
        "lock": ["rundll32.exe", "user32.dll,LockWorkStation"],
        "cancel": ["shutdown", "/a"],
    }
    return commands[action]


def _linux_command(action: PowerAction, delay_seconds: int) -> list[str]:
    minutes = _seconds_to_shutdown_minutes(delay_seconds)

    if action == "shutdown":
        if minutes == 0:
            return _first_available(
                [
                    ["systemctl", "poweroff"],
                    ["shutdown", "-h", "now"],
                    ["poweroff"],
                ]
            )
        return ["shutdown", "-h", f"+{minutes}"]

    if action == "restart":
        if minutes == 0:
            return _first_available(
                [
                    ["systemctl", "reboot"],
                    ["shutdown", "-r", "now"],
                    ["reboot"],
                ]
            )
        return ["shutdown", "-r", f"+{minutes}"]

    if action == "sleep":
        return _first_available(
            [
                ["systemctl", "suspend"],
                ["pm-suspend"],
            ]
        )

    if action == "hibernate":
        return _first_available(
            [
                ["systemctl", "hibernate"],
                ["pm-hibernate"],
            ]
        )

    if action == "lock":
        return _first_available(
            [
                ["loginctl", "lock-session"],
                ["xdg-screensaver", "lock"],
                ["gnome-screensaver-command", "--lock"],
                ["dm-tool", "lock"],
            ]
        )

    if action == "cancel":
        return ["shutdown", "-c"]

    raise RuntimeError(f"Unsupported action: {action}")


def _macos_command(action: PowerAction, delay_seconds: int) -> list[str]:
    minutes = _seconds_to_shutdown_minutes(delay_seconds)

    if action == "shutdown":
        if minutes == 0:
            return ["shutdown", "-h", "now"]
        return ["shutdown", "-h", f"+{minutes}"]

    if action == "restart":
        if minutes == 0:
            return ["shutdown", "-r", "now"]
        return ["shutdown", "-r", f"+{minutes}"]

    if action == "sleep":
        return ["pmset", "sleepnow"]

    if action == "hibernate":
        # macOS uses Safe Sleep; there is no direct userland hibernate equivalent.
        raise UnsupportedActionError(
            "hibernate is not supported on macOS; use sleep instead (Safe Sleep)"
        )

    if action == "lock":
        return [
            "osascript",
            "-e",
            'tell application "System Events" to keystroke "q" using {control down, command down}',
        ]

    if action == "cancel":
        # Prefer shutdown -c when available; fall back to killing pending shutdown.
        if shutil.which("shutdown"):
            return ["shutdown", "-c"]
        return ["killall", "shutdown"]

    raise RuntimeError(f"Unsupported action: {action}")


def run_power_action(action: PowerAction, delay_seconds: int = 0) -> dict:
    delay = max(0, int(delay_seconds))
    os_name = detect_os()

    if os_name == OS_WINDOWS:
        command = _windows_command(action, delay)
        effective_delay = delay if action in {"shutdown", "restart"} else 0
    elif os_name == OS_LINUX:
        command = _linux_command(action, delay)
        effective_delay = (
            _seconds_to_shutdown_minutes(delay) * 60
            if action in {"shutdown", "restart"} and delay > 0
            else 0
        )
    elif os_name == OS_MACOS:
        command = _macos_command(action, delay)
        effective_delay = (
            _seconds_to_shutdown_minutes(delay) * 60
            if action in {"shutdown", "restart"} and delay > 0
            else 0
        )
    else:
        raise RuntimeError(f"Unsupported operating system: {platform.system()}")

    _run(command)

    return {
        "action": action,
        "platform": os_name,
        "delay_seconds": effective_delay,
        "status": "ok",
        "message": f"{action} requested",
        "command": command,
    }
