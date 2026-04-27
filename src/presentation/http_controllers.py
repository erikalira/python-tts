"""HTTP controllers for handling web requests."""

import hashlib
import hmac
import logging

from aiohttp import web

from src.application.dto import BotSpeakRequestDTO, SpeakTextInputDTO, VoiceContextQueryDTO
from src.application.rate_limiting import RateLimiter, RateLimitRequest, RateLimitResult
from src.application.runtime_telemetry import NullRuntimeSpanContext, RuntimeTelemetry
from src.application.use_cases import GetCurrentVoiceContextUseCase, SpeakTextUseCase
from src.core.entities import TTSConfig
from src.core.interfaces import IConfigRepository
from src.presentation.http_presenters import HTTPSpeakPresenter, HTTPVoiceContextPresenter

logger = logging.getLogger(__name__)

_ALLOW_RATE_LIMIT_RESULT = RateLimitResult(allowed=True, scope="disabled")


class SpeakController:
    """Controller for /speak endpoint."""

    def __init__(
        self,
        speak_use_case: SpeakTextUseCase,
        config_repository: IConfigRepository | None = None,
        rate_limiter: RateLimiter | None = None,
        rate_limit_max_requests: int = 0,
        rate_limit_window_seconds: float = 0,
        auth_token: str | None = None,
        max_text_length: int = 500,
        otel_runtime: RuntimeTelemetry | None = None,
    ):
        self._speak_use_case = speak_use_case
        self._config_repository = config_repository
        self._rate_limiter = rate_limiter
        self._rate_limit_max_requests = rate_limit_max_requests
        self._rate_limit_window_seconds = rate_limit_window_seconds
        self._auth_token = auth_token
        self._max_text_length = max_text_length
        self._presenter = HTTPSpeakPresenter()
        self._otel_runtime = otel_runtime

    async def handle(self, request: web.Request) -> web.Response:
        headers = getattr(request, "headers", {}) or {}
        with self._otel_runtime.start_http_span(
            "http.speak",
            headers=headers,
            attributes={"http.route": "/speak", "http.method": "POST"},
        ) if self._otel_runtime is not None else NullRuntimeSpanContext() as span:
            presented_token = self._presented_token(headers)
            if not self._is_authorized(presented_token):
                logger.warning("[AUTH] HTTP /speak rejected unauthorized request")
                span.set_attribute("result_code", "unauthorized")
                return web.Response(text="unauthorized", status=401)

            content_type = getattr(request, "content_type", "application/json") or ""
            if isinstance(content_type, str) and content_type != "application/json":
                span.set_attribute("result_code", "unsupported_media_type")
                return web.Response(text="unsupported media type", status=415)

            try:
                data = await request.json()
            except Exception as exc:
                logger.error("Invalid JSON: %s", exc)
                span.set_attribute("result_code", "invalid_json")
                if self._otel_runtime is not None:
                    self._otel_runtime.mark_span_error(span, exc)
                return web.Response(text="invalid json", status=400)
            if not isinstance(data, dict):
                span.set_attribute("result_code", "invalid_json_object")
                return web.Response(text="invalid json object", status=400)
            parsed_text = self._parse_text(data.get("text"))
            if len(parsed_text) > self._max_text_length:
                span.set_attribute("result_code", "text_too_long")
                return web.Response(text="text too long", status=413)

            guild_id = self._parse_int(data.get("guild_id"))
            member_id_value = data.get("member_id") or data.get("user_id")
            config_override = self._parse_config_override(data, guild_id, self._parse_int(member_id_value))
            request_dto = BotSpeakRequestDTO(
                text=parsed_text,
                channel_id=self._parse_int(data.get("channel_id")),
                guild_id=guild_id,
                member_id=str(member_id_value) if member_id_value is not None else None,
                config_override=config_override,
            )
            span.set_attribute("guild_id", str(guild_id) if guild_id is not None else "unknown")
            span.set_attribute(
                "engine",
                config_override.engine if config_override is not None else "configured_default",
            )
            rate_limit_result = self._check_rate_limit(guild_id, self._parse_int(member_id_value), presented_token)
            if not rate_limit_result.allowed:
                logger.warning(
                    "[RATE_LIMIT] HTTP /speak blocked scope=%s retry_after_seconds=%.2f",
                    rate_limit_result.scope,
                    rate_limit_result.retry_after_seconds or 0,
                )
                span.set_attribute("result_code", "rate_limited")
                span.set_attribute("rate_limited", True)
                span.set_attribute("rate_limit_scope", rate_limit_result.scope)
                return web.Response(
                    text=self._presenter.build_rate_limit_message(rate_limit_result),
                    status=self._presenter.get_rate_limit_status_code(rate_limit_result),
                )

            tts_request = SpeakTextInputDTO(
                text=request_dto.text,
                channel_id=request_dto.channel_id,
                guild_id=request_dto.guild_id,
                member_id=self._parse_int(request_dto.member_id),
                config_override=request_dto.config_override,
                trace_context=self._otel_runtime.inject_current_context() if self._otel_runtime is not None else None,
            )
            result = await self._speak_use_case.execute(tts_request)
            span.set_attribute("result_code", result.code)
            span.set_attribute("timeout_flag", result.code in {"generation_timeout", "playback_timeout"})
            return web.Response(
                text=self._presenter.build_message(result),
                status=self._presenter.get_status_code(result),
            )

    def _check_rate_limit(
        self,
        guild_id: int | None,
        member_id: int | None,
        presented_token: str | None = None,
    ) -> RateLimitResult:
        if self._rate_limiter is None:
            return _ALLOW_RATE_LIMIT_RESULT

        scope = self._rate_limit_scope(guild_id, member_id, presented_token)
        return self._rate_limiter.check(
            RateLimitRequest(
                scope=scope,
                limit=self._rate_limit_max_requests,
                window_seconds=self._rate_limit_window_seconds,
            )
        )

    def _rate_limit_scope(self, guild_id: int | None, member_id: int | None, presented_token: str | None = None) -> str:
        guild = str(guild_id) if guild_id is not None else "unknown"
        member = str(member_id) if member_id is not None else "unknown"
        if self._auth_token and presented_token:
            token_hash = hashlib.sha256(presented_token.encode("utf-8")).hexdigest()[:12]
            return f"http:speak:token:{token_hash}:guild:{guild}:member:{member}"
        return f"http:speak:guild:{guild}:member:{member}"

    def _presented_token(self, headers) -> str | None:
        header_token = headers.get("X-Bot-Token") if headers else None
        if header_token:
            return str(header_token)

        authorization = headers.get("Authorization") if headers else None
        if not authorization:
            return None
        scheme, _, value = str(authorization).partition(" ")
        if scheme.lower() != "bearer" or not value:
            return None
        return value

    def _is_authorized(self, presented_token: str | None) -> bool:
        if not self._auth_token:
            return True
        if not presented_token:
            return False
        return hmac.compare_digest(presented_token, self._auth_token)

    def _parse_int(self, value) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _parse_text(self, value) -> str:
        if isinstance(value, str):
            return value
        return ""

    def _parse_config_override(
        self,
        data: dict,
        guild_id: int | None = None,
        member_id: int | None = None,
    ) -> TTSConfig | None:
        override = data.get("config_override")
        if not isinstance(override, dict):
            override = data

        engine = override.get("engine")
        language = override.get("language")
        voice_id = override.get("voice_id")
        rate = override.get("rate")

        if engine is None and language is None and voice_id is None and rate is None:
            return None

        base_config = self._get_base_config(guild_id, member_id)
        return TTSConfig(
            engine=str(engine or base_config.engine),
            language=str(language or base_config.language),
            voice_id=str(voice_id or base_config.voice_id),
            rate=self._parse_int(rate) or base_config.rate,
            output_device=base_config.output_device,
        )

    def _get_base_config(self, guild_id: int | None, member_id: int | None = None) -> TTSConfig:
        if self._config_repository is None:
            return TTSConfig()
        return self._config_repository.get_config(guild_id, user_id=member_id)


class VoiceContextController:
    """Controller for querying the current voice context for a member."""

    def __init__(self, voice_context_use_case: GetCurrentVoiceContextUseCase):
        self._voice_context_use_case = voice_context_use_case
        self._presenter = HTTPVoiceContextPresenter()

    async def handle(self, request: web.Request) -> web.Response:
        query = VoiceContextQueryDTO(
            member_id=self._parse_int(request.query.get("member_id") or request.query.get("user_id"))
        )
        result = await self._voice_context_use_case.execute(query)
        return web.json_response(
            self._presenter.to_payload(result),
            status=self._presenter.get_status_code(result),
        )

    def _parse_int(self, value) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
