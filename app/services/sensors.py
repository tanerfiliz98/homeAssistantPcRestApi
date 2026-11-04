import platform
import socket
import time
from datetime import datetime, timezone

import psutil


BOOT_TIME = psutil.boot_time()


def _bytes_to_gb(value: int) -> float:
    return round(value / (1024**3), 2)


def get_system_info() -> dict:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "boot_time": datetime.fromtimestamp(BOOT_TIME, tz=timezone.utc).isoformat(),
        "uptime_seconds": int(time.time() - BOOT_TIME),
    }


def get_cpu() -> dict:
    freq = psutil.cpu_freq()
    return {
        "percent": psutil.cpu_percent(interval=0.2),
        "count_logical": psutil.cpu_count(logical=True),
        "count_physical": psutil.cpu_count(logical=False),
        "freq_mhz": round(freq.current, 1) if freq else None,
        "per_cpu_percent": psutil.cpu_percent(interval=None, percpu=True),
    }


def get_memory() -> dict:
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": _bytes_to_gb(mem.total),
        "used_gb": _bytes_to_gb(mem.used),
        "available_gb": _bytes_to_gb(mem.available),
        "percent": mem.percent,
        "swap_total_gb": _bytes_to_gb(swap.total),
        "swap_used_gb": _bytes_to_gb(swap.used),
        "swap_percent": swap.percent,
    }


SKIP_FS_TYPES = {
    "",
    "tmpfs",
    "devtmpfs",
    "squashfs",
    "overlay",
    "proc",
    "sysfs",
    "devfs",
    "cgroup",
    "cgroup2",
    "pstore",
    "bpf",
    "tracefs",
    "debugfs",
    "securityfs",
    "hugetlbfs",
    "mqueue",
    "fusectl",
    "configfs",
    "ramfs",
    "autofs",
}


def get_disks() -> list[dict]:
    disks: list[dict] = []
    for part in psutil.disk_partitions(all=False):
        fstype = (part.fstype or "").lower()
        if "cdrom" in part.opts or fstype in SKIP_FS_TYPES:
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):
            continue
        disks.append(
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": _bytes_to_gb(usage.total),
                "used_gb": _bytes_to_gb(usage.used),
                "free_gb": _bytes_to_gb(usage.free),
                "percent": usage.percent,
            }
        )
    return disks


def get_network() -> dict:
    counters = psutil.net_io_counters()
    return {
        "bytes_sent": counters.bytes_sent,
        "bytes_recv": counters.bytes_recv,
        "packets_sent": counters.packets_sent,
        "packets_recv": counters.packets_recv,
        "bytes_sent_gb": _bytes_to_gb(counters.bytes_sent),
        "bytes_recv_gb": _bytes_to_gb(counters.bytes_recv),
    }


def get_temperatures() -> dict:
    if not hasattr(psutil, "sensors_temperatures"):
        return {"available": False, "sensors": []}

    raw = psutil.sensors_temperatures(fahrenheit=False) or {}
    sensors = []
    for name, entries in raw.items():
        for entry in entries:
            sensors.append(
                {
                    "name": name,
                    "label": entry.label or name,
                    "current_c": entry.current,
                    "high_c": entry.high,
                    "critical_c": entry.critical,
                }
            )
    return {"available": bool(sensors), "sensors": sensors}


def get_battery() -> dict:
    battery = psutil.sensors_battery()
    if battery is None:
        return {"available": False}

    return {
        "available": True,
        "percent": battery.percent,
        "plugged_in": battery.power_plugged,
        "secs_left": battery.secsleft if battery.secsleft >= 0 else None,
    }


def get_all_sensors() -> dict:
    return {
        "system": get_system_info(),
        "cpu": get_cpu(),
        "memory": get_memory(),
        "disks": get_disks(),
        "network": get_network(),
        "temperatures": get_temperatures(),
        "battery": get_battery(),
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
