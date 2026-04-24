"""HTTP server using aiohttp."""
from __future__ import annotations

import logging
from dataclasses import asdict
from collections.abc import Awaitable, Callable

from aiohttp import web

from src.application.dto import BotHealthResponseDTO
from src.__version__ import __version__, __author__, __description__
from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime

logger = logging.getLogger(__name__)

RequestHandler = Callable[[web.Request], Awaitable[web.StreamResponse]]
ObservabilitySnapshotProvider = Callable[[], dict[str, object]]


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
        otel_runtime: OpenTelemetryRuntime | None = None,
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
        self._otel_runtime = otel_runtime
        self._runner = None
        self._site = None

    def _build_app(self) -> web.Application:
        """Build aiohttp application with operational and integration endpoints."""
        app = web.Application()
        app.router.add_get('/', self._home)
        app.router.add_get('/health', self._health, name='health')
        app.router.add_get('/observability', self._observability, name='observability')
        app.router.add_get('/version', self._version)
        app.router.add_get('/about', self._about)
        app.router.add_get('/voice-context', self._voice_context_handler)
        app.router.add_post('/speak', self._speak_handler)
        return app

    async def _home(self, request: web.Request) -> web.Response:
        return web.Response(text="Bot online! v2.0")

    async def _health(self, request: web.Request) -> web.Response:
        """Health check endpoint for Docker/Render."""
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
