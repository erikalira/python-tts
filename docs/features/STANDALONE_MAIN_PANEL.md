# Painel Principal do Standalone

Esta feature transforma a GUI do standalone em um painel principal persistente, em vez de uma janela usada apenas para configuração inicial.

## Objetivo

Dar ao usuário final uma experiência clara ao abrir o executável:

- a janela principal permanece aberta
- o app se apresenta e orienta o fluxo inicial
- a configuração pode ser salva sem depender de terminal
- a conexão com o bot pode ser testada manualmente
- um teste curto de envio pode ser disparado sob demanda
- a atividade relevante do app fica visível em uma área de logs

## Fluxo esperado

1. O usuário abre `tts_hotkey_clean.exe`
2. O painel principal aparece e permanece visível
3. O usuário preenche `Bot URL`, `Guild ID` e `User ID`
4. O usuário clica em `Testar conexão`
5. O usuário salva a configuração
6. O usuário pode clicar em `Enviar teste de voz` para validar o fluxo manualmente
7. O usuário passa a usar as hotkeys normalmente, mantendo a janela como referência visual

## Regras de custo e infraestrutura

- não há polling contínuo de conexão
- a verificação de conexão ocorre apenas quando o usuário clica em `Testar conexão`
- o envio de fala de teste ocorre apenas quando o usuário clica em `Enviar teste de voz`
- a mensagem de teste deve ser curta para reduzir custo e ruído operacional

## Integração arquitetural

- a GUI apenas coleta dados, mostra estado e delega ações
- a checagem de conexão usa o adapter HTTP do standalone
- o envio de teste reutiliza o fluxo HTTP já existente para o bot
- o runtime standalone continua separado do bot, preservando execução independente

## UX implementada

- status visual do app
- status claro de configuração do bot
- status claro do último teste de conexão/envio
- orientações curtas de uso no próprio painel
- área de atividade com logs úteis para o usuário
- bandeja usada como atalho secundário, não como fluxo principal obrigatório

## Validação manual recomendada

- abrir o executável e confirmar que a janela continua visível
- preencher configuração válida e salvar
- testar conexão com o bot
- enviar mensagem curta de teste
- confirmar atualização dos logs no painel
- minimizar, restaurar e fechar o app
