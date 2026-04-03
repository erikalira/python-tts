"""HTTP server using aiohttp."""
import logging
from aiohttp import web
from src.presentation.http_controllers import SpeakController, VoiceContextController
from src.__version__ import __version__, __author__, __description__

logger = logging.getLogger(__name__)


class HTTPServer:
    """HTTP server for bot endpoints.
    
    Follows Single Responsibility: only handles HTTP server setup.
    """
    
    def __init__(
        self,
        speak_controller: SpeakController,
        voice_context_controller: VoiceContextController,
        port: int,
    ):
        """Initialize HTTP server.
        
        Args:
            speak_controller: Controller for /speak endpoint
            voice_context_controller: Controller for /voice-context endpoint
            port: Port to listen on
        """
        self._speak_controller = speak_controller
        self._voice_context_controller = voice_context_controller
        self._port = port
        self._runner = None
        self._site = None

    def _build_app(self) -> web.Application:
        """Build aiohttp application with operational and integration endpoints."""
        app = web.Application()
        app.router.add_get('/', self._home)
        app.router.add_get('/health', self._health)
        app.router.add_get('/version', self._version)
        app.router.add_get('/about', self._about)
        app.router.add_get('/voice-context', self._voice_context_controller.handle)
        app.router.add_post('/speak', self._speak_controller.handle)
        return app

    async def _home(self, request: web.Request) -> web.Response:
        return web.Response(text="Bot online! v2.0")

    async def _health(self, request: web.Request) -> web.Response:
        """Health check endpoint for Docker/Render."""
        return web.json_response({"status": "healthy"})

    async def _version(self, request: web.Request) -> web.Response:
        return web.json_response({
            "version": __version__,
            "author": __author__,
            "description": __description__,
        })

    async def _about(self, request: web.Request) -> web.Response:
        return web.json_response({
            "name": "TTS Hotkey Windows",
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
        
        self._site = web.TCPSite(self._runner, '0.0.0.0', self._port)
        await self._site.start()
        
        logger.info(f"🌐 HTTP server started on port {self._port}")
    
    async def stop(self):
        """Stop HTTP server."""
        if self._runner:
            await self._runner.cleanup()
