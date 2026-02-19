#!/usr/bin/env python3
"""
🤖 APEX V2 - INSTALADOR E CONFIGURADOR
Script para configurar e testar a versão melhorada do assistente
"""

import os
import shutil
from pathlib import Path

def banner():
    print("="*70)
    print("   🤖 APEX V2 - ASSISTENTE EXECUTIVO CONVERSACIONAL")
    print("   Instalador e Configurador Automático")
    print("="*70)
    print()

def verificar_dependencias():
    """Verifica se as bibliotecas necessárias estão instaladas"""
    print("📋 Verificando dependências...")
    
    dependencias = {
        'pyttsx3': 'Síntese de voz',
        'speech_recognition': 'Reconhecimento de voz',
        'keyboard': 'Detecção de teclas',
        'pyautogui': 'Automação de interface',
        'google.generativeai': 'API Gemini',
        'requests': 'Requisições HTTP',
        'python-dotenv': 'Variáveis de ambiente'
    }
    
    faltando = []
    
    for pacote, descricao in dependencias.items():
        try:
            if pacote == 'google.generativeai':
                __import__('google.genai')
            elif pacote == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(pacote.replace('-', '_'))
            print(f"   ✅ {pacote} - {descricao}")
        except ImportError:
            print(f"   ❌ {pacote} - {descricao} [FALTANDO]")
            faltando.append(pacote)
    
    print()
    
    if faltando:
        print("⚠️  ATENÇÃO: Algumas dependências estão faltando!")
        print("\nInstale com:")
        print(f"pip install {' '.join(faltando)}")
        print()
        return False
    else:
        print("✅ Todas as dependências estão instaladas!\n")
        return True

def verificar_configuracao():
    """Verifica se o arquivo .env existe e está configurado"""
    print("🔧 Verificando configuração (.env)...")
    
    if not os.path.exists('.env'):
        print("   ❌ Arquivo .env não encontrado!")
        criar = input("   Deseja criar um modelo de .env? (s/n): ").lower()
        
        if criar == 's':
            criar_env_template()
        else:
            print("   ⚠️  Configure manualmente o arquivo .env antes de continuar.")
            return False
    else:
        print("   ✅ Arquivo .env encontrado")
        
        # Verifica campos essenciais
        with open('.env', 'r') as f:
            conteudo = f.read()
            
        campos_essenciais = [
            'GEMINI_API_KEY',
            'GMAIL_USER',
            'GMAIL_PASS'
        ]
        
        faltando = []
        for campo in campos_essenciais:
            if campo not in conteudo or f'{campo}=' in conteudo and '=' in conteudo.split(campo)[1].split('\n')[0] and not conteudo.split(campo)[1].split('\n')[0].split('=')[1].strip():
                faltando.append(campo)
        
        if faltando:
            print(f"   ⚠️  Campos vazios ou ausentes: {', '.join(faltando)}")
            print("   Configure estes campos no arquivo .env")
            return False
        else:
            print("   ✅ Configuração básica ok")
    
    print()
    return True

def criar_env_template():
    """Cria um template do arquivo .env"""
    template = """# Configurações do APEX
# Preencha os valores e remova os comentários

# === GEMINI API (OBRIGATÓRIO) ===
GEMINI_API_KEY=sua_chave_aqui

# === EMAIL (OBRIGATÓRIO para funções de email) ===
GMAIL_USER=seu_email@gmail.com
GMAIL_PASS=sua_senha_app_gmail
GMAIL_DESTINO_PADRAO=destinatario@gmail.com

# === ZOHO (OPCIONAL - só se usar integração Zoho Projects) ===
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=
ZOHO_REFRESH_TOKEN=
ZOHO_PORTAL_ID=
ZOHO_MY_USER_ID=

# === USUÁRIO ===
USER_NAME=Giovani
"""
    
    with open('.env', 'w') as f:
        f.write(template)
    
    print("   ✅ Arquivo .env criado!")
    print("   📝 IMPORTANTE: Edite o arquivo .env e preencha suas credenciais")
    print()

