# Desktop App

Este guia concentra a visao operacional do Desktop App Windows.

## Entry points

- Execucao local: `app.py`
- Runtime interno: `src/desktop/`
- Composition root: `src/desktop/app/bootstrap.py`

## Configuracao

Use a configuracao persistida do Desktop App em `src/desktop/config/desktop_config.py`
e a interface grafica do proprio app para ajustar Discord, TTS, hotkeys e preferencias da interface.

## Ambiente

O ambiente local do projeto e baseado em `.env`.

- o Desktop App usa o `.env` como fonte de variaveis e defaults de ambiente
- valores persistidos em configuracao podem coexistir com variaveis definidas no `.env`
- para reproduzir comportamento local e cenarios de teste, mantenha o `.env` configurado

## Painel principal

Ao abrir o executavel, o usuario ve um painel principal que:

- permanece aberto como janela principal do app
- permite configurar Discord, TTS, hotkeys e preferencias de interface
- oferece `Testar conexao` sob demanda, sem polling continuo
- oferece `Enviar teste de voz` manual com mensagem curta
- exibe atividade e logs uteis sem depender do terminal

## Build

```powershell
python app.py
./scripts/build/build_clean_architecture.ps1
```

## Relacionados

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [features/DESKTOP_APP_MAIN_PANEL.md](features/DESKTOP_APP_MAIN_PANEL.md)
- [features/DESKTOP_APP_GUI_UX.md](features/DESKTOP_APP_GUI_UX.md)
