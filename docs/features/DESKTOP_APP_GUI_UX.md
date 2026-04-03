# UX da GUI do Desktop App

Este documento registra requisitos e critÃ©rios de qualidade para a GUI do Desktop App. O objetivo Ã© garantir uma experiÃªncia estÃ¡vel para usuÃ¡rio final sem enfraquecer a arquitetura do projeto.

## Objetivos

- manter a interface responsiva durante toda a interaÃ§Ã£o
- garantir ediÃ§Ã£o confiÃ¡vel dos campos e controles da GUI
- evitar experiÃªncia confusa ao distribuir o programa para outro usuÃ¡rio
- preservar a independÃªncia do Desktop App em relaÃ§Ã£o ao bot
- manter regras de negÃ³cio fora da camada de interface

## Problemas que motivam esta diretriz

- a interface apresenta travamentos intermitentes e cliques inconsistentes
- a GUI do Desktop App nÃ£o permite ediÃ§Ã£o confiÃ¡vel
- a distribuiÃ§Ã£o atual abre terminal e deixa o app na bandeja de forma pouco amigÃ¡vel

## Requisitos de UX

### 1. Responsividade da interface

- cliques devem responder de forma consistente
- operaÃ§Ãµes longas ou bloqueantes nÃ£o podem congelar a thread da interface
- a GUI deve refletir estados transitÃ³rios com feedback claro ao usuÃ¡rio
- handlers de eventos devem ser curtos e delegar trabalho para serviÃ§os ou mecanismos assÃ­ncronos apropriados

### 2. Editabilidade e interaÃ§Ã£o

- campos de texto precisam aceitar foco, seleÃ§Ã£o, digitaÃ§Ã£o, ediÃ§Ã£o e colagem de forma confiÃ¡vel
- componentes desabilitados ou somente leitura devem deixar isso explÃ­cito visualmente
- a interface deve evitar estados em que o usuÃ¡rio acredita poder editar algo, mas a aÃ§Ã£o nÃ£o funciona
- validaÃ§Ãµes devem orientar correÃ§Ã£o sem impedir interaÃ§Ã£o bÃ¡sica

### 3. ExperiÃªncia de distribuiÃ§Ã£o

- a versÃ£o destinada a usuÃ¡rio final nÃ£o deve abrir um terminal junto com a GUI
- comportamento de inicializaÃ§Ã£o em bandeja deve ser intencional, compreensÃ­vel e previsÃ­vel
- se o app iniciar minimizado ou em bandeja, a interface precisa comunicar como abrir, fechar ou sair
- fechar, minimizar e restaurar devem seguir um fluxo consistente

### 4. Clareza de fluxo

- o usuÃ¡rio deve entender rapidamente o estado atual do app
- aÃ§Ãµes principais devem ser visÃ­veis e fÃ¡ceis de descobrir
- mensagens de erro e status devem ser objetivas e acionÃ¡veis
- a GUI deve priorizar tarefas frequentes e reduzir surpresa comportamental

### 5. Fluxo de inicializaÃ§Ã£o e painel principal

- ao abrir o executÃ¡vel, a janela principal deve permanecer aberta
- a primeira tela deve apresentar o app e orientar o usuÃ¡rio sobre os prÃ³ximos passos
- a configuraÃ§Ã£o nÃ£o deve depender de terminal nem de uma janela puramente modal
- a janela principal deve permitir testar a conexÃ£o com o bot antes do uso normal
- a janela principal deve exibir atividade relevante do app, incluindo logs Ãºteis de envio, teste e status

## Requisitos de arquitetura

- lÃ³gica de negÃ³cio nÃ£o deve ser implementada na GUI
- a camada de interface deve apenas capturar eventos, apresentar estado e delegar para casos de uso ou serviÃ§os
- lÃ³gica compartilhÃ¡vel entre o Desktop App e o bot deve ficar em `src/`, nÃ£o duplicada em `src/standalone/`
- integraÃ§Ãµes especÃ­ficas de runtime, janela, tray e toolkit devem permanecer em adapters ou bootstrap do Desktop App
- melhorias de UX devem preferir refactors pequenos e seguros

## Checklist para mudanÃ§as na GUI do Desktop App

Antes de concluir uma alteraÃ§Ã£o na GUI do Desktop App, validar:

- a interface continua clicÃ¡vel e responsiva
- campos editÃ¡veis continuam realmente editÃ¡veis
- nÃ£o hÃ¡ operaÃ§Ã£o bloqueante rodando diretamente na thread principal da GUI
- o fluxo de abrir, minimizar, restaurar e sair estÃ¡ claro
- a execuÃ§Ã£o para usuÃ¡rio final nÃ£o expÃµe terminal desnecessÃ¡rio
- a mudanÃ§a nÃ£o duplicou lÃ³gica entre `src/standalone/` e o restante de `src/`
- a mudanÃ§a nÃ£o moveu regra de negÃ³cio para interface ou infraestrutura

## ValidaÃ§Ã£o recomendada

- iniciar o Desktop App em ambiente local e interagir manualmente com os principais controles
- testar foco, clique, digitaÃ§Ã£o, seleÃ§Ã£o e colagem nos campos editÃ¡veis
- validar inicializaÃ§Ã£o, minimizaÃ§Ã£o para bandeja, restauraÃ§Ã£o e encerramento
- validar comportamento do pacote final voltado a usuÃ¡rio final, especialmente ausÃªncia de terminal desnecessÃ¡rio
- confirmar que bot e Desktop App continuam executando de forma independente

## Quando criar documentaÃ§Ã£o adicional

Se uma mudanÃ§a introduzir:

- novo fluxo de janela ou bandeja
- novo comportamento de empacotamento/distribuiÃ§Ã£o
- nova estratÃ©gia de responsividade da GUI
- novo padrÃ£o de integraÃ§Ã£o entre GUI e casos de uso

entÃ£o a implementaÃ§Ã£o deve ser documentada em um arquivo especÃ­fico adicional dentro de `docs/features/`.
