# Painel Principal do Desktop App

Esta feature transforma a GUI do Desktop App em um painel principal persistente, em vez de uma janela usada apenas para configuracao inicial.

## Objetivo

Dar ao usuario final uma experiencia clara ao abrir o executavel:

- a janela principal permanece aberta
- o app se apresenta e orienta o fluxo inicial
- a configuracao pode ser salva sem depender de terminal
- a conexao com o bot pode ser testada manualmente
- um teste curto de envio pode ser disparado sob demanda
- a atividade relevante do app fica visivel em uma area de logs

## Fluxo esperado

1. O usuario abre `HotkeyTTS.exe`
2. O painel principal aparece e permanece visivel
3. O usuario preenche `Bot URL` e `User ID`
4. O usuario clica em `Testar conexao`
5. O usuario pode clicar em `Recarregar canal detectado` para ver qual servidor e canal de voz o bot encontrou
6. O usuario salva a configuracao
7. O usuario pode clicar em `Enviar teste de voz` para validar o fluxo manualmente
8. O usuario passa a usar as hotkeys normalmente, mantendo a janela como referencia visual

## Regras de custo e infraestrutura

- nao ha polling continuo de conexao
- a verificacao de conexao ocorre apenas quando o usuario clica em `Testar conexao`
- a deteccao de servidor/canal ocorre apenas quando o usuario clica em `Recarregar canal detectado`
- o envio de fala de teste ocorre apenas quando o usuario clica em `Enviar teste de voz`
- a mensagem de teste deve ser curta para reduzir custo e ruido operacional

## Integracao arquitetural

- a GUI apenas coleta dados, mostra estado e delega acoes
- a checagem de conexao usa o adapter HTTP do Desktop App
- a deteccao de canal atual usa um endpoint HTTP dedicado do bot
- o envio de teste reutiliza o fluxo HTTP ja existente para o bot
- o runtime do Desktop App continua separado do bot, preservando execucao independente

## UX implementada

- status visual do app
- status claro de configuracao do bot
- status claro do servidor/canal de voz detectados para o usuario configurado
- status claro do ultimo teste de conexao e envio
- orientacoes curtas de uso no proprio painel
- area de atividade com logs uteis para o usuario
- bandeja usada como atalho secundario, nao como fluxo principal obrigatorio

## Validacao manual recomendada

- abrir o executavel e confirmar que a janela continua visivel
- preencher configuracao valida e salvar
- testar conexao com o bot
- recarregar o canal detectado e verificar servidor/canal exibidos
- enviar mensagem curta de teste
- confirmar atualizacao dos logs no painel
- minimizar, restaurar e fechar o app
