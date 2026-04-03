# TTS Hotkey - Configuracao Avancada

## Desktop App Atual

**Entry point**: `app.py`  
**Executavel**: `dist/tts_hotkey_clean.exe`

### Discord ID Automatico

O Desktop App usa a configuracao persistida para descobrir em qual canal voce esta.

## Como Descobrir seu Discord ID

### Passo 1: Ativar Modo Desenvolvedor

1. Discord -> **Configuracoes do Usuario**
2. **Avancado** -> Ativar **Modo Desenvolvedor**

### Passo 2: Copiar seu ID

1. Clique direito no **seu nome** em qualquer chat
2. **Copiar ID do Usuario**
3. Cole na interface de configuracao do app

## Funcionamento Inteligente

O bot usa esta ordem de prioridade:

1. Canal ja conectado, se voce usou `/join` antes
2. Channel ID especifico, se configurou `DISCORD_CHANNEL_ID`
3. Member ID, para encontrar onde voce esta
4. Erro, se nenhuma opcao funcionar

## Configuracoes por Perfil

### Perfis sugeridos

- Gaming: taxa de fala mais alta e menos notificacoes
- Office: taxa mais baixa e timeout maior
- Streaming: canal fixo e menos logs visuais

## Triggers Personalizaveis

Evite conflitos com outros programas:

Escolha uma combinacao de abertura e fechamento que nao conflite com outros programas.

## Configuracao de Audio Avancada

Configure engine, idioma, taxa e dispositivo de audio pela interface do Desktop App.

## Status

Quando executado, o app mostra logs de inicializacao e status dos servicos do Desktop App.

## Compilar e Usar

```powershell
# 1. Rodar o app
python app.py

# 2. Compilar
./scripts/build/build_clean_architecture.ps1

# 3. Usar
dist/tts_hotkey_clean.exe
```

## Modo de Uso

1. Entre em um canal de voz no Discord
2. Execute o app com `python app.py` ou o `.exe`
3. Aperte sua trigger key, por exemplo `{`
4. Digite o texto que quer falar
5. Aperte a close key, por exemplo `}`
6. O bot fala automaticamente

## Solucao de Problemas

### "Hotkey registration failed"

Mude as hotkeys na interface de configuracao do app.

### "Discord not found"

Verifique a URL do bot na configuracao do app ou no `.env`.

### "Member not found"

Use o ID correto do usuario ou configure um canal fixo na interface do app.

## Vantagens da Versao Atual

- Um unico runtime do Desktop App
- Configuracao persistida
- Build dedicado para Windows
- Menos caminhos paralelos de execucao

**Resultado**: um unico `.exe` baseado no runtime limpo de `src/desktop`.
