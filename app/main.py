from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import PROJECT_ROOT, settings
from app.mdns import start_mdns, stop_mdns
from app.routers import power
from app.services.power import detect_os


@asynccontextmanager
async def lifespan(_app: FastAPI):
    mdns_state = await start_mdns()
    try:
        yield
    finally:
        await stop_mdns(mdns_state)


app = FastAPI(
    title="Home Assistant PC REST API",
    description="Control this PC (Windows / Linux / macOS) and read local sensor data from Home Assistant.",
    version="1.2.0",
    lifespan=lifespan,
)

app.include_router(power.router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "platform": detect_os(),
        "mdns": {
            "enabled": settings.mdns_enabled,
            "name": f"{settings.mdns_name}.local" if settings.mdns_enabled else None,
            "url": (
                f"http://{settings.mdns_name}.local:{settings.port}"
                if settings.mdns_enabled
                else None
            ),
        },
    }


def _log_config(log_file: Path) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(asctime)s %(levelprefix)s %(message)s",
                "use_colors": False,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                "use_colors": False,
            },
        },
        "handlers": {
            "default": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": str(log_file),
                "maxBytes": 1_000_000,
                "backupCount": 3,
                "encoding": "utf-8",
            },
            "access": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "access",
                "filename": str(log_file),
                "maxBytes": 1_000_000,
                "backupCount": 3,
                "encoding": "utf-8",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stderr",
            },
            "console_access": {
                "class": "logging.StreamHandler",
                "formatter": "access",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default", "console"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["default", "console"], "level": "INFO", "propagate": False},
            "uvicorn.access": {
                "handlers": ["access", "console_access"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


def run() -> None:
    import uvicorn

    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "service.log"

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_config=_log_config(log_file),
    )


if __name__ == "__main__":
    run()
