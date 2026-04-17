# Desktop App Guide

Este guia concentra a visao operacional do Desktop App Windows.

## Entry points

- Execucao local: `app.py`
- Runtime interno: `src/desktop/`
- Composition root: `src/desktop/app/bootstrap.py`

## Configuracao

Use a configuracao persistida do Desktop App em `src/desktop/config/desktop_config.py`
e a interface grafica do proprio app para ajustar Discord, TTS, hotkeys e preferencias da interface.

O fluxo principal do Desktop App e enviar o texto capturado para o bot do Discord.
A voz local do Windows com `pyttsx3` continua disponivel apenas como recurso opcional
de acessibilidade/fallback e fica desativada por padrao.

### Discord ID

O Desktop App pode usar o ID do usuario para descobrir em qual canal de voz
voce esta.

Para copiar esse ID no Discord:

1. Abra `Configuracoes do Usuario`
2. Em `Avancado`, ative `Modo Desenvolvedor`
3. Clique com o botao direito no seu nome em qualquer chat
4. Escolha `Copiar ID do Usuario`
5. Cole o valor na interface de configuracao do app

### Hotkeys

Prefira combinacoes que:

- nao conflitem com atalhos globais do Windows
- nao conflitem com atalhos frequentes de editores, browsers, Discord ou OBS
- sejam faceis de lembrar
- sejam confortaveis para abrir e fechar a captura

Se a sua configuracao usa tecla de abertura e tecla de fechamento, escolha um
par que fique facil de reconhecer durante a digitacao.

O fluxo padrao de uso e:

1. entrar em um canal de voz no Discord
2. abrir o Desktop App
3. acionar a hotkey de abertura
4. digitar o texto
5. acionar a hotkey de fechamento
6. deixar o texto seguir para o bot

Quando o app depende do bot para falar, o fluxo usa esta ordem de prioridade
para descobrir o canal:

1. canal ja conectado, se voce usou `/join` antes
2. ID do usuario para localizar o canal de voz atual
3. erro se nenhuma estrategia funcionar

## Ambiente

O ambiente local do projeto e baseado em `.env`.

- o Desktop App usa o `.env` como fonte de variaveis e defaults de ambiente
- valores persistidos em configuracao podem coexistir com variaveis definidas no `.env`
- para reproduzir comportamento local e cenarios de teste, mantenha o `.env` configurado

## Painel principal

Ao abrir o executavel, o usuario ve um painel principal que:

- permanece aberto como janela principal do app
- permite configurar Discord, TTS, hotkeys e preferencias de interface
- deixa explicito quando a voz local opcional do Windows esta ativada
- oferece `Testar conexao` sob demanda, sem polling continuo
- oferece `Enviar teste de voz` manual com mensagem curta
- exibe atividade e logs uteis sem depender do terminal

## Diretrizes de UX

O Desktop App deve manter uma experiencia previsivel para o usuario final:

- a interface deve permanecer responsiva durante interacoes comuns
- handlers da GUI nao devem bloquear a thread principal com trabalho longo
- campos editaveis devem aceitar foco, selecao, digitacao e colagem de forma confiavel
- estados somente leitura ou desabilitados devem ficar claros visualmente
- a janela principal deve orientar o fluxo inicial sem depender de terminal
- minimizar, restaurar e sair devem seguir um fluxo consistente
- a GUI deve coletar dados e delegar acoes, sem absorver regra de negocio

## Build

```powershell
python app.py
./scripts/build/build_clean_architecture.ps1
```

## Relacionados

- [../architecture/ARCHITECTURE.md](../architecture/ARCHITECTURE.md)
- [../architecture/BOT_DESKTOP_HTTP_CONTRACT.md](../architecture/BOT_DESKTOP_HTTP_CONTRACT.md)
