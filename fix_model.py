#!/usr/bin/env python3
"""
Script para corrigir modelo Gemini nos arquivos do Jarvis
Lista modelos disponíveis e atualiza automaticamente
"""

import os
from pathlib import Path

def listar_modelos_disponiveis():
    """Lista modelos Gemini disponíveis"""
    try:
        from google import genai
        from config import Config
        
        print("🔍 Consultando modelos disponíveis na API Gemini...")
        print("-"*70)
        
        client = genai.Client(api_key=Config.GEMINI_KEY)
        
        modelos_validos = []
        
        for model in client.models.list():
            nome = model.name
            if 'gemini' in nome.lower() and 'generatecontent' in str(model.supported_generation_methods).lower():
                modelos_validos.append(nome)
                print(f"✅ {nome}")
        
        print("-"*70)
        print(f"\n📊 Total de modelos disponíveis: {len(modelos_validos)}\n")
        
        return modelos_validos
        
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")
        print("\n💡 Usando lista padrão de modelos conhecidos:")
        modelos_padrao = [
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b", 
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        for m in modelos_padrao:
            print(f"  • {m}")
        return modelos_padrao

def corrigir_arquivo(caminho, modelo_antigo, modelo_novo):
    """Corrige o modelo em um arquivo"""
    try:
        if not os.path.exists(caminho):
            return False
        
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        if modelo_antigo not in conteudo:
            return False
        
        conteudo_novo = conteudo.replace(
            f'self.model_name = "{modelo_antigo}"',
            f'self.model_name = "{modelo_novo}"'
        )
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo_novo)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir {caminho}: {e}")
        return False

def main():
    print("="*70)
    print("🔧 CORREÇÃO DE MODELO GEMINI - JARVIS")
    print("="*70)
    print()
    
    # Lista modelos disponíveis
    modelos = listar_modelos_disponiveis()
    
    # Modelo recomendado
    if "gemini-1.5-flash" in modelos:
        modelo_recomendado = "gemini-1.5-flash"
    elif "gemini-1.5-pro" in modelos:
        modelo_recomendado = "gemini-1.5-pro"
    elif modelos:
        modelo_recomendado = modelos[0]
    else:
        modelo_recomendado = "gemini-1.5-flash"
    
    print(f"💡 Modelo recomendado: {modelo_recomendado}")
    print()
    
    # Pergunta ao usuário
    print("Deseja usar este modelo? (s/n)")
    print("Ou digite o nome de outro modelo da lista acima:")
    escolha = input("> ").strip()
    
    if escolha.lower() == 'n':
        print("\n❌ Operação cancelada.")
        return
    elif escolha.lower() != 's' and escolha:
        modelo_recomendado = escolha
    
    print()
    print(f"✅ Usando modelo: {modelo_recomendado}")
    print()
    
    # Lista de arquivos para corrigir
    arquivos = [
        "brain.py",
        "brain_v2.py",
        "brain_v2_logged.py"
    ]
    
    modelo_antigo = "gemini-2.0-flash-exp"
    corrigidos = []
    
    print("🔄 Corrigindo arquivos...")
    print("-"*70)
    
    for arquivo in arquivos:
        if corrigir_arquivo(arquivo, modelo_antigo, modelo_recomendado):
            print(f"✅ {arquivo} corrigido")
            corrigidos.append(arquivo)
        else:
            if os.path.exists(arquivo):
                print(f"⚠️  {arquivo} - modelo já correto ou não encontrado")
            else:
                print(f"⏭️  {arquivo} - arquivo não existe")
    
    print("-"*70)
    print()
    
    if corrigidos:
        print(f"🎉 {len(corrigidos)} arquivo(s) corrigido(s) com sucesso!")
        print()
        print("Arquivos atualizados:")
        for arq in corrigidos:
            print(f"  • {arq}")
        print()
        print("✅ Agora você pode executar o Jarvis normalmente!")
        print()
        print("Comandos:")
        print("  streamlit run app_v2.py")
        print("  python main_v2.py")
    else:
        print("ℹ️  Nenhum arquivo foi modificado.")
        print("   Verifique se os arquivos existem ou se já estão corretos.")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
