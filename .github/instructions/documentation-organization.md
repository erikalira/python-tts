# Organização da Documentação

## Estrutura da Documentação

Todos os arquivos de documentação do projeto (exceto o README.md principal) devem ser mantidos no diretório `/docs`.

### Localização dos Arquivos

- **README.md** - Permanece na raiz do projeto
- **Demais documentações** - Localizadas em `/docs/`

### Arquivos na pasta `/docs/`:

- `ARCHITECTURE.md` - Arquitetura do sistema
- `CORREÇÕES_IMPLEMENTADAS.md` - Log de correções implementadas
- `HOTKEY_SETUP.md` - Configuração de teclas de atalho
- `HOTKEY_SETUP_OLD.md` - Configuração antiga de teclas (histórico)
- `README_DESKTOP_APP.md` - README do Desktop App
- `TROUBLESHOOTING.md` - Guia de solução de problemas
- `VOICE_TIMEOUT.md` - Documentação sobre timeout de voz

## Diretrizes

1. **Novos arquivos de documentação** devem ser criados diretamente na pasta `/docs/`
2. **O README.md principal** deve permanecer na raiz para visibilidade no GitHub
3. **Atualize links** quando mover arquivos de documentação
4. **Mantenha a estrutura organizada** para facilitar a navegação

## Exemplo de Estrutura

```
/
├── README.md (principal)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── HOTKEY_SETUP.md
│   ├── TROUBLESHOOTING.md
│   └── ...outros arquivos de documentação
└── .github/
    └── instructions/
        └── documentation-organization.md (este arquivo)
```

## Atualização de Links

Ao referenciar documentação em outros arquivos, use caminhos relativos:

- `docs/ARCHITECTURE.md`
- `docs/TROUBLESHOOTING.md`
- etc.
