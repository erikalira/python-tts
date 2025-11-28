# Interface Gráfica de Configuração do TTS Hotkey

## 🎯 **Nova Funcionalidade Implementada**

Foi adicionada uma **interface gráfica amigável** para configurar o executável TTS Hotkey do Windows, eliminando a necessidade de editar código para personalizações básicas.

## 🖼️ **Como Funciona**

### **Primeira Execução**

1. **Executa o .exe** → Janela de configuração abre automaticamente
2. **Insere Discord User ID** (obrigatório)
3. **Configura outras opções** (opcional)
4. **Clica "Salvar e Continuar"** → Configuração salva permanentemente
5. **Pronto!** Sistema ativo para usar `{texto}`

### **Reconfiguração**

- **System Tray**: Botão direito no ícone → "⚙️ Configurações"
- **Manual**: Delete `~/tts_hotkey_config.json` e reinicie

## 🔧 **Configurações Disponíveis**

### **Obrigatória**

- **Discord User ID**: Seu ID único do Discord (números)
  - Como obter: Discord → Configurações → Avançado → Modo Desenvolvedor
  - Clique direito em seu nome → "Copiar ID"

### **Opcionais**

- **URL do Bot**: Endereço do bot Discord
- **Engine TTS**: gtts, pyttsx3, edge-tts
- **Idioma**: pt, en, es, fr

## 💾 **Persistência**

As configurações são salvas em: `~/tts_hotkey_config.json`

Exemplo do arquivo:

```json
{
  "discord_member_id": "123456789012345678",
  "discord_channel_id": null,
  "discord_bot_url": "https://python-tts-s3z8.onrender.com",
  "tts_engine": "gtts",
  "tts_language": "pt"
}
```

## ✨ **Benefícios**

### **Para Usuários Finais**

- ✅ **Zero código** para configurar
- ✅ **Interface intuitiva** com instruções claras
- ✅ **Configuração permanente**
- ✅ **Validação automática** de dados
- ✅ **Reconfiguração fácil** via system tray

### **Para Desenvolvedores**

- ✅ **Menos suporte** necessário
- ✅ **Distribuição simplificada**
- ✅ **Configuração padrão** mantida no código
- ✅ **Fallback console** se GUI falhar

## 🎮 **Experiência do Usuário**

### **Fluxo Típico**

```
1. Duplo-click no .exe
   ↓
2. Janela "TTS Hotkey - Configuração" abre
   ↓
3. Usuário vê instruções claras sobre Discord ID
   ↓
4. Preenche ID + configurações opcionais
   ↓
5. Clica "Salvar e Continuar"
   ↓
6. Sistema inicia automaticamente
   ↓
7. Usa {texto} normalmente!
```

### **Validações Incluídas**

- ❌ Discord ID vazio
- ❌ Discord ID com caracteres inválidos
- ✅ Apenas números aceitos
- ✅ Configurações salvas automaticamente

## 🔄 **Compatibilidade**

- **GUI Disponível**: Interface tkinter completa
- **GUI Indisponível**: Fallback para configuração via console
- **Configuração Existente**: Carregada automaticamente
- **Primeira Vez**: Interface de configuração obrigatória

## 🚀 **Implementação Técnica**

### **Principais Classes**

- `Config`: Gerencia configurações e persistência
- `ConfigWindow`: Interface gráfica tkinter
- Carregamento/salvamento automático em JSON

### **Integração**

- Verificação na `main()` se configuração existe
- System tray com opção "Configurações"
- Fallback gracioso se tkinter não disponível

---

**Resultado**: Interface muito mais amigável para usuários finais! 🎉
