## Matriz de senioridade (estado atual vs alvo + como chegar em Senior/Staff)

| Ponto | Estado atual | Nível atual | Como chegar em Senior/Staff |
|---|---|---|---|
| Fila distribuída do bot | Redis backend com lock por guild, processing lease, renew de lock/lease e worker dedicado. | Senior | **Staff:** validar concorrência real com 2+ instâncias do bot competindo pelo mesmo guild, com teste de race/failover e critérios de throughput/p99 por guild. |
| Persistência e stack de produção | `docker-compose.prod.yml` já sobe Redis + Postgres + bot com healthcheck e restart policy. | Senior | **Staff:** runbooks de incidentes, backup/restore automatizado, teste de DR recorrente (restore validado) e checklist de rollback por versão. |
| Contratos explícitos da fila | `IAudioQueue` já define contratos tipados e operações de lease/lock. | Senior | **Staff:** versionar contratos (policy de compatibilidade e depreciação), com migração controlada entre versões do bot/desktop. |
| Qualidade de testes Redis | Cobertura unit boa, mas base relevante ainda usa `FakeRedis`. | Pleno+/Senior- | **Senior:** adicionar suíte de integração Redis real em CI dedicada (docker service), incluindo TTL, lock-loss e recovery. **Staff:** soak test periódico e validação de estabilidade sob carga. |
| CI cross-platform | Workflow de teste principal ainda só em Ubuntu. | Pleno+/Senior- | **Senior:** matriz Linux + Windows para fluxos críticos. **Staff:** gates de release separados por runtime (bot e desktop) com critérios objetivos. |
| Testes de integração externa | Integrações de rede/OS ainda são opt-in e podem ser skipped. | Pleno+ | **Senior:** job noturno para integrações reais (network + Windows). **Staff:** pirâmide de validação por ambiente (smoke, integration, release candidate). |
| Gate de cobertura | `--cov-fail-under=70` já é um bom baseline. | Senior- | **Senior:** subir para 80–85 progressivamente. **Staff:** gate por domínio crítico (queue/runtime/presentation) e bloqueio por regressão de domínio. |
| Observabilidade | Health endpoint e contrato HTTP já existem. | Senior- | **Senior:** adicionar OpenTelemetry (spans + metrics) no fluxo HTTP → queue worker → TTS. **Staff:** SLO/SLI formal, dashboards e alertas por erro/latência/depth da fila. |
