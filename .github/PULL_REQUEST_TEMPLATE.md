## 📝 Descrição

<!-- Descreva o que este PR faz e por quê -->

## 🎯 Tipo de Mudança

- [ ] 🐛 Bug fix (correção de bug)
- [ ] ✨ New feature (nova funcionalidade)
- [ ] 🔨 Refactoring (refatoração sem mudar funcionalidade)
- [ ] 📚 Documentation (apenas documentação)
- [ ] 🧪 Tests (adição/correção de testes)
- [ ] 🚀 Performance (melhoria de performance)

## ✅ Checklist de Arquitetura

### Clean Architecture

- [ ] ✅ Código está na camada correta (Domain/Application/Infrastructure/Presentation)
- [ ] ✅ Dependências apontam para dentro (camadas externas → internas)
- [ ] ✅ Não há import circular
- [ ] ✅ Domain Layer não depende de nada externo (puro Python)
- [ ] ✅ Application Layer não depende diretamente de Infrastructure

### SOLID Principles

#### Single Responsibility Principle (SRP)

- [ ] ✅ Cada classe tem uma única responsabilidade
- [ ] ✅ Métodos fazem apenas uma coisa
- [ ] ✅ Não há "god classes" com múltiplas responsabilidades

#### Open/Closed Principle (OCP)

- [ ] ✅ Novo código não modifica classes existentes
- [ ] ✅ Extensões são feitas via herança/composição, não modificação

#### Liskov Substitution Principle (LSP)

- [ ] ✅ Implementações respeitam contratos das interfaces
- [ ] ✅ Subclasses podem substituir classes base sem quebrar funcionalidade

#### Interface Segregation Principle (ISP)

- [ ] ✅ Interfaces são pequenas e focadas
- [ ] ✅ Nenhuma classe é forçada a implementar métodos que não usa

#### Dependency Inversion Principle (DIP)

- [ ] ✅ Use cases dependem de interfaces (abstrações)
- [ ] ✅ Não há dependência direta de implementações concretas
- [ ] ✅ Dependency Injection é usado corretamente

## 🧪 Testes

- [ ] ✅ Testes unitários adicionados/atualizados
- [ ] ✅ Todos os testes passam localmente (`pytest`)
- [ ] ✅ Coverage mantém ou melhora (mínimo 77%)
- [ ] ✅ Mocks usam interfaces, não implementações concretas

## 📚 Documentação

- [ ] ✅ Docstrings adicionadas/atualizadas
- [ ] ✅ Type hints em todos os métodos públicos
- [ ] ✅ README.md atualizado (se necessário)
- [ ] ✅ docs/ARCHITECTURE.md atualizado (se mudou arquitetura)
- [ ] ✅ Comentários explicam "por quê", não "o quê"

## 🎨 Código Limpo

- [ ] ✅ Nomes descritivos (classes, métodos, variáveis)
- [ ] ✅ Métodos pequenos (máximo ~20 linhas)
- [ ] ✅ Sem código comentado ou debug prints
- [ ] ✅ Sem imports não utilizados
- [ ] ✅ Formatação consistente

## 🔍 Revisão de Camadas

### Se modificou `src/core/` (Domain):

- [ ] ✅ Apenas entidades puras ou interfaces
- [ ] ✅ Sem dependências externas (sem imports de libraries externas)
- [ ] ✅ Sem lógica de infraestrutura ou apresentação

### Se modificou `src/application/` (Application):

- [ ] ✅ Apenas casos de uso (use cases)
- [ ] ✅ Depende apenas de interfaces do Domain
- [ ] ✅ Não importa Infrastructure ou Presentation

### Se modificou `src/infrastructure/` (Infrastructure):

- [ ] ✅ Implementa interfaces do Domain
- [ ] ✅ Contém apenas código de infraestrutura (DB, APIs, TTS, etc)
- [ ] ✅ Não contém lógica de negócio

### Se modificou `src/presentation/` (Presentation):

- [ ] ✅ Apenas controllers/commands (HTTP, Discord, etc)
- [ ] ✅ Delega lógica de negócio para use cases
- [ ] ✅ Trata apenas entrada/saída de dados

## 🚨 Validações Importantes

- [ ] ⚠️ **Não** violei o princípio de dependência (camadas externas → internas)
- [ ] ⚠️ **Não** coloquei lógica de negócio em controllers
- [ ] ⚠️ **Não** criei acoplamento direto com implementações concretas
- [ ] ⚠️ **Não** misturei responsabilidades em uma única classe
- [ ] ⚠️ **Não** adicionei dependências externas no Domain Layer

## 📸 Screenshots (se aplicável)

<!-- Adicione screenshots ou GIFs se houver mudanças visuais -->

## 🔗 Issues Relacionadas

<!-- Mencione issues relacionadas: Closes #123, Fixes #456 -->

## 📋 Notas Adicionais

<!-- Qualquer informação adicional relevante para os revisores -->

---

**Ao submeter este PR, confirmo que:**

- ✅ Li e segui o guia [CONTRIBUTING.md](../CONTRIBUTING.md)
- ✅ Meu código segue os princípios SOLID e Clean Architecture
- ✅ Testei localmente e tudo funciona conforme esperado
- ✅ Estou pronto para receber feedback e fazer ajustes se necessário
