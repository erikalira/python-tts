# Painel Principal do Desktop App

Esta feature transforma a GUI do Desktop App em um painel principal persistente, em vez de uma janela usada apenas para configuraÃ§Ã£o inicial.

## Objetivo

Dar ao usuÃ¡rio final uma experiÃªncia clara ao abrir o executÃ¡vel:

- a janela principal permanece aberta
- o app se apresenta e orienta o fluxo inicial
- a configuraÃ§Ã£o pode ser salva sem depender de terminal
- a conexÃ£o com o bot pode ser testada manualmente
- um teste curto de envio pode ser disparado sob demanda
- a atividade relevante do app fica visÃ­vel em uma Ã¡rea de logs

## Fluxo esperado

1. O usuÃ¡rio abre `tts_hotkey_clean.exe`
2. O painel principal aparece e permanece visÃ­vel
3. O usuÃ¡rio preenche `Bot URL`, `Guild ID` e `User ID`
4. O usuÃ¡rio clica em `Testar conexÃ£o`
5. O usuÃ¡rio salva a configuraÃ§Ã£o
6. O usuÃ¡rio pode clicar em `Enviar teste de voz` para validar o fluxo manualmente
7. O usuÃ¡rio passa a usar as hotkeys normalmente, mantendo a janela como referÃªncia visual

## Regras de custo e infraestrutura

- nÃ£o hÃ¡ polling contÃ­nuo de conexÃ£o
- a verificaÃ§Ã£o de conexÃ£o ocorre apenas quando o usuÃ¡rio clica em `Testar conexÃ£o`
- o envio de fala de teste ocorre apenas quando o usuÃ¡rio clica em `Enviar teste de voz`
- a mensagem de teste deve ser curta para reduzir custo e ruÃ­do operacional

## IntegraÃ§Ã£o arquitetural

- a GUI apenas coleta dados, mostra estado e delega aÃ§Ãµes
- a checagem de conexÃ£o usa o adapter HTTP do Desktop App
- o envio de teste reutiliza o fluxo HTTP jÃ¡ existente para o bot
- o runtime do Desktop App continua separado do bot, preservando execuÃ§Ã£o independente

## UX implementada

- status visual do app
- status claro de configuraÃ§Ã£o do bot
- status claro do Ãºltimo teste de conexÃ£o/envio
- orientaÃ§Ãµes curtas de uso no prÃ³prio painel
- Ã¡rea de atividade com logs Ãºteis para o usuÃ¡rio
- bandeja usada como atalho secundÃ¡rio, nÃ£o como fluxo principal obrigatÃ³rio

## ValidaÃ§Ã£o manual recomendada

- abrir o executÃ¡vel e confirmar que a janela continua visÃ­vel
- preencher configuraÃ§Ã£o vÃ¡lida e salvar
- testar conexÃ£o com o bot
- enviar mensagem curta de teste
- confirmar atualizaÃ§Ã£o dos logs no painel
- minimizar, restaurar e fechar o app
