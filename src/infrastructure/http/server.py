"""HTTP server using aiohttp."""
import asyncio
import logging
from aiohttp import web
from src.presentation.http_controllers import SpeakController

logger = logging.getLogger(__name__)


class HTTPServer:
    """HTTP server for bot endpoints.
    
    Follows Single Responsibility: only handles HTTP server setup.
    """
    
    def __init__(self, speak_controller: SpeakController, port: int):
        """Initialize HTTP server.
        
        Args:
            speak_controller: Controller for /speak endpoint
            port: Port to listen on
        """
        self._speak_controller = speak_controller
        self._port = port
        self._runner = None
        self._site = None
    
    async def start(self):
        """Start HTTP server."""
        app = web.Application()
        app.router.add_post('/speak', self._speak_controller.handle)
        
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        
        self._site = web.TCPSite(self._runner, '0.0.0.0', self._port)
        await self._site.start()
        
        logger.info(f"🌐 HTTP server started on port {self._port}")
    
    async def stop(self):
        """Stop HTTP server."""
        if self._runner:
            await self._runner.cleanup()
