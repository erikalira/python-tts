#!/usr/bin/env python3
"""
Teste manual simples da correção de segurança do TTS Bot.
"""

import asyncio
import sys
import os
from typing import Optional

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.application.use_cases import SpeakTextUseCase
from src.core.entities import TTSRequest, TTSConfig, AudioFile
from src.core.interfaces import ITTSEngine, IVoiceChannel, IVoiceChannelRepository, IConfigRepository

class MockTTSEngine(ITTSEngine):
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        return AudioFile(path="/tmp/mock_audio.wav")

class MockVoiceChannel(IVoiceChannel):
    def __init__(self, channel_id: int):
        self._channel_id = channel_id
        self.connected = False
        self.played_audio = []
    
    async def connect(self) -> None:
        self.connected = True
    
    async def disconnect(self) -> None:
        self.connected = False
    
    async def play_audio(self, audio: AudioFile) -> None:
        if not self.connected:
            raise RuntimeError("Not connected")
        self.played_audio.append(audio.path)
    
    def is_connected(self) -> bool:
        return self.connected
    
    def get_channel_id(self) -> int:
        return self._channel_id

class MockConfigRepository(IConfigRepository):
    def get_config(self, user_id: Optional[int] = None) -> TTSConfig:
        return TTSConfig(engine='gtts', language='pt', voice_id='roa/pt-br', rate=180)
    
    def set_config(self, user_id: int, config: TTSConfig) -> None:
        pass

class SecurityTestRepository(IVoiceChannelRepository):
    def __init__(self):
        # Canal onde o bot está conectado (Canal A - ID 111)  
        self.bot_channel = MockVoiceChannel(111)
        self.bot_channel.connected = True
        
        # Canal onde o usuário está (Canal B - ID 222)
        self.user_channel = MockVoiceChannel(222)
    
    async def find_connected_channel(self) -> Optional[IVoiceChannel]:
        return self.bot_channel
    
    async def find_by_member_id(self, member_id: int) -> Optional[IVoiceChannel]:
        return self.user_channel
    
    async def find_by_channel_id(self, channel_id: int) -> Optional[IVoiceChannel]:
        return None
    
    async def find_by_guild_id(self, guild_id: Optional[int]) -> Optional[IVoiceChannel]:
        return None

async def test_security_vulnerability():
    """Testa o cenário de vulnerabilidade de segurança."""
    
    print("🔒 TESTE DE SEGURANÇA - Vazamento de Informação TTS")
    print("=" * 60)
    
    # Setup
    repository = SecurityTestRepository()
    use_case = SpeakTextUseCase(
        tts_engine=MockTTSEngine(),
        channel_repository=repository,
        config_repository=MockConfigRepository()
    )
    
    print("\n📝 CENÁRIO:")
    print("- Bot conectado no Canal A (ID: 111)")
    print("- Usuário atual no Canal B (ID: 222)")  
    print("- Usuário solicita TTS: 'Informação confidencial'")
    
    request = TTSRequest(
        text="Informação confidencial",
        member_id=123,
        guild_id=999
    )
    
    print("\n🚀 EXECUTANDO...")
    result = await use_case.execute(request)
    
    print(f"\n📊 RESULTADO:")
    print(f"Sucesso: {result['success']}")
    print(f"Mensagem: {result['message']}")
    
    if result["success"]:
        print("\n❌ FALHA DE SEGURANÇA! TTS executado com usuário em canal diferente!")
        return False
    else:
        print("\n✅ SEGURANÇA OK! Bot rejeitou solicitação por questões de segurança")
        return True

async def test_valid_scenario():
    """Testa cenário válido - usuário no mesmo canal."""
    
    print("\n🔓 TESTE CENÁRIO VÁLIDO")
    print("=" * 60)
    
    class ValidRepository(IVoiceChannelRepository):
        def __init__(self):
            # Ambos no mesmo canal
            self.channel = MockVoiceChannel(111) 
            self.channel.connected = True
        
        async def find_connected_channel(self):
            return self.channel
        
        async def find_by_member_id(self, member_id: int):
            return self.channel  # Mesmo canal!
        
        async def find_by_channel_id(self, channel_id: int):
            return None
        
        async def find_by_guild_id(self, guild_id: Optional[int]):
            return None
    
    repository = ValidRepository()
    use_case = SpeakTextUseCase(
        tts_engine=MockTTSEngine(),
        channel_repository=repository,
        config_repository=MockConfigRepository()
    )
    
    print("\n📝 CENÁRIO:")
    print("- Bot conectado no Canal A (ID: 111)")
    print("- Usuário também no Canal A (ID: 111)")
    
    request = TTSRequest(
        text="Informação válida",
        member_id=123,
        guild_id=999
    )
    
    print("\n🚀 EXECUTANDO...")
    result = await use_case.execute(request)
    
    print(f"\n📊 RESULTADO:")
    print(f"Sucesso: {result['success']}")
    print(f"Mensagem: {result['message']}")
    
    if result["success"]:
        print("\n✅ FUNCIONAMENTO OK! TTS executado com usuário no canal correto")
        return True
    else:
        print("\n❌ PROBLEMA: TTS rejeitado mesmo com usuário no canal correto")
        return False

if __name__ == "__main__":
    print("🤖 TESTE DE SEGURANÇA TTS BOT")
    print("Verificando correção de vazamento de informação\n")
    
    try:
        # Teste vulnerabilidade
        vuln_ok = asyncio.run(test_security_vulnerability())
        
        # Teste cenário válido
        valid_ok = asyncio.run(test_valid_scenario())
        
        print("\n" + "=" * 60)
        print("🎯 RESUMO DOS TESTES:")
        print(f"🔒 Proteção contra vazamento: {'✅ PASSOU' if vuln_ok else '❌ FALHOU'}")
        print(f"✅ Cenário válido funciona: {'✅ PASSOU' if valid_ok else '❌ FALHOU'}")
        
        if vuln_ok and valid_ok:
            print("\n🎉 TODOS OS TESTES PASSARAM! Correção de segurança implementada com sucesso!")
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM! Revisar implementação.")
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()