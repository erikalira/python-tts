"""Discord-specific presentation mapping for typed application results."""

from __future__ import annotations

from src.application.dto import (
    JOIN_RESULT_MISSING_GUILD_ID,
    JOIN_RESULT_OK,
    JOIN_RESULT_USER_NOT_IN_CHANNEL,
    JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND,
    JOIN_RESULT_VOICE_CONNECTION_FAILED,
    LEAVE_RESULT_MISSING_GUILD_ID,
    LEAVE_RESULT_NOT_CONNECTED,
    LEAVE_RESULT_OK,
    LEAVE_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_CROSS_GUILD_CHANNEL,
    SPEAK_RESULT_GENERATION_TIMEOUT,
    SPEAK_RESULT_MISSING_GUILD_ID,
    SPEAK_RESULT_MISSING_TEXT,
    SPEAK_RESULT_PLAYBACK_TIMEOUT,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_UNKNOWN_ERROR,
    SPEAK_RESULT_USER_LEFT_CHANNEL,
    SPEAK_RESULT_USER_NOT_IN_CHANNEL,
    SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
    SPEAK_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_VOICE_PERMISSION_DENIED,
    JoinVoiceChannelResult,
    LeaveVoiceChannelResult,
    SpeakTextResult,
)


class DiscordSpeakPresenter:
    """Map speak results to Discord-facing messages."""

    def build_message(self, result: SpeakTextResult) -> str:
        code = result.code
        if code == SPEAK_RESULT_QUEUED:
            position = (result.position or 0) + 1
            queue_size = result.queue_size or position
            return f"Sua mensagem esta na **fila** (posicao **{position}**/{queue_size}). Sera reproduzida em breve!"
        if code == SPEAK_RESULT_MISSING_TEXT:
            return "Texto nao informado."
        if code == SPEAK_RESULT_USER_NOT_IN_CHANNEL:
            return "Voce nao esta em nenhuma sala de voz. Entre em uma sala e tente novamente."
        if code == SPEAK_RESULT_QUEUE_FULL:
            return "Fila de audio cheia. Tente novamente mais tarde."
        if code == SPEAK_RESULT_MISSING_GUILD_ID:
            return "Erro: Nao foi possivel determinar o servidor."
        if code == SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND:
            return "Bot nao conseguiu encontrar sua sala de voz."
        if code == SPEAK_RESULT_CROSS_GUILD_CHANNEL:
            return "Canal de voz pertence a servidor diferente."
        if code == SPEAK_RESULT_USER_LEFT_CHANNEL:
            return "Voce saiu do canal de voz."
        if code == SPEAK_RESULT_GENERATION_TIMEOUT:
            return "Tempo limite excedido durante geracao do audio."
        if code == SPEAK_RESULT_PLAYBACK_TIMEOUT:
            return "Tempo limite excedido durante reproducao."
        if code == SPEAK_RESULT_VOICE_CONNECTION_FAILED:
            return "Bot nao conseguiu se conectar ao canal."
        if code == SPEAK_RESULT_VOICE_PERMISSION_DENIED:
            return "Bot nao tem permissao neste canal."
        if code == SPEAK_RESULT_UNKNOWN_ERROR:
            return "Erro ao reproduzir audio."
        return "Erro inesperado ao processar audio."


class DiscordJoinPresenter:
    """Map join results to Discord messages."""

    def build_message(self, result: JoinVoiceChannelResult) -> str:
        if result.code == JOIN_RESULT_OK:
            return "Joined your channel."
        if result.code == JOIN_RESULT_USER_NOT_IN_CHANNEL:
            return "You are not connected to a voice channel."
        if result.code == JOIN_RESULT_MISSING_GUILD_ID:
            return "Este comando so pode ser usado em um servidor."
        if result.code == JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND:
            return "Could not find voice channel."
        if result.code == JOIN_RESULT_VOICE_CONNECTION_FAILED:
            return "Nao foi possivel entrar no canal. Tente novamente."
        return "Nao foi possivel entrar no canal. Tente novamente."


class DiscordLeavePresenter:
    """Map leave results to Discord messages."""

    def build_message(self, result: LeaveVoiceChannelResult) -> str:
        if result.code == LEAVE_RESULT_OK:
            return "Disconnected."
        if result.code == LEAVE_RESULT_NOT_CONNECTED:
            return "I am not connected to a voice channel."
        if result.code == LEAVE_RESULT_MISSING_GUILD_ID:
            return "Este comando so pode ser usado em um servidor."
        if result.code == LEAVE_RESULT_VOICE_CONNECTION_FAILED and result.error_detail:
            return f"Error disconnecting: {result.error_detail}"
        return "Error disconnecting."
