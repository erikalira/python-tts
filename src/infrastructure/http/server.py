"""HTTP server using aiohttp."""
from __future__ import annotations

import logging
import re
from collections.abc import Awaitable, Callable
from dataclasses import asdict

from aiohttp import web

from src.__version__ import __author__, __description__, __version__
from src.application.dto import BotHealthResponseDTO
from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime

logger = logging.getLogger(__name__)

RequestHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]
ObservabilitySnapshotProvider = Callable[[], dict[str, object]]
ReadinessProvider = Callable[[], Awaitable[dict[str, object]]]
_HTTP_HEADER_TOKEN_PATTERN = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")


class HTTPServer:
    """HTTP server for bot endpoints.
    
    Follows Single Responsibility: only handles HTTP server setup.
    """
    
    def __init__(
        self,
        speak_handler: RequestHandler,
        voice_context_handler: RequestHandler,
        port: int,
        host: str = "127.0.0.1",
        observability_snapshot_provider: ObservabilitySnapshotProvider | None = None,
        readiness_provider: ReadinessProvider | None = None,
        otel_runtime: OpenTelemetryRuntime | None = None,
        cors_allowed_origins: tuple[str, ...] = (),
        max_request_body_bytes: int = 4096,
    ):
        """Initialize HTTP server.
        
        Args:
            speak_handler: Handler for /speak endpoint
            voice_context_handler: Handler for /voice-context endpoint
            port: Port to listen on
            host: Host interface to bind to
        """
        self._speak_handler = speak_handler
        self._voice_context_handler = voice_context_handler
        self._port = port
        self._host = host
        self._observability_snapshot_provider = observability_snapshot_provider
        self._readiness_provider = readiness_provider
        self._otel_runtime = otel_runtime
        self._cors_allowed_origins = frozenset(cors_allowed_origins)
        self._max_request_body_bytes = max_request_body_bytes
        self._runner = None
        self._site = None

    def _build_app(self) -> web.Application:
        """Build aiohttp application with operational and integration endpoints."""
        app = web.Application(
            client_max_size=self._max_request_body_bytes,
            middlewares=[self._cors_middleware],
        )
        app.router.add_get('/', self._home)
        app.router.add_get('/health', self._health, name='health')
        app.router.add_get('/ready', self._ready, name='ready')
        app.router.add_get('/observability', self._observability, name='observability')
        app.router.add_get('/version', self._version)
        app.router.add_get('/about', self._about)
        app.router.add_get('/voice-context', self._voice_context_handler)
        app.router.add_options('/speak', self._speak_preflight)
        app.router.add_post('/speak', self._speak_handler)
        return app

    @web.middleware
    async def _cors_middleware(self, request: web.Request, handler: RequestHandler) -> web.StreamResponse:
        response = await handler(request)
        self._apply_cors_headers(request, response)
        return response

    async def _speak_preflight(self, request: web.Request) -> web.Response:
        origin = request.headers.get("Origin")
        if origin and origin not in self._cors_allowed_origins:
            return web.Response(text="cors origin not allowed", status=403)
        return web.Response(status=204)

    def _apply_cors_headers(self, request: web.Request, response: web.StreamResponse) -> None:
        origin = request.headers.get("Origin")
        if not origin or origin not in self._cors_allowed_origins:
            return

        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Bot-Token"
        response.headers["Access-Control-Max-Age"] = "600"
        response.headers["Vary"] = _append_vary_origin(response.headers.get("Vary"))

    async def _home(self, request: web.Request) -> web.Response:
        return web.Response(text="Bot online! v2.0")

    async def _health(self, request: web.Request) -> web.Response:
        """Health check endpoint for container and runtime probes."""
        with self._otel_runtime.start_http_span(
            "http.health",
            headers=getattr(request, "headers", {}) or {},
            attributes={"http.route": "/health", "http.method": "GET"},
        ) if self._otel_runtime is not None else _null_span_context():
            return web.json_response(asdict(BotHealthResponseDTO(status="healthy")))

    async def _observability(self, request: web.Request) -> web.Response:
        """Expose a compact runtime observability snapshot for operational baselines."""
        if self._observability_snapshot_provider is None:
            return web.json_response({"status": "disabled"})
        return web.json_response(self._observability_snapshot_provider())

    async def _ready(self, request: web.Request) -> web.Response:
        """Readiness endpoint that checks configured external dependencies."""
        if self._readiness_provider is None:
            return web.json_response({"status": "unknown", "dependencies": []}, status=503)
        payload = await self._readiness_provider()
        status_code = 200 if payload.get("status") == "ready" else 503
        return web.json_response(payload, status=status_code)

    async def _version(self, request: web.Request) -> web.Response:
        return web.json_response({
            "version": __version__,
            "author": __author__,
            "description": __description__,
        })

    async def _about(self, request: web.Request) -> web.Response:
        return web.json_response({
            "name": "Discord Bot and Desktop App",
            "version": __version__,
            "author": __author__,
            "description": __description__,
            "status": "online",
        })
    
    async def start(self):
        """Start HTTP server."""
        app = self._build_app()
        
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        
        self._site = web.TCPSite(self._runner, self._host, self._port)
        await self._site.start()
        
        logger.info("HTTP server started on %s:%s", self._host, self._port)
    
    async def stop(self):
        """Stop HTTP server."""
        if self._runner:
            await self._runner.cleanup()


class _null_span_context:
    def __enter__(self) -> "_null_span_context":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        del exc_type, exc, tb
        return False


def _append_vary_origin(current: str | None) -> str:
    if not current:
        return "Origin"
    values = [
        value.strip()
        for value in current.split(",")
        if _HTTP_HEADER_TOKEN_PATTERN.fullmatch(value.strip())
    ]
    if any(value.lower() == "origin" for value in values):
        return ", ".join(values)
    return ", ".join([*values, "Origin"])
