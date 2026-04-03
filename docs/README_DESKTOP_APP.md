# Desktop App

Este guia concentra a visÃ£o operacional do Desktop App Windows.

## Entry points

- ExecuÃ§Ã£o local: `app.py`
- Runtime interno: `src/desktop/`
- Composition root: `src/desktop/app/bootstrap.py`

## ConfiguraÃ§Ã£o

Use a configuraÃ§Ã£o persistida do Desktop App em `src/desktop/config/desktop_config.py`
e a interface grÃ¡fica do prÃ³prio app para ajustar Discord, TTS, hotkeys e preferÃªncias da interface.

## Ambiente

O ambiente local do projeto Ã© baseado em `.env`.

- o Desktop App usa o `.env` como fonte de variÃ¡veis e defaults de ambiente
- valores persistidos em configuraÃ§Ã£o podem coexistir com variÃ¡veis definidas no `.env`
- para reproduzir comportamento local e cenÃ¡rios de teste, mantenha o `.env` configurado

## Painel principal

Ao abrir o executÃ¡vel, o usuÃ¡rio vÃª um painel principal que:

- permanece aberto como janela principal do app
- permite configurar Discord, TTS, hotkeys e preferÃªncias de interface
- oferece `Testar conexÃ£o` sob demanda, sem polling contÃ­nuo
- oferece `Enviar teste de voz` manual com mensagem curta
- exibe atividade e logs Ãºteis sem depender do terminal

## Build

```powershell
python app.py
./scripts/build/build_clean_architecture.ps1
```

## Relacionados

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [features/DESKTOP_APP_MAIN_PANEL.md](features/DESKTOP_APP_MAIN_PANEL.md)
- [features/DESKTOP_APP_GUI_UX.md](features/DESKTOP_APP_GUI_UX.md)

