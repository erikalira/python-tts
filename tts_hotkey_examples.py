#!/usr/bin/env python3
"""
🎯 TTS Hotkey - Exemplo de Configuração Personalizada
Copie este arquivo e modifique para suas necessidades específicas.
"""

# =============================================================================
# 🎨 EXEMPLO: CONFIGURAÇÃO GAMER
# =============================================================================

class Config:
    """Configuração otimizada para gamers e streamers."""
    
    # 🌐 Discord Bot Configuration
    DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
    DISCORD_CHANNEL_ID = "123456789012345678"  # Seu canal de voz preferido
    DISCORD_MEMBER_ID = None                   # Deixe None para detectar automaticamente
    
    # 🎤 TTS Configuration (Otimizado para gaming)
    TTS_ENGINE = "gtts"           # gtts é mais rápido para texto curto
    TTS_LANGUAGE = "pt"           # Português brasileiro
    TTS_VOICE_ID = "roa/pt-br"   # Voz brasileira
    TTS_RATE = 200               # Mais rápido para comunicação gaming
    
    # 🔊 Audio Output (Para streamers)
    TTS_OUTPUT_DEVICE = "CABLE Input (VB-Audio Virtual Cable)"  # OBS Virtual Cable
    
    # ⚨ Gaming Hotkeys (Evita conflitos com jogos)
    TRIGGER_OPEN = "["           # Menos usado em jogos que {
    TRIGGER_CLOSE = "]"          # Menos usado em jogos que }
    
    # 🎨 Interface (Otimizada para gaming)
    SHOW_NOTIFICATIONS = False   # Não atrapalha durante jogos
    CONSOLE_LOGS = True         # Para debug quando necessário
    
    # ⚡ Network (Rápido para comunicação em tempo real)
    REQUEST_TIMEOUT = 5         # Mais rápido, falha mais rápido
    RETRY_ATTEMPTS = 0          # Sem tentativas, ou funciona ou usa local
    
    # 🔐 Advanced
    USER_AGENT = "TTS-Gaming/2.0"
    MAX_TEXT_LENGTH = 100       # Textos curtos para gaming

# =============================================================================
# 💼 EXEMPLO: CONFIGURAÇÃO ESCRITÓRIO
# =============================================================================

class ConfigOffice:
    """Configuração otimizada para ambiente profissional."""
    
    # 🌐 Discord Bot Configuration
    DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
    DISCORD_CHANNEL_ID = None   # Sem canal fixo, mais flexível
    DISCORD_MEMBER_ID = None    
    
    # 🎤 TTS Configuration (Profissional)
    TTS_ENGINE = "gtts"
    TTS_LANGUAGE = "pt"
    TTS_VOICE_ID = "roa/pt-br"
    TTS_RATE = 160              # Mais devagar, mais claro
    
    # 🔊 Audio Output
    TTS_OUTPUT_DEVICE = None    # Usar padrão do sistema
    
    # ⌨️ Office Hotkeys (Não conflita com shortcuts)
    TRIGGER_OPEN = "{"
    TRIGGER_CLOSE = "}"
    
    # 🎨 Interface (Profissional)
    SHOW_NOTIFICATIONS = True   # Útil em ambiente de escritório
    CONSOLE_LOGS = False        # Menos poluição visual
    
    # ⏱️ Network (Mais tolerante)
    REQUEST_TIMEOUT = 15        # Aguarda mais tempo
    RETRY_ATTEMPTS = 2          # Tenta novamente se falhar
    
    # 🔐 Advanced
    USER_AGENT = "TTS-Office/2.0"
    MAX_TEXT_LENGTH = 1000      # Textos mais longos para apresentações

# =============================================================================
# 🎓 INSTRUÇÕES DE USO
# =============================================================================

"""
COMO USAR ESTE ARQUIVO:

1. ESCOLHA SUA CONFIGURAÇÃO:
   - Renomeie 'Config' para 'ConfigGaming' 
   - Renomeie 'ConfigOffice' para 'Config'
   
   OU crie sua própria configuração baseada nos exemplos

2. PERSONALIZE:
   - Edite os valores conforme sua necessidade
   - Adicione novos campos se necessário

3. COMPILE:
   - Execute: build_configurable.ps1
   - Distribua o .exe gerado

4. EXEMPLOS DE PERSONALIZAÇÃO:

   # Para streamers:
   TTS_OUTPUT_DEVICE = "CABLE Input (VB-Audio Virtual Cable)"
   SHOW_NOTIFICATIONS = False
   TTS_RATE = 220
   
   # Para apresentações:
   TTS_RATE = 140
   MAX_TEXT_LENGTH = 2000
   SHOW_NOTIFICATIONS = True
   
   # Para jogos competitivos:
   TRIGGER_OPEN = "["
   TRIGGER_CLOSE = "]" 
   REQUEST_TIMEOUT = 3
   
   # Para idiomas diferentes:
   TTS_LANGUAGE = "en"
   TTS_VOICE_ID = "en-US"

5. TRIGGERS ALTERNATIVOS:
   - Padrão: {texto}
   - Gaming: [texto]
   - Discreto: `texto`
   - Matemático: (texto)
"""

# =============================================================================
# 🚀 CONFIGURAÇÃO ATIVA (EDITE AQUI)
# =============================================================================

# Descomente a linha que você quer usar:
Config = Config          # Configuração gamer
# Config = ConfigOffice  # Configuração escritório

# =============================================================================
# 📋 CÓDIGO DO TTS HOTKEY (NÃO EDITAR ABAIXO DESTA LINHA)
# =============================================================================

# [O resto do código do TTS Hotkey viria aqui...]