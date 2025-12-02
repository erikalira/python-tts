# Windows Executable Build Guide

Este guia ajuda a criar executáveis Windows funcionais para o projeto Python TTS.

## 🎯 Problemas Identificados e Soluções

### Problema Principal

Os scripts de build anteriores tentavam compilar arquivos inexistentes ou no local errado.

### ✅ Soluções Implementadas

1. **Script Corrigido**: `build_hotkey_exe.ps1`

   - Compila o arquivo correto: `tts_hotkey_configurable.py`
   - Inclui todas as dependências necessárias
   - Cria executable funcional para Windows

2. **Comandos Make Simplificados**:
   ```bash
   make build-windows    # Build rápido para Windows
   make build-hotkey     # Build específico do TTS Hotkey
   make build-exe        # Build do Discord bot
   ```

## 🚀 Como Compilar no Windows

### Método 1: Usando Make (Recomendado)

```bash
# Build rápido (método mais simples)
make build-windows

# Ou especificamente para TTS Hotkey
make build-hotkey
```

### Método 2: PowerShell Direto

```powershell
# Execute no PowerShell
.\scripts\build\build_hotkey_exe.ps1
```

### Método 3: Manual (Fallback)

```bash
# Instalar dependências
pip install -r requirements.txt
pip install pyinstaller

# Compilar
python -m PyInstaller --onefile --console --name=tts_hotkey --hidden-import=requests --hidden-import=keyboard --hidden-import=pyttsx3 --hidden-import=gtts --hidden-import=pygame --hidden-import=pystray --hidden-import=PIL tts_hotkey_configurable.py
```

## 📁 Arquivos Gerados

Após a compilação bem-sucedida, você terá:

```
dist/
└── tts_hotkey.exe          # Executável principal

run_tts_hotkey.bat          # Script para execução fácil
```

## 🔧 Funcionalidades do Executável

- ✅ **Standalone**: Não precisa Python instalado
- ✅ **Configuração embutida**: Settings no próprio código
- ✅ **TTS engines**: Suporte a gtts e pyttsx3
- ✅ **Hotkeys**: Sistema de atalhos funcionando
- ✅ **Discord integration**: Conexão com bot Discord
- ✅ **System tray**: Ícone na bandeja do sistema

## 🐛 Troubleshooting

### Erro: "Arquivo não encontrado"

**Causa**: Script tentando compilar arquivo inexistente
**Solução**: Use o novo script `build_hotkey_exe.ps1`

### Erro: "PyInstaller não encontrado"

**Causa**: PyInstaller não instalado
**Solução**:

```bash
pip install pyinstaller
```

### Erro: "Dependências em falta"

**Causa**: Módulos necessários não foram incluídos
**Solução**: O novo script inclui todos os `--hidden-import` necessários

### Executável não funciona no Windows

**Causas possíveis**:

1. Faltam DLLs do sistema
2. Antivírus bloqueando
3. Dependências não incluídas

**Soluções**:

1. Execute o `.exe` via prompt de comando para ver erros
2. Adicione exceção no antivírus
3. Use o script `build_hotkey_exe.ps1` que inclui todas as dependências

### "ModuleNotFoundError" ao executar

**Causa**: Dependência não foi incluída no build
**Solução**: Adicione `--hidden-import=nome_do_modulo` no script de build

## 🎯 Teste do Executável

1. **Teste básico**:

   ```cmd
   dist\tts_hotkey.exe
   ```

2. **Teste com batch**:

   ```cmd
   run_tts_hotkey.bat
   ```

3. **Verificar funcionamento**:
   - ✅ Aplicação inicia sem erros
   - ✅ Sistema tray aparece
   - ✅ Hotkeys funcionam
   - ✅ TTS gera áudio
   - ✅ Conexão Discord (se configurada)

## 🔍 Debug do Executável

Para identificar problemas:

1. **Execute via CMD**:

   ```cmd
   cd dist
   tts_hotkey.exe
   ```

   Isso mostrará erros no console.

2. **Verificar logs**:
   O aplicativo pode gerar logs que ajudam a identificar problemas.

3. **Teste incremental**:
   - Primeiro teste sem Discord (configuração local)
   - Depois teste conexão Discord
   - Por último teste todas as funcionalidades

## ✅ Checklist de Build Bem-Sucedido

- [ ] Script roda sem erros
- [ ] Arquivo `dist/tts_hotkey.exe` é criado
- [ ] Tamanho do executável é razoável (>10MB, <100MB)
- [ ] Executável roda no Windows de destino
- [ ] Funcionalidades básicas funcionam
- [ ] Não há erros críticos no console

## 📝 Próximos Passos

Após build bem-sucedido:

1. **Teste em máquina limpa**: Teste em Windows sem Python
2. **Distribuição**: Compartilhe apenas o arquivo `.exe`
3. **Documentação**: Crie manual do usuário se necessário
4. **Atualizações**: Para mudanças, recompile e redistribua

## 🆘 Se Ainda Não Funcionar

Se mesmo com as correções o executável não funcionar:

1. **Verifique o arquivo base**: Teste `python tts_hotkey_configurable.py` primeiro
2. **Use modo debug**: Compile com `--console` para ver erros
3. **Teste dependências**: Instale manualmente cada dependência
4. **Ambiente limpo**: Teste em venv novo
5. **Plataforma específica**: Compile na máquina Windows de destino

## 🔗 Links Úteis

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [Windows Executable Troubleshooting](https://pyinstaller.readthedocs.io/en/stable/when-things-go-wrong.html)
- [Python TTS Project Documentation](docs/README.md)