def ativar_versao_v2():
    """Ativa a versão V2 do Apex"""
    print("🔄 Ativando APEX V2...")
    
    # Cria backup dos originais
    if os.path.exists('brain.py'):
        if not os.path.exists('brain_original.py'):
            shutil.copy2('brain.py', 'brain_original.py')
            print("   💾 Backup criado: brain_original.py")
    
    if os.path.exists('main.py'):
        if not os.path.exists('main_original.py'):
            shutil.copy2('main.py', 'main_original.py')
            print("   💾 Backup criado: main_original.py")
    
    # Ativa V2
    if os.path.exists('brain_v2.py'):
        shutil.copy2('brain_v2.py', 'brain.py')
        print("   ✅ brain.py atualizado para V2")
    else:
        print("   ❌ brain_v2.py não encontrado!")
        return False
    
    if os.path.exists('main_v2.py'):
        shutil.copy2('main_v2.py', 'main.py')
        print("   ✅ main.py atualizado para V2")
    else:
        print("   ❌ main_v2.py não encontrado!")
        return False
    
    print("   🚀 APEX V2 ativado com sucesso!")
    print()
    return True

def desativar_versao_v2():
    """Restaura versão original"""
    print("🔄 Restaurando versão original...")
    
    if os.path.exists('brain_original.py'):
        shutil.copy2('brain_original.py', 'brain.py')
        print("   ✅ brain.py restaurado")
    
    if os.path.exists('main_original.py'):
        shutil.copy2('main_original.py', 'main.py')
        print("   ✅ main.py restaurado")
    
    print("   ↩️  Versão original restaurada!")
    print()

def testar_voz():
    """Testa o sistema de voz"""
    print("🎤 Testando sistema de voz...")
    
    try:
        from voz import ApexVoz
        
        voz = ApexVoz()
        print("   🔊 Teste de síntese de voz...")
        voz.falar("Sistema de voz funcionando perfeitamente.")
        print("   ✅ TTS ok")
        
        print("\n   🎤 Teste de reconhecimento...")
        print("   Diga algo (você tem 5 segundos):")
        
        texto = voz.ouvir()
        
        if texto:
            print(f"   ✅ STT ok - Captado: '{texto}'")
        else:
            print("   ⚠️  Nada foi captado (microfone ok?)")
        
        del voz
        print()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        print()
        return False

def menu_principal():
    """Menu interativo"""
    while True:
        print("\n" + "="*70)
        print("   MENU PRINCIPAL")
        print("="*70)
        print("   1. Verificar dependências")
        print("   2. Verificar configuração (.env)")
        print("   3. Ativar APEX V2")
        print("   4. Restaurar versão original")
        print("   5. Testar sistema de voz")
        print("   6. Executar APEX")
        print("   7. Ver documentação")
        print("   0. Sair")
        print("="*70)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            verificar_dependencias()
        elif opcao == '2':
            verificar_configuracao()
        elif opcao == '3':
            ativar_versao_v2()
        elif opcao == '4':
            desativar_versao_v2()
        elif opcao == '5':
            testar_voz()
        elif opcao == '6':
            executar_apex()
        elif opcao == '7':
            mostrar_documentacao()
        elif opcao == '0':
            print("\n👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")
        
        input("\nPressione ENTER para continuar...")

def executar_apex():
    """Executa o Apex"""
    print("\n🚀 Iniciando APEX...")
    print("="*70)
    
    if not verificar_configuracao():
        print("❌ Configure o .env antes de executar!")
        return
    
    print("\n⚡ Executando main.py...")
    print("   (Pressione Ctrl+C para encerrar)\n")
    
    try:
        import main
    except KeyboardInterrupt:
        print("\n\n🛑 Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro na execução: {e}")

def mostrar_documentacao():
    """Mostra o guia de uso"""
    if os.path.exists('GUIA_V2.md'):
        with open('GUIA_V2.md', 'r', encoding='utf-8') as f:
            print("\n" + f.read())
    else:
        print("❌ Arquivo GUIA_V2.md não encontrado!")

def main():
    banner()
    
    print("🎯 BEM-VINDO AO INSTALADOR DO APEX V2!\n")
    print("Este assistente vai ajudá-lo a configurar e testar o sistema.\n")
    
    # Verificação inicial rápida
    deps_ok = verificar_dependencias()
    config_ok = verificar_configuracao()
    
    if deps_ok and config_ok:
        print("✅ Sistema pronto para uso!\n")
        iniciar = input("Deseja ativar o APEX V2 agora? (s/n): ").lower()
        
        if iniciar == 's':
            if ativar_versao_v2():
                rodar = input("\nDeseja executar o APEX agora? (s/n): ").lower()
                if rodar == 's':
                    executar_apex()
                    return
    
    # Menu interativo
    menu_principal()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Instalação cancelada pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
