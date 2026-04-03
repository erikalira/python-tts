# UX da GUI do Desktop App

Este documento registra requisitos e critÃƒÂ©rios de qualidade para a GUI do Desktop App. O objetivo ÃƒÂ© garantir uma experiÃƒÂªncia estÃƒÂ¡vel para usuÃƒÂ¡rio final sem enfraquecer a arquitetura do projeto.

## Objetivos

- manter a interface responsiva durante toda a interaÃƒÂ§ÃƒÂ£o
- garantir ediÃƒÂ§ÃƒÂ£o confiÃƒÂ¡vel dos campos e controles da GUI
- evitar experiÃƒÂªncia confusa ao distribuir o programa para outro usuÃƒÂ¡rio
- preservar a independÃƒÂªncia do Desktop App em relaÃƒÂ§ÃƒÂ£o ao bot
- manter regras de negÃƒÂ³cio fora da camada de interface

## Problemas que motivam esta diretriz

- a interface apresenta travamentos intermitentes e cliques inconsistentes
- a GUI do Desktop App nÃƒÂ£o permite ediÃƒÂ§ÃƒÂ£o confiÃƒÂ¡vel
- a distribuiÃƒÂ§ÃƒÂ£o atual abre terminal e deixa o app na bandeja de forma pouco amigÃƒÂ¡vel

## Requisitos de UX

### 1. Responsividade da interface

- cliques devem responder de forma consistente
- operaÃƒÂ§ÃƒÂµes longas ou bloqueantes nÃƒÂ£o podem congelar a thread da interface
- a GUI deve refletir estados transitÃƒÂ³rios com feedback claro ao usuÃƒÂ¡rio
- handlers de eventos devem ser curtos e delegar trabalho para serviÃƒÂ§os ou mecanismos assÃƒÂ­ncronos apropriados

### 2. Editabilidade e interaÃƒÂ§ÃƒÂ£o

- campos de texto precisam aceitar foco, seleÃƒÂ§ÃƒÂ£o, digitaÃƒÂ§ÃƒÂ£o, ediÃƒÂ§ÃƒÂ£o e colagem de forma confiÃƒÂ¡vel
- componentes desabilitados ou somente leitura devem deixar isso explÃƒÂ­cito visualmente
- a interface deve evitar estados em que o usuÃƒÂ¡rio acredita poder editar algo, mas a aÃƒÂ§ÃƒÂ£o nÃƒÂ£o funciona
- validaÃƒÂ§ÃƒÂµes devem orientar correÃƒÂ§ÃƒÂ£o sem impedir interaÃƒÂ§ÃƒÂ£o bÃƒÂ¡sica

### 3. ExperiÃƒÂªncia de distribuiÃƒÂ§ÃƒÂ£o

- a versÃƒÂ£o destinada a usuÃƒÂ¡rio final nÃƒÂ£o deve abrir um terminal junto com a GUI
- comportamento de inicializaÃƒÂ§ÃƒÂ£o em bandeja deve ser intencional, compreensÃƒÂ­vel e previsÃƒÂ­vel
- se o app iniciar minimizado ou em bandeja, a interface precisa comunicar como abrir, fechar ou sair
- fechar, minimizar e restaurar devem seguir um fluxo consistente

### 4. Clareza de fluxo

- o usuÃƒÂ¡rio deve entender rapidamente o estado atual do app
- aÃƒÂ§ÃƒÂµes principais devem ser visÃƒÂ­veis e fÃƒÂ¡ceis de descobrir
- mensagens de erro e status devem ser objetivas e acionÃƒÂ¡veis
- a GUI deve priorizar tarefas frequentes e reduzir surpresa comportamental

### 5. Fluxo de inicializaÃƒÂ§ÃƒÂ£o e painel principal

- ao abrir o executÃƒÂ¡vel, a janela principal deve permanecer aberta
- a primeira tela deve apresentar o app e orientar o usuÃƒÂ¡rio sobre os prÃƒÂ³ximos passos
- a configuraÃƒÂ§ÃƒÂ£o nÃƒÂ£o deve depender de terminal nem de uma janela puramente modal
- a janela principal deve permitir testar a conexÃƒÂ£o com o bot antes do uso normal
- a janela principal deve exibir atividade relevante do app, incluindo logs ÃƒÂºteis de envio, teste e status

## Requisitos de arquitetura

- lÃƒÂ³gica de negÃƒÂ³cio nÃƒÂ£o deve ser implementada na GUI
- a camada de interface deve apenas capturar eventos, apresentar estado e delegar para casos de uso ou serviÃƒÂ§os
- lÃƒÂ³gica compartilhÃƒÂ¡vel entre o Desktop App e o bot deve ficar em `src/`, nÃƒÂ£o duplicada em `src/desktop/`
- integraÃƒÂ§ÃƒÂµes especÃƒÂ­ficas de runtime, janela, tray e toolkit devem permanecer em adapters ou bootstrap do Desktop App
- melhorias de UX devem preferir refactors pequenos e seguros

## Checklist para mudanÃƒÂ§as na GUI do Desktop App

Antes de concluir uma alteraÃƒÂ§ÃƒÂ£o na GUI do Desktop App, validar:

- a interface continua clicÃƒÂ¡vel e responsiva
- campos editÃƒÂ¡veis continuam realmente editÃƒÂ¡veis
- nÃƒÂ£o hÃƒÂ¡ operaÃƒÂ§ÃƒÂ£o bloqueante rodando diretamente na thread principal da GUI
- o fluxo de abrir, minimizar, restaurar e sair estÃƒÂ¡ claro
- a execuÃƒÂ§ÃƒÂ£o para usuÃƒÂ¡rio final nÃƒÂ£o expÃƒÂµe terminal desnecessÃƒÂ¡rio
- a mudanÃƒÂ§a nÃƒÂ£o duplicou lÃƒÂ³gica entre `src/desktop/` e o restante de `src/`
- a mudanÃƒÂ§a nÃƒÂ£o moveu regra de negÃƒÂ³cio para interface ou infraestrutura

## ValidaÃƒÂ§ÃƒÂ£o recomendada

- iniciar o Desktop App em ambiente local e interagir manualmente com os principais controles
- testar foco, clique, digitaÃƒÂ§ÃƒÂ£o, seleÃƒÂ§ÃƒÂ£o e colagem nos campos editÃƒÂ¡veis
- validar inicializaÃƒÂ§ÃƒÂ£o, minimizaÃƒÂ§ÃƒÂ£o para bandeja, restauraÃƒÂ§ÃƒÂ£o e encerramento
- validar comportamento do pacote final voltado a usuÃƒÂ¡rio final, especialmente ausÃƒÂªncia de terminal desnecessÃƒÂ¡rio
- confirmar que bot e Desktop App continuam executando de forma independente

## Quando criar documentaÃƒÂ§ÃƒÂ£o adicional

Se uma mudanÃƒÂ§a introduzir:

- novo fluxo de janela ou bandeja
- novo comportamento de empacotamento/distribuiÃƒÂ§ÃƒÂ£o
- nova estratÃƒÂ©gia de responsividade da GUI
- novo padrÃƒÂ£o de integraÃƒÂ§ÃƒÂ£o entre GUI e casos de uso

entÃƒÂ£o a implementaÃƒÂ§ÃƒÂ£o deve ser documentada em um arquivo especÃƒÂ­fico adicional dentro de `docs/features/`.

