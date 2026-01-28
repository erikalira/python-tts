#!/usr/bin/env python3
"""
Teste de Integração - TTS Hotkey
Verifica se todas as funcionalidades estão operacionais antes da compilação.
"""

def test_discord_integration():
    """Testa integração com Discord bot."""
    import requests
    
    print("🔍 Testando Discord Bot Integration...")
    
    # Test health endpoint
    try:
        response = requests.get('https://python-tts-s3z8.onrender.com/health', timeout=10)
        if response.status_code == 200:
            print("✅ Discord bot está online")
        else:
            print(f"⚠️ Discord bot status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro conectando ao Discord bot: {e}")
        return False
    
    # Test TTS endpoint
    try:
        payload = {
            'text': 'teste de integração',
            'channel_id': None,
            'member_id': None
        }
        
        response = requests.post(
            'https://python-tts-s3z8.onrender.com/speak',
            json=payload,
            timeout=10,
            headers={'User-Agent': 'TTS-Integration-Test/1.0'}
        )
        
        if response.status_code == 200:
            print("✅ Endpoint /speak funcionando - TTS enviado com sucesso")
            return True
        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get('error', 'Erro desconhecido')
            if "não está conectado" in error_msg:
                print("⚠️ Bot não está em canal de voz (normal se não estiver testando)")
                print("💡 Para testar completamente: entre num canal e use /join")
                return True  # This is expected behavior
            else:
                print(f"❌ Erro TTS: {error_msg}")
                return False
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro testando TTS: {e}")
        return False


def test_dependencies():
    """Testa se dependências estão instaladas."""
    print("\n📦 Testando Dependências...")
    
    required_packages = [
        ('requests', 'Comunicação HTTP'),
        ('keyboard', 'Captura de hotkeys'),
    ]
    
    optional_packages = [
        ('pygame', 'Reprodução de áudio'),
        ('pyttsx3', 'TTS local'),
        ('gtts', 'Google TTS'),
        ('pystray', 'System tray'),
        ('PIL', 'Ícones'),
    ]
    
    missing_required = []
    missing_optional = []
    
    # Test required packages
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (OBRIGATÓRIO)")
            missing_required.append(package)
    
    # Test optional packages  
    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"⚠️ {package} - {description} (opcional)")
            missing_optional.append(package)
        except Exception as e:
            if 'Gtk' in str(e) or 'display' in str(e).lower():
                print(f"⚠️ {package} - {description} (GUI não disponível - OK)")
            else:
                print(f"⚠️ {package} - {description} (erro: {e})")
                missing_optional.append(package)
    
    if missing_required:
        print(f"\n❌ DEPENDÊNCIAS OBRIGATÓRIAS EM FALTA: {', '.join(missing_required)}")
        print("Execute: pip install " + " ".join(missing_required))
        return False
    
    if missing_optional:
        print(f"\n💡 Dependências opcionais em falta: {', '.join(missing_optional)}")
        print("Para funcionalidade completa: pip install " + " ".join(missing_optional))
    
    return True


def test_file_structure():
    """Testa se arquivos necessários existem."""
    print("\n📁 Testando Estrutura de Arquivos...")
    
    import os
    
    required_files = [
        ('tts_hotkey_configurable.py', 'Versão única com Clean Architecture'),
        ('scripts/build/build_clean_architecture.ps1', 'Script de build Clean Architecture'),
    ]
    
    missing_files = []
    
    for file_path, description in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} (FALTANDO)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ ARQUIVOS EM FALTA: {', '.join(missing_files)}")
        return False
    
    return True


def test_basic_functionality():
    """Testa funcionalidade básica do código."""
    print("\n⚙️ Testando Funcionalidades Básicas...")
    
    try:
        # Test syntax only - don't execute (avoids GUI dependencies)
        print("🔍 Testando sintaxe tts_hotkey_configurable.py...")
        with open('tts_hotkey_configurable.py', 'r') as f:
            code = f.read()
        compile(code, 'tts_hotkey_configurable.py', 'exec')
        print("✅ tts_hotkey_configurable.py - sintaxe OK")
        
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe em tts_hotkey_configurable.py: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Aviso em tts_hotkey_configurable.py: {e}")
        print("💡 Sintaxe OK, erro pode ser dependência GUI (normal em Linux)")
    
    # Simple version removed - Clean Architecture handles all cases with embedded fallback
        
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("TTS HOTKEY - INTEGRATION TEST")
    print("=" * 70)
    
    tests = [
        ("Estrutura de Arquivos", test_file_structure),
        ("Dependências", test_dependencies), 
        ("Funcionalidade Básica", test_basic_functionality),
        ("Integração Discord", test_discord_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSOU")
                passed += 1
            else:
                print(f"❌ {test_name}: FALHOU")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 70)
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"📈 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para compilação")
        print("\n💡 Próximos passos:")
        print("   • make build-windows  (versão simples)")  
        print("   • make build-hotkey   (versão completa)")
        print("   • Teste o executável em máquina Windows")
        return True
    else:
        print(f"\n⚠️ {failed} TESTE(S) FALHARAM")
        print("🔧 Corrija os problemas antes de compilar")
        return False


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)