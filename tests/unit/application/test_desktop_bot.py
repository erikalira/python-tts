from src.application.desktop_bot import (
    CheckDesktopBotConnectionUseCase,
    DESKTOP_BOT_TEST_MESSAGE,
    FetchDesktopBotVoiceContextUseCase,
    SendDesktopBotTestMessageUseCase,
)


class FakeDesktopBotGateway:
    def __init__(
        self,
        *,
        has_bot_url=True,
        has_member_id=True,
        check_connection_result=None,
        send_text_result=True,
        fetch_voice_context_result=None,
        last_error_message=None,
    ):
        self._has_bot_url = has_bot_url
        self._has_member_id = has_member_id
        self._check_connection_result = check_connection_result or {"success": True, "message": "ok"}
        self._send_text_result = send_text_result
        self._fetch_voice_context_result = fetch_voice_context_result or {
            "success": True,
            "message": "Canal detectado: Guild A / Sala 1",
        }
        self._last_error_message = last_error_message
        self.sent_texts = []

    def has_bot_url(self) -> bool:
        return self._has_bot_url

    def has_member_id(self) -> bool:
        return self._has_member_id

    def check_connection(self) -> dict:
        return self._check_connection_result

    def send_text(self, text: str) -> bool:
        self.sent_texts.append(text)
        return self._send_text_result

    def fetch_voice_context(self) -> dict:
        return self._fetch_voice_context_result

    def get_last_error_message(self):
        return self._last_error_message


def test_check_desktop_bot_connection_requires_bot_url():
    gateway = FakeDesktopBotGateway(has_bot_url=False)

    result = CheckDesktopBotConnectionUseCase(gateway).execute()

    assert result == {"success": False, "message": "Bot URL nao configurada"}


def test_send_desktop_bot_test_message_requires_member_id():
    gateway = FakeDesktopBotGateway(has_member_id=False)

    result = SendDesktopBotTestMessageUseCase(gateway).execute()

    assert result == {"success": False, "message": "User ID e necessario para enviar o teste"}


def test_send_desktop_bot_test_message_delegates_to_gateway():
    gateway = FakeDesktopBotGateway(send_text_result=True)

    result = SendDesktopBotTestMessageUseCase(gateway).execute()

    assert result == {"success": True, "message": "Mensagem de teste enviada ao bot com sucesso"}
    assert gateway.sent_texts == [DESKTOP_BOT_TEST_MESSAGE]


def test_send_desktop_bot_test_message_returns_last_error_message():
    gateway = FakeDesktopBotGateway(
        send_text_result=False,
        last_error_message="Bot respondeu HTTP 400: playback failed",
    )

    result = SendDesktopBotTestMessageUseCase(gateway).execute()

    assert result == {"success": False, "message": "Bot respondeu HTTP 400: playback failed"}


def test_fetch_desktop_bot_voice_context_requires_member_id():
    gateway = FakeDesktopBotGateway(has_member_id=False)

    result = FetchDesktopBotVoiceContextUseCase(gateway).execute()

    assert result == {"success": False, "message": "User ID e necessario para detectar o canal"}
