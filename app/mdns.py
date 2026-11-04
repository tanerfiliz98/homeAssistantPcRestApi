import logging
import socket

from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf

from app.config import settings

logger = logging.getLogger("uvicorn.error")


def _lan_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def _service_info() -> ServiceInfo:
    name = settings.mdns_name.strip().rstrip(".")
    if not name:
        raise RuntimeError("MDNS_NAME cannot be empty")

    ip = _lan_ip()
    host_fqdn = f"{name}.local."
    service_type = "_http._tcp.local."
    service_name = f"{name}.{service_type}"

    return ServiceInfo(
        type_=service_type,
        name=service_name,
        addresses=[socket.inet_aton(ip)],
        port=settings.port,
        properties={
            "path": "/",
            "api": "homeassistant-pc-rest-api",
        },
        server=host_fqdn,
    )


async def start_mdns() -> tuple[AsyncZeroconf, ServiceInfo] | None:
    if not settings.mdns_enabled:
        return None

    info = _service_info()
    aio_zc = AsyncZeroconf()
    await aio_zc.async_register_service(info)
    await aio_zc.zeroconf.async_wait_for_start()

    name = settings.mdns_name.strip().rstrip(".")
    ip = socket.inet_ntoa(info.addresses[0])
    logger.info("mDNS advertised as http://%s.local:%s (ip=%s)", name, settings.port, ip)
    return aio_zc, info


async def stop_mdns(state: tuple[AsyncZeroconf, ServiceInfo] | None) -> None:
    if not state:
        return
    aio_zc, info = state
    try:
        await aio_zc.async_unregister_service(info)
    finally:
        await aio_zc.async_close()
