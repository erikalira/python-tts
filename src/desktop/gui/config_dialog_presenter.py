"""Presentation helpers for Desktop App configuration dialogs."""

from __future__ import annotations

from dataclasses import dataclass

from .config_helpers import normalize_optional_text, validate_numeric_field


@dataclass(frozen=True)
class DialogFeedback:
    """User-facing dialog feedback."""

    title: str
    message: str


class ConfigDialogsPresenter:
    """Build dialog messages and form results for Desktop App configuration UIs."""

    def build_skip_discord_result(self, *, bot_url: str) -> dict:
        return {
            "member_id": None,
            "bot_url": bot_url,
            "skip_discord": True,
        }

    def validate_initial_setup(
        self,
        *,
        member_id: str,
        bot_url: str,
    ) -> DialogFeedback | None:
        member_error = validate_numeric_field(
            member_id,
            required=False,
            required_message="",
            numeric_message="Discord User ID deve conter apenas numeros!",
        )
        if member_error:
            return DialogFeedback(title="Erro", message=member_error)

        if not bot_url.strip():
            return DialogFeedback(title="Erro", message="Bot URL e obrigatoria!")
        return None

    def build_initial_setup_result(
        self,
        *,
        member_id: str,
        bot_url: str,
    ) -> tuple[dict, DialogFeedback]:
        result = {
            "member_id": normalize_optional_text(member_id),
            "bot_url": bot_url,
            "skip_discord": False,
        }
        if normalize_optional_text(member_id):
            return result, DialogFeedback(
                title="Sucesso",
                message="Configuracao salva! O TTS funcionara no Discord.",
            )
        return result, DialogFeedback(
            title="Aviso",
            message="Sem Discord User ID, o TTS funcionara apenas localmente.",
        )

    def build_console_initial_setup_result(
        self,
        *,
        member_id: str,
        bot_url: str,
    ) -> dict:
        return {
            "member_id": normalize_optional_text(member_id),
            "bot_url": bot_url,
            "skip_discord": not bool(normalize_optional_text(member_id)),
        }

    def format_validation_errors(self, errors: list[str]) -> str:
        return "Erros encontrados:\n\n" + "\n".join(errors)
