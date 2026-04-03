# UX da GUI do Desktop App

Este documento registra requisitos e criterios de qualidade para a GUI do Desktop App. O objetivo e garantir uma experiencia estavel para o usuario final sem enfraquecer a arquitetura do projeto.

## Objetivos

- manter a interface responsiva durante toda a interacao
- garantir edicao confiavel dos campos e controles da GUI
- evitar experiencia confusa ao distribuir o programa para outro usuario
- preservar a independencia do Desktop App em relacao ao bot
- manter regras de negocio fora da camada de interface

## Problemas que motivam esta diretriz

- a interface apresenta travamentos intermitentes e cliques inconsistentes
- a GUI do Desktop App nao permite edicao confiavel
- a distribuicao atual abre terminal e deixa o app na bandeja de forma pouco amigavel

## Requisitos de UX

### 1. Responsividade da interface

- cliques devem responder de forma consistente
- operacoes longas ou bloqueantes nao podem congelar a thread da interface
- a GUI deve refletir estados transitorios com feedback claro ao usuario
- handlers de eventos devem ser curtos e delegar trabalho para servicos ou mecanismos assincronos apropriados

### 2. Editabilidade e interacao

- campos de texto precisam aceitar foco, selecao, digitacao, edicao e colagem de forma confiavel
- componentes desabilitados ou somente leitura devem deixar isso explicito visualmente
- a interface deve evitar estados em que o usuario acredita poder editar algo, mas a acao nao funciona
- validacoes devem orientar correcao sem impedir interacao basica

### 3. Experiencia de distribuicao

- a versao destinada ao usuario final nao deve abrir um terminal junto com a GUI
- comportamento de inicializacao em bandeja deve ser intencional, compreensivel e previsivel
- se o app iniciar minimizado ou em bandeja, a interface precisa comunicar como abrir, fechar ou sair
- fechar, minimizar e restaurar devem seguir um fluxo consistente

### 4. Clareza de fluxo

- o usuario deve entender rapidamente o estado atual do app
- acoes principais devem ser visiveis e faceis de descobrir
- mensagens de erro e status devem ser objetivas e acionaveis
- a GUI deve priorizar tarefas frequentes e reduzir surpresa comportamental

### 5. Fluxo de inicializacao e painel principal

- ao abrir o executavel, a janela principal deve permanecer aberta
- a primeira tela deve apresentar o app e orientar o usuario sobre os proximos passos
- a configuracao nao deve depender de terminal nem de uma janela puramente modal
- a janela principal deve permitir testar a conexao com o bot antes do uso normal
- a janela principal deve exibir atividade relevante do app, incluindo logs uteis de envio, teste e status

## Requisitos de arquitetura

- logica de negocio nao deve ser implementada na GUI
- a camada de interface deve apenas capturar eventos, apresentar estado e delegar para casos de uso ou servicos
- logica compartilhavel entre o Desktop App e o bot deve ficar em `src/`, nao duplicada em `src/desktop/`
- integracoes especificas de runtime, janela, tray e toolkit devem permanecer em adapters ou bootstrap do Desktop App
- melhorias de UX devem preferir refactors pequenos e seguros

## Checklist para mudancas na GUI do Desktop App

Antes de concluir uma alteracao na GUI do Desktop App, validar:

- a interface continua clicavel e responsiva
- campos editaveis continuam realmente editaveis
- nao ha operacao bloqueante rodando diretamente na thread principal da GUI
- o fluxo de abrir, minimizar, restaurar e sair esta claro
- a execucao para usuario final nao expoe terminal desnecessario
- a mudanca nao duplicou logica entre `src/desktop/` e o restante de `src/`
- a mudanca nao moveu regra de negocio para interface ou infraestrutura

## Validacao recomendada

- iniciar o Desktop App em ambiente local e interagir manualmente com os principais controles
- testar foco, clique, digitacao, selecao e colagem nos campos editaveis
- validar inicializacao, minimizacao para bandeja, restauracao e encerramento
- validar comportamento do pacote final voltado ao usuario final, especialmente ausencia de terminal desnecessario
- confirmar que bot e Desktop App continuam executando de forma independente

## Quando criar documentacao adicional

Se uma mudanca introduzir:

- novo fluxo de janela ou bandeja
- novo comportamento de empacotamento/distribuicao
- nova estrategia de responsividade da GUI
- novo padrao de integracao entre GUI e casos de uso

entao a implementacao deve ser documentada em um arquivo especifico adicional dentro de `docs/features/`.
