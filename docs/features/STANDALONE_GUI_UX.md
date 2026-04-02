# UX da GUI do Desktop App

Este documento registra requisitos e critérios de qualidade para a GUI do Desktop App. O objetivo é garantir uma experiência estável para usuário final sem enfraquecer a arquitetura do projeto.

## Objetivos

- manter a interface responsiva durante toda a interação
- garantir edição confiável dos campos e controles da GUI
- evitar experiência confusa ao distribuir o programa para outro usuário
- preservar a independência do Desktop App em relação ao bot
- manter regras de negócio fora da camada de interface

## Problemas que motivam esta diretriz

- a interface apresenta travamentos intermitentes e cliques inconsistentes
- a GUI do Desktop App não permite edição confiável
- a distribuição atual abre terminal e deixa o app na bandeja de forma pouco amigável

## Requisitos de UX

### 1. Responsividade da interface

- cliques devem responder de forma consistente
- operações longas ou bloqueantes não podem congelar a thread da interface
- a GUI deve refletir estados transitórios com feedback claro ao usuário
- handlers de eventos devem ser curtos e delegar trabalho para serviços ou mecanismos assíncronos apropriados

### 2. Editabilidade e interação

- campos de texto precisam aceitar foco, seleção, digitação, edição e colagem de forma confiável
- componentes desabilitados ou somente leitura devem deixar isso explícito visualmente
- a interface deve evitar estados em que o usuário acredita poder editar algo, mas a ação não funciona
- validações devem orientar correção sem impedir interação básica

### 3. Experiência de distribuição

- a versão destinada a usuário final não deve abrir um terminal junto com a GUI
- comportamento de inicialização em bandeja deve ser intencional, compreensível e previsível
- se o app iniciar minimizado ou em bandeja, a interface precisa comunicar como abrir, fechar ou sair
- fechar, minimizar e restaurar devem seguir um fluxo consistente

### 4. Clareza de fluxo

- o usuário deve entender rapidamente o estado atual do app
- ações principais devem ser visíveis e fáceis de descobrir
- mensagens de erro e status devem ser objetivas e acionáveis
- a GUI deve priorizar tarefas frequentes e reduzir surpresa comportamental

### 5. Fluxo de inicialização e painel principal

- ao abrir o executável, a janela principal deve permanecer aberta
- a primeira tela deve apresentar o app e orientar o usuário sobre os próximos passos
- a configuração não deve depender de terminal nem de uma janela puramente modal
- a janela principal deve permitir testar a conexão com o bot antes do uso normal
- a janela principal deve exibir atividade relevante do app, incluindo logs úteis de envio, teste e status

## Requisitos de arquitetura

- lógica de negócio não deve ser implementada na GUI
- a camada de interface deve apenas capturar eventos, apresentar estado e delegar para casos de uso ou serviços
- lógica compartilhável entre o Desktop App e o bot deve ficar em `src/`, não duplicada em `src/standalone/`
- integrações específicas de runtime, janela, tray e toolkit devem permanecer em adapters ou bootstrap do Desktop App
- melhorias de UX devem preferir refactors pequenos e seguros

## Checklist para mudanças na GUI do Desktop App

Antes de concluir uma alteração na GUI do Desktop App, validar:

- a interface continua clicável e responsiva
- campos editáveis continuam realmente editáveis
- não há operação bloqueante rodando diretamente na thread principal da GUI
- o fluxo de abrir, minimizar, restaurar e sair está claro
- a execução para usuário final não expõe terminal desnecessário
- a mudança não duplicou lógica entre `src/standalone/` e o restante de `src/`
- a mudança não moveu regra de negócio para interface ou infraestrutura

## Validação recomendada

- iniciar o Desktop App em ambiente local e interagir manualmente com os principais controles
- testar foco, clique, digitação, seleção e colagem nos campos editáveis
- validar inicialização, minimização para bandeja, restauração e encerramento
- validar comportamento do pacote final voltado a usuário final, especialmente ausência de terminal desnecessário
- confirmar que bot e Desktop App continuam executando de forma independente

## Quando criar documentação adicional

Se uma mudança introduzir:

- novo fluxo de janela ou bandeja
- novo comportamento de empacotamento/distribuição
- nova estratégia de responsividade da GUI
- novo padrão de integração entre GUI e casos de uso

então a implementação deve ser documentada em um arquivo específico adicional dentro de `docs/features/`.
