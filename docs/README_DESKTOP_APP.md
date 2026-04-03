# Desktop App

Este guia concentra a visão operacional do Desktop App Windows.

## Entry points

- Execução local: `app.py`
- Runtime interno: `src/standalone/`
- Composition root: `src/standalone/app/bootstrap.py`

## Configuração

Use a configuração persistida do Desktop App em `src/standalone/config/desktop_config.py`
e a interface gráfica do próprio app para ajustar Discord, TTS, hotkeys e preferências da interface.

## Ambiente

O ambiente local do projeto é baseado em `.env`.

- o Desktop App usa o `.env` como fonte de variáveis e defaults de ambiente
- valores persistidos em configuração podem coexistir com variáveis definidas no `.env`
- para reproduzir comportamento local e cenários de teste, mantenha o `.env` configurado

## Painel principal

Ao abrir o executável, o usuário vê um painel principal que:

- permanece aberto como janela principal do app
- permite configurar Discord, TTS, hotkeys e preferências de interface
- oferece `Testar conexão` sob demanda, sem polling contínuo
- oferece `Enviar teste de voz` manual com mensagem curta
- exibe atividade e logs úteis sem depender do terminal

## Build

```powershell
python app.py
./scripts/build/build_clean_architecture.ps1
```

## Relacionados

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [features/DESKTOP_APP_MAIN_PANEL.md](features/DESKTOP_APP_MAIN_PANEL.md)
- [features/DESKTOP_APP_GUI_UX.md](features/DESKTOP_APP_GUI_UX.md)
