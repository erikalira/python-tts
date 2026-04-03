# ðŸŽ¤ TTS Hotkey - ConfiguraÃ§Ã£o AvanÃ§ada

## ðŸ† Desktop App Atual

**Entry point**: `app.py`  
**ExecutÃ¡vel**: `dist/tts_hotkey_clean.exe`

### âœ¨ Discord ID AutomÃ¡tico

O Desktop App usa a configuraÃ§Ã£o persistida para descobrir em qual canal vocÃª estÃ¡.

## ðŸ”§ **Como Descobrir seu Discord ID**

### Passo 1: Ativar Modo Desenvolvedor

1. Discord â†’ **ConfiguraÃ§Ãµes do UsuÃ¡rio**
2. **AvanÃ§ado** â†’ Ativar **Modo Desenvolvedor**

### Passo 2: Copiar seu ID

1. Clique direito no **seu nome** em qualquer chat
2. **Copiar ID do UsuÃ¡rio**
3. Cole na interface de configuraÃ§Ã£o do app

## ðŸŽ¯ **Funcionamento Inteligente**

O bot usa esta **ordem de prioridade**:

1. ðŸŽ¯ **Canal jÃ¡ conectado** (se usou `/join` antes)
2. ðŸ“ **Channel ID especÃ­fico** (se configurou `DISCORD_CHANNEL_ID`)
3. ðŸ‘¤ **Member ID** (encontra onde vocÃª estÃ¡)
4. âŒ **Erro** se nenhuma opÃ§Ã£o funcionar

## ðŸŽ® **ConfiguraÃ§Ãµes por Perfil**

### Perfis sugeridos

- Gaming: taxa de fala mais alta e menos notificaÃ§Ãµes
- Office: taxa mais baixa e timeout maior
- Streaming: canal fixo e menos logs visuais

## âš¡ **Triggers PersonalizÃ¡veis**

Evite conflitos com outros programas:

Escolha uma combinaÃ§Ã£o de abertura/fechamento que nÃ£o conflite com outros programas.

## ðŸ”Š **ConfiguraÃ§Ã£o de Ãudio AvanÃ§ada**

Configure engine, idioma, taxa e dispositivo de Ã¡udio pela interface do Desktop App.

## ðŸ“Š Status

Quando executado, o app mostra logs de inicializaÃ§Ã£o e status dos serviÃ§os do Desktop App.

## ðŸš€ **Compilar e Usar**

```powershell
# 1. Rodar o app
python app.py

# 2. Compilar
./scripts/build/build_clean_architecture.ps1

# 3. Usar
dist/tts_hotkey_clean.exe
```

## ðŸŽ¯ **Modo de Uso**

1. **Entre em um canal de voz** no Discord
2. **Execute o app** (`python app.py` ou o `.exe`)
3. **Aperte sua trigger key** (ex: `{`)
4. **Digite o texto** que quer falar
5. **Aperte a close key** (ex: `}`)
6. **Bot fala automaticamente!**

## ðŸ› ï¸ **Troubleshooting Premium**

### âŒ "Hotkey registration failed"

Mude as hotkeys na interface de configuraÃ§Ã£o do app.

### âŒ "Discord not found"

Verifique a URL do bot na configuraÃ§Ã£o do app ou no `.env`.

### âŒ "Member not found"

Use o ID correto do usuÃ¡rio ou configure um canal fixo na interface do app.

## ðŸ’Ž Vantagens da VersÃ£o Atual

- ðŸŽ¯ Um Ãºnico runtime do Desktop App
- ðŸ“Š ConfiguraÃ§Ã£o persistida
- âš¡ Build dedicado para Windows
- ðŸ”§ Menos caminhos paralelos de execuÃ§Ã£o

**Resultado**: um Ãºnico `.exe` baseado no runtime limpo de `src/desktop`.

