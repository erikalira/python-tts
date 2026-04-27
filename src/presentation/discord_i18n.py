"""Discord-facing internationalization helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import discord
from discord import app_commands

SUPPORTED_LOCALES = ("pt-BR", "en-US")
DEFAULT_LOCALE = "en-US"


_MESSAGES: dict[str, dict[str, str]] = {
    "pt-BR": {
        "voice.runtime_unavailable": "❌ O recurso de voz do bot está indisponível no momento. Tente novamente mais tarde.",
        "bot.inactive": (
            "❌ **Bot está desligando ou inativo!**\n\n"
            "Tente novamente em alguns instantes ou avise um administrador."
        ),
        "bot.inactive.short": "❌ Bot está inativo ou desligando.",
        "error.unexpected": "❌ Erro inesperado",
        "error.guild_only": "❌ Este comando só pode ser usado em um servidor.",
        "error.invalid_voice": "❌ Voz inválida ou indisponível.",
        "error.load_voice_config": "❌ Não foi possível carregar a configuração atual da voz.",
        "config.update_error": "❌ Erro ao atualizar sua configuração",
        "config.reset_error": "❌ Erro ao resetar sua configuração",
        "config.title.current": "Sua Configuração de Voz",
        "config.description.current": "Configurações pessoais em {guild_name}",
        "config.title.updated": "✅ Configuração Atualizada",
        "config.description.updated": "Sua configuração de voz em {guild_name} foi atualizada",
        "config.title.reset": "Configuração Pessoal Resetada",
        "config.description.reset": "Seu override pessoal foi removido em {guild_name}",
        "config.field.voice": "Voz",
        "config.field.rate": "Taxa de Fala",
        "config.field.scope": "Escopo",
        "config.field.effective_source": "Origem Efetiva",
        "config.field.active_voice": "Voz Ativa Agora",
        "config.scope.personal": "Configuração pessoal neste servidor",
        "config.scope.saved": "Override pessoal salvo com sucesso",
        "config.scope.user": "Configuração pessoal",
        "config.scope.guild": "Padrão do servidor",
        "config.scope.global": "Padrão global",
        "config.footer.guild": "Servidor (Guild ID: {guild_id})",
        "voice_resolution.name": "Resolução da Voz",
        "voice_resolution.gtts": "Google TTS usa o idioma selecionado; não há catálogo local de vozes do sistema.",
        "voice_resolution.edge": "Edge TTS usará a voz neural '{voice_id}'.",
        "voice_resolution.pyttsx3.found": "Voz do Windows encontrada para '{voice_id}'.",
        "voice_resolution.pyttsx3.missing": "Voice ID '{voice_id}' não encontrado; o pyttsx3 usará a voz padrão do Windows.",
        "server_config.permission.update": "❌ Você precisa da permissão de gerenciar o servidor para alterar a voz padrão.",
        "server_config.permission.reset": "❌ Você precisa da permissão de gerenciar o servidor para resetar a voz padrão.",
        "server_config.update_error": "❌ Erro ao atualizar a configuração padrão do servidor",
        "server_config.reset_error": "❌ Erro ao resetar a configuração padrão do servidor",
        "server_config.title.current": "Configuração Padrão do Servidor",
        "server_config.description.current": "Voz usada em {guild_name} quando o usuário não tem configuração pessoal",
        "server_config.title.updated": "✅ Padrão do Servidor Atualizado",
        "server_config.description.updated": "Usuários sem voz pessoal agora usarão esta voz em {guild_name}",
        "server_config.title.reset": "Padrão do Servidor Resetado",
        "server_config.description.reset": "O padrão do servidor foi removido em {guild_name}",
        "server_config.scope.saved": "Padrão do servidor salvo com sucesso",
        "about.title": "Informações do TTS Bot",
        "about.version": "Versão",
        "about.author": "Autor",
        "about.available": "Disponível",
        "about.not_found": "Não encontrado",
        "about.installed": "Instalado",
        "about.not_installed": "Não instalado",
        "about.commands": "Comandos",
        "about.footer": "Rodando em {system} {release}",
        "about.commands.value": (
            "• `/join` - Entrar no seu canal de voz\n"
            "• `/leave` - Sair do canal de voz\n"
            "• `/speak` - Falar um texto\n"
            "• `/config` - Configurar sua voz pessoal\n"
            "• `/config-reset` - Resetar sua voz pessoal\n"
            "• `/server-config` - Configurar a voz padrão do servidor\n"
            "• `/server-config-reset` - Resetar a voz padrão do servidor\n"
            "• `/about` - Mostrar estas informações"
        ),
        "speak.queued": "Sua mensagem entrou na **fila** (**{position}**/{queue_size}).",
        "speak.missing_text": "Texto não informado.",
        "speak.user_not_in_channel": "Você não está em nenhuma sala de voz. Entre em uma sala e tente novamente.",
        "speak.queue_full": "Fila de áudio cheia. Tente novamente mais tarde.",
        "speak.missing_guild_id": "Erro: Não foi possível determinar o servidor.",
        "speak.voice_channel_not_found": "Bot não conseguiu encontrar sua sala de voz.",
        "speak.cross_guild_channel": "Canal de voz pertence a servidor diferente.",
        "speak.user_left_channel": "Você saiu do canal de voz.",
        "speak.generation_timeout": "Tempo limite excedido durante geração do áudio.",
        "speak.playback_timeout": "Tempo limite excedido durante reprodução.",
        "speak.voice_connection_failed": "Bot não conseguiu se conectar ao canal.",
        "speak.voice_permission_denied": "Bot não tem permissão neste canal.",
        "speak.unknown_error": "Erro ao reproduzir áudio.",
        "speak.unexpected_error": "Erro inesperado ao processar áudio.",
        "rate_limit.without_retry": "Muitas solicitações em pouco tempo. Tente novamente daqui a pouco.",
        "rate_limit.with_retry": "Muitas solicitações em pouco tempo. Tente novamente em {seconds} segundos.",
        "join.ok": "Entrei no seu canal.",
        "join.user_not_in_channel": "Você não está conectado a um canal de voz.",
        "join.missing_guild_id": "Este comando só pode ser usado em um servidor.",
        "join.voice_channel_not_found": "Não consegui encontrar o canal de voz.",
        "join.voice_connection_failed": "Não foi possível entrar no canal. Tente novamente.",
        "leave.ok": "Desconectado.",
        "leave.not_connected": "Não estou conectado a um canal de voz.",
        "leave.missing_guild_id": "Este comando só pode ser usado em um servidor.",
        "leave.voice_connection_failed": "Erro ao desconectar: {error_detail}",
        "leave.error": "Erro ao desconectar.",
        "language.invalid": "❌ Idioma de interface inválido.",
        "language.name.en-US": "inglês",
        "language.name.pt-BR": "português",
        "language.user.updated": "✅ O idioma da sua interface agora é {language_name}.",
        "language.user.automatic": "✅ Sua interface agora seguirá o idioma do seu Discord.",
        "language.guild.updated": "✅ O idioma padrão da interface do servidor agora é {language_name}.",
        "language.guild.automatic": "✅ Usuários sem idioma pessoal agora seguirão o idioma do Discord/servidor.",
        "language.update_error": "❌ Erro ao atualizar o idioma da interface.",
        "server_language.permission": "❌ Você precisa da permissão de gerenciar o servidor para alterar o idioma padrão.",
    },
    "en-US": {
        "voice.runtime_unavailable": "❌ Bot voice is unavailable right now. Try again later.",
        "bot.inactive": (
            "❌ **Bot is shutting down or inactive!**\n\n"
            "Try again in a moment or notify an administrator."
        ),
        "bot.inactive.short": "❌ Bot is inactive or shutting down.",
        "error.unexpected": "❌ Unexpected error",
        "error.guild_only": "❌ This command can only be used in a server.",
        "error.invalid_voice": "❌ Invalid or unavailable voice.",
        "error.load_voice_config": "❌ Could not load the current voice configuration.",
        "config.update_error": "❌ Error updating your configuration",
        "config.reset_error": "❌ Error resetting your configuration",
        "config.title.current": "Your Voice Configuration",
        "config.description.current": "Personal settings in {guild_name}",
        "config.title.updated": "✅ Configuration Updated",
        "config.description.updated": "Your voice configuration in {guild_name} was updated",
        "config.title.reset": "Personal Configuration Reset",
        "config.description.reset": "Your personal override was removed in {guild_name}",
        "config.field.voice": "Voice",
        "config.field.rate": "Speech Rate",
        "config.field.scope": "Scope",
        "config.field.effective_source": "Effective Source",
        "config.field.active_voice": "Active Voice Now",
        "config.scope.personal": "Personal configuration in this server",
        "config.scope.saved": "Personal override saved successfully",
        "config.scope.user": "Personal configuration",
        "config.scope.guild": "Server default",
        "config.scope.global": "Global default",
        "config.footer.guild": "Server (Guild ID: {guild_id})",
        "voice_resolution.name": "Voice Resolution",
        "voice_resolution.gtts": "Google TTS uses the selected language; there is no local system voice catalog.",
        "voice_resolution.edge": "Edge TTS will use the neural voice '{voice_id}'.",
        "voice_resolution.pyttsx3.found": "Windows voice found for '{voice_id}'.",
        "voice_resolution.pyttsx3.missing": "Voice ID '{voice_id}' was not found; pyttsx3 will use the default Windows voice.",
        "server_config.permission.update": "❌ You need the manage server permission to change the default voice.",
        "server_config.permission.reset": "❌ You need the manage server permission to reset the default voice.",
        "server_config.update_error": "❌ Error updating the server default configuration",
        "server_config.reset_error": "❌ Error resetting the server default configuration",
        "server_config.title.current": "Server Default Configuration",
        "server_config.description.current": "Voice used in {guild_name} when a user has no personal configuration",
        "server_config.title.updated": "✅ Server Default Updated",
        "server_config.description.updated": "Users without a personal voice will now use this voice in {guild_name}",
        "server_config.title.reset": "Server Default Reset",
        "server_config.description.reset": "The server default was removed in {guild_name}",
        "server_config.scope.saved": "Server default saved successfully",
        "about.title": "TTS Bot Information",
        "about.version": "Version",
        "about.author": "Author",
        "about.available": "Available",
        "about.not_found": "Not found",
        "about.installed": "Installed",
        "about.not_installed": "Not installed",
        "about.commands": "Commands",
        "about.footer": "Running on {system} {release}",
        "about.commands.value": (
            "• `/join` - Join your voice channel\n"
            "• `/leave` - Leave the voice channel\n"
            "• `/speak` - Speak text\n"
            "• `/config` - Configure your personal TTS settings\n"
            "• `/config-reset` - Reset your personal voice override\n"
            "• `/server-config` - Configure the server default voice\n"
            "• `/server-config-reset` - Reset the server default voice\n"
            "• `/about` - Show this info"
        ),
        "speak.queued": "Your message entered the **queue** (**{position}**/{queue_size}).",
        "speak.missing_text": "No text was provided.",
        "speak.user_not_in_channel": "You are not in a voice channel. Join one and try again.",
        "speak.queue_full": "Audio queue is full. Try again later.",
        "speak.missing_guild_id": "Error: Could not determine the server.",
        "speak.voice_channel_not_found": "Bot could not find your voice channel.",
        "speak.cross_guild_channel": "Voice channel belongs to a different server.",
        "speak.user_left_channel": "You left the voice channel.",
        "speak.generation_timeout": "Timed out while generating audio.",
        "speak.playback_timeout": "Timed out during playback.",
        "speak.voice_connection_failed": "Bot could not connect to the channel.",
        "speak.voice_permission_denied": "Bot does not have permission in this channel.",
        "speak.unknown_error": "Error playing audio.",
        "speak.unexpected_error": "Unexpected error while processing audio.",
        "rate_limit.without_retry": "Too many requests in a short time. Try again in a moment.",
        "rate_limit.with_retry": "Too many requests in a short time. Try again in {seconds} seconds.",
        "join.ok": "Joined your channel.",
        "join.user_not_in_channel": "You are not connected to a voice channel.",
        "join.missing_guild_id": "This command can only be used in a server.",
        "join.voice_channel_not_found": "Could not find voice channel.",
        "join.voice_connection_failed": "Could not join the channel. Try again.",
        "leave.ok": "Disconnected.",
        "leave.not_connected": "I am not connected to a voice channel.",
        "leave.missing_guild_id": "This command can only be used in a server.",
        "leave.voice_connection_failed": "Error disconnecting: {error_detail}",
        "leave.error": "Error disconnecting.",
        "language.invalid": "❌ Invalid interface language.",
        "language.name.en-US": "English",
        "language.name.pt-BR": "Portuguese",
        "language.user.updated": "✅ Your interface language is now {language_name}.",
        "language.user.automatic": "✅ Your interface will now follow your Discord language.",
        "language.guild.updated": "✅ The server default interface language is now {language_name}.",
        "language.guild.automatic": "✅ Users without a personal language will now follow Discord/server language.",
        "language.update_error": "❌ Error updating the interface language.",
        "server_language.permission": "❌ You need the manage server permission to change the default language.",
    },
}

_COMMAND_TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt-BR": {
        "cmd.join.description": "Faz o bot entrar no seu canal de voz",
        "cmd.leave.description": "Faz o bot sair do canal de voz",
        "cmd.speak.description": "Faz o bot falar o texto informado no canal de voz",
        "cmd.speak.text": "Texto para falar",
        "cmd.speak.voice": "Escolha uma voz apenas para esta fala",
        "cmd.config.description": "Configura suas preferências pessoais de TTS",
        "cmd.config.voice": "Escolha a voz completa que o bot deve usar",
        "cmd.config_reset.description": "Reseta seu override pessoal de voz",
        "cmd.server_config.description": "Configura a voz padrão do servidor",
        "cmd.server_config.voice": "Escolha a voz padrão para usuários sem configuração pessoal",
        "cmd.server_config_reset.description": "Reseta a voz padrão do servidor",
        "cmd.language.description": "Configura o idioma da sua interface",
        "cmd.language.language": "Escolha o idioma da interface",
        "cmd.server_language.description": "Configura o idioma padrão da interface do servidor",
        "cmd.server_language.language": "Escolha o idioma padrão da interface do servidor",
        "cmd.about.description": "Mostra informações e versão do bot",
    },
    "en-US": {
        "cmd.join.description": "Make the bot join your voice channel",
        "cmd.leave.description": "Make the bot leave the voice channel",
        "cmd.speak.description": "Make the bot speak the given text in voice channel",
        "cmd.speak.text": "Text to speak",
        "cmd.speak.voice": "Choose a voice only for this speech",
        "cmd.config.description": "Configure your personal TTS settings",
        "cmd.config.voice": "Choose the full voice the bot should use",
        "cmd.config_reset.description": "Reset your personal voice override",
        "cmd.server_config.description": "Configure the default server voice",
        "cmd.server_config.voice": "Choose the default voice for users without personal settings",
        "cmd.server_config_reset.description": "Reset the default server voice",
        "cmd.language.description": "Configure your interface language",
        "cmd.language.language": "Choose the interface language",
        "cmd.server_language.description": "Configure the server default interface language",
        "cmd.server_language.language": "Choose the server default interface language",
        "cmd.about.description": "Show bot information and version",
    },
}


def normalize_discord_locale(locale: Any) -> str | None:
    """Normalize a Discord locale-like value to a supported message locale."""

    if locale is None:
        return None

    value = getattr(locale, "value", locale)
    normalized = str(value).replace("_", "-").lower()
    if normalized.startswith("pt"):
        return "pt-BR"
    if normalized.startswith("en"):
        return "en-US"
    return None


class DiscordLocaleResolver:
    """Resolve user locale first, then server locale, then the project default."""

    def resolve(self, interaction: discord.Interaction | None) -> str:
        if interaction is None:
            return DEFAULT_LOCALE

        user_locale = normalize_discord_locale(getattr(interaction, "locale", None))
        if user_locale is not None:
            return user_locale

        guild_locale = normalize_discord_locale(getattr(interaction, "guild_locale", None))
        if guild_locale is not None:
            return guild_locale

        return DEFAULT_LOCALE

    def resolve_candidates(self, *locales: object) -> str:
        """Resolve the first supported locale from an ordered candidate list."""

        for locale in locales:
            resolved_locale = normalize_discord_locale(locale)
            if resolved_locale is not None:
                return resolved_locale
        return DEFAULT_LOCALE


class DiscordMessageCatalog:
    """Small in-memory catalog for Discord user-facing text."""

    def text(self, key: str, locale: str | None = None, **values: object) -> str:
        resolved_locale = normalize_discord_locale(locale) or DEFAULT_LOCALE
        template = _MESSAGES.get(resolved_locale, _MESSAGES[DEFAULT_LOCALE]).get(key)
        if template is None:
            template = _MESSAGES[DEFAULT_LOCALE][key]
        return template.format(**values)


class DiscordCommandTranslator(app_commands.Translator):
    """Translate slash-command metadata for Discord-supported locales."""

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContextTypes,
    ) -> str | None:
        del context
        resolved_locale = normalize_discord_locale(locale)
        if resolved_locale is None:
            return None
        return _COMMAND_TRANSLATIONS.get(resolved_locale, {}).get(str(string))


def command_text(key: str) -> app_commands.locale_str:
    """Create a translatable command metadata string."""

    return app_commands.locale_str(key)


def command_translation(locale: str, key: str) -> str:
    """Return the configured command text for tests and explicit defaults."""

    resolved_locale = normalize_discord_locale(locale) or DEFAULT_LOCALE
    return _COMMAND_TRANSLATIONS[resolved_locale][key]


def supported_locales() -> Mapping[str, Mapping[str, str]]:
    """Expose command translations for tests without allowing mutation."""

    return _COMMAND_TRANSLATIONS


def supported_message_locales() -> Mapping[str, Mapping[str, str]]:
    """Expose message translations for tests without allowing mutation."""

    return _MESSAGES
