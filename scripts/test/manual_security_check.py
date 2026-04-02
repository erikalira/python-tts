#!/usr/bin/env python3
"""
Teste manual da correcao de seguranca do TTS Bot.
Este script simula o cenario de vazamento de informacao identificado.
"""

import asyncio
import sys
import os

# Adicionar a raiz do repositorio ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.application.use_cases import SpeakTextUseCase
from src.core.entities import TTSRequest
from src.infrastructure.audio_queue import InMemoryAudioQueue
from tests.conftest import MockTTSEngine, MockVoiceChannelRepository, MockVoiceChannel, MockConfigRepository


class SecurityTestChannel(MockVoiceChannel):
    """Canal de teste para verificacao de seguranca."""

    def __init__(self, channel_id: int):
        super().__init__()
        self._channel_id = channel_id

    def get_channel_id(self) -> int:
        return self._channel_id


class SecurityTestRepository(MockVoiceChannelRepository):
    """Repository de teste para cenarios de seguranca."""

    def __init__(self):
        # Canal onde o bot está conectado (Canal A - ID 111)
        self.bot_connected_channel = SecurityTestChannel(111)
        self.bot_connected_channel.connected = True

        # Canal onde o usuário está atualmente (Canal B - ID 222)
        self.user_current_channel = SecurityTestChannel(222)

        super().__init__(self.bot_connected_channel)

    async def find_connected_channel(self):
        """Retorna o canal onde o bot está conectado."""
        print(f"[REPOSITORY] Bot conectado no canal {self.bot_connected_channel.get_channel_id()}")
        return self.bot_connected_channel

    async def find_by_member_id(self, member_id: int):
        """Retorna o canal onde o usuário está atualmente."""
        print(f"[REPOSITORY] Usuário {member_id} está no canal {self.user_current_channel.get_channel_id()}")
        return self.user_current_channel


async def test_security_vulnerability():
    """Testa o cenario de vulnerabilidade de seguranca."""

    print("🔒 TESTE DE SEGURANÇA - Vazamento de Informação TTS")
    print("=" * 60)

    # Setup dos mocks
    tts_engine = MockTTSEngine()
    repository = SecurityTestRepository()
    config_repository = MockConfigRepository()
    audio_queue = InMemoryAudioQueue()

    # Criar use case
    use_case = SpeakTextUseCase(
        tts_engine=tts_engine,
        channel_repository=repository,
        config_repository=config_repository,
        audio_queue=audio_queue,
    )

    # Cenario: Usuario solicita TTS
    print("\n📝 CENÁRIO:")
    print("- Bot está conectado no Canal A (ID: 111)")
    print("- Usuário saiu do Canal A e está agora no Canal B (ID: 222)")
    print("- Usuário solicita TTS: 'Informação confidencial'")
    print()

    request = TTSRequest(
        text="Informação confidencial que não deveria vazar",
        member_id=123,
        guild_id=999
    )

    # Executar use case
    print("🚀 EXECUTANDO USE CASE...")
    result = await use_case.execute(request)

    # Verificar resultado
    print("\n📊 RESULTADO:")
    print(f"✅ Sucesso: {result['success']}")
    print(f"📝 Mensagem: {result['message']}")

    # Analisar se houve vazamento
    if result["success"]:
        print("\n❌ FALHA DE SEGURANÇA: TTS foi executado mesmo com usuário em canal diferente!")
        print("   💀 VAZAMENTO DE INFORMAÇÃO CONFIRMADO!")
    else:
        print("\n✅ CORREÇÃO DE SEGURANÇA FUNCIONANDO:")
        print("   🛡️  Bot rejeitou a solicitação por questões de segurança")
        print("   🔒 Informação protegida contra vazamento")

    # Verificar se houve reproducao de audio
    if repository.bot_connected_channel.played_audio:
        print(f"\n⚠️  ÁUDIO REPRODUZIDO NO CANAL ERRADO: {repository.bot_connected_channel.played_audio}")
    else:
        print("\n✅ NENHUM ÁUDIO REPRODUZIDO (correto)")

    print("\n" + "=" * 60)


async def test_security_valid_scenario():
    """Testa cenario valido onde usuario esta no mesmo canal do bot."""

    print("🔓 TESTE CENÁRIO VÁLIDO - Usuário no Canal Correto")
    print("=" * 60)

    # Setup - usuario e bot no mesmo canal
    tts_engine = MockTTSEngine()
    config_repository = MockConfigRepository()
    audio_queue = InMemoryAudioQueue()

    # Repository onde usuário está no mesmo canal do bot
    class ValidRepository(MockVoiceChannelRepository):
        def __init__(self):
            self.shared_channel = SecurityTestChannel(111)
            self.shared_channel.connected = True
            super().__init__(self.shared_channel)

        async def find_connected_channel(self):
            return self.shared_channel

        async def find_by_member_id(self, member_id: int):
            return self.shared_channel

    repository = ValidRepository()

    use_case = SpeakTextUseCase(
        tts_engine=tts_engine,
        channel_repository=repository,
        config_repository=config_repository,
        audio_queue=audio_queue,
    )

    print("\n📝 CENÁRIO:")
    print("- Bot está conectado no Canal A (ID: 111)")
    print("- Usuário também está no Canal A (ID: 111)")
    print("- Usuário solicita TTS: 'Informação válida'")
    print()

    request = TTSRequest(
        text="Informação válida para usuário no canal correto",
        member_id=123,
        guild_id=999
    )

    print("🚀 EXECUTANDO USE CASE...")
    result = await use_case.execute(request)

    print("\n📊 RESULTADO:")
    print(f"✅ Sucesso: {result['success']}")
    print(f"📝 Mensagem: {result['message']}")

    if result["success"]:
        print("\n✅ FUNCIONAMENTO CORRETO:")
        print("   🎵 TTS executado com segurança - usuário no canal correto")
    else:
        print("\n❌ PROBLEMA: TTS foi rejeitado mesmo com usuário no canal correto")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("🤖 TESTE DE SEGURANÇA DO TTS BOT DISCORD")
    print("Verificando correção de vazamento de informação")
    print()

    try:
        asyncio.run(test_security_vulnerability())

        print()

        asyncio.run(test_security_valid_scenario())

        print("\n🎉 TESTES CONCLUÍDOS!")

    except Exception as e:
        print(f"\n❌ ERRO DURANTE TESTE: {e}")
        import traceback
        traceback.print_exc()
