"""Console-based configuration dialog for the Desktop App."""

from __future__ import annotations

from typing import Optional

from src.application.tts_voice_catalog import TTSCatalog
from src.infrastructure.tts.voice_catalog import RuntimeTTSCatalog

from ..config.desktop_config import ConfigurationValidator, DesktopAppConfig
from .config_dialog_contracts import ConfigInterface
from .config_helpers import build_updated_config, prompt_numeric_input, resolve_text_value


class ConsoleConfig(ConfigInterface):
    """Console configuration interface."""

    def __init__(self, tts_catalog: TTSCatalog | None = None):
        self._tts_catalog = tts_catalog or RuntimeTTSCatalog()

    def show_config(self, config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        print("\n" + "=" * 50)
        print("Desktop App - Configuracao")
        print("=" * 50)

        current_id = config.discord.member_id or ""
        member_id = prompt_numeric_input(
            f"Discord User ID [{current_id}]: ",
            current_id,
            "Discord User ID deve conter apenas numeros!",
        )
        bot_url = resolve_text_value(input(f"Bot URL [{config.discord.bot_url}]: "), config.discord.bot_url)

        print("\nEngines TTS disponiveis:")
        print("1. gtts (Google TTS)")
        print("2. pyttsx3 (local)")
        print("3. edge-tts (vozes neurais)")
        while True:
            choice = input(f"Escolha [1-3, atual: {config.tts.engine}]: ").strip()
            if not choice:
                engine = config.tts.engine
                break
            if choice == "1":
                engine = "gtts"
                break
            if choice == "2":
                engine = "pyttsx3"
                break
            if choice == "3":
                engine = "edge-tts"
                break
            print("Opcao invalida!")

        selected_option = self._prompt_voice_option(engine, config)
        default_language = selected_option.language if selected_option is not None else config.tts.language
        default_voice_id = selected_option.voice_id if selected_option is not None else config.tts.voice_id
        language = resolve_text_value(input(f"Idioma [{default_language}]: "), default_language)
        voice_id = resolve_text_value(input(f"Voice ID [{default_voice_id}]: "), default_voice_id)

        while True:
            rate_input = input(f"Velocidade [{config.tts.rate}]: ").strip()
            if not rate_input:
                rate = config.tts.rate
                break
            try:
                rate = int(rate_input)
                if 50 <= rate <= 400:
                    break
                print("Velocidade deve estar entre 50 e 400!")
            except ValueError:
                print("Velocidade deve ser um numero!")

        print("\nLocal voice in the Windows app:")
        print("1. Disabled (recommended: use only the Discord bot)")
        print("2. Enabled (accessibility/local fallback with pyttsx3)")
        while True:
            local_choice = input(
                "Enable local voice in the Windows app? "
                f"[1-2, current: {'enabled' if config.interface.local_tts_enabled else 'disabled'}]: "
            ).strip()
            if not local_choice:
                local_tts_enabled = config.interface.local_tts_enabled
                break
            if local_choice == "1":
                local_tts_enabled = False
                break
            if local_choice == "2":
                local_tts_enabled = True
                break
            print("Invalid option!")

        print("\nConfiguracao de Triggers")
        trigger_open = resolve_text_value(
            input(f"Trigger abrir [{config.hotkey.trigger_open}]: "),
            config.hotkey.trigger_open,
        )
        trigger_close = resolve_text_value(
            input(f"Trigger fechar [{config.hotkey.trigger_close}]: "),
            config.hotkey.trigger_close,
        )

        new_config = build_updated_config(
            config,
            member_id=member_id,
            bot_url=bot_url,
            engine=engine,
            language=language,
            voice_id=voice_id,
            rate=rate,
            trigger_open=trigger_open,
            trigger_close=trigger_close,
            local_tts_enabled=local_tts_enabled,
        )

        is_valid, errors = ConfigurationValidator.validate(new_config)
        if is_valid:
            print("Configuracao salva com sucesso!")
            return new_config

        print("Erros na configuracao:")
        for error in errors:
            print(f"   - {error}")
        return None

    def _prompt_voice_option(self, engine: str, config: DesktopAppConfig):
        options = [option for option in self._tts_catalog.list_voice_options() if option.engine == engine]
        if not options:
            return None

        print(f"\nVozes disponiveis para {engine}:")
        current_option = self._tts_catalog.find_voice_option(
            engine=config.tts.engine,
            language=config.tts.language,
            voice_id=config.tts.voice_id,
        )
        for index, option in enumerate(options, start=1):
            current_marker = " (atual)" if current_option and option.key == current_option.key else ""
            print(f"{index}. {option.label}{current_marker}")

        while True:
            choice = input("Escolha uma voz do catalogo ou pressione Enter para manter/editar manualmente: ").strip()
            if not choice:
                return None
            if choice.isdigit():
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(options):
                    return options[selected_index]
            print("Opcao invalida!")
