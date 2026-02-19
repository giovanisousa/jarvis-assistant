import os

def mudar_nome_assistente():
    # Extensões de arquivos que serão lidos e modificados
    extensoes_alvo = ('.py', '.md', '.txt', '.json')
    
    # Mapeamento exato (Case-sensitive para não quebrar a formatação)
    substituicoes = {
        "Jarvis": "Apex",
        "JARVIS": "APEX",
        "jarvis": "apex"
    }
    
    diretorio_atual = os.getcwd()
    arquivos_modificados = 0
    
    print(f"🔄 Iniciando migração de identidade: Jarvis ➡️  Apex...\n")
    
    for root, dirs, files in os.walk(diretorio_atual):
        # Ignora pastas de sistema, git e ambientes virtuais
        if any(ignorar in root for ignorar in ['.git', 'venv', '__pycache__', '.venv']):
            continue
            
        for file in files:
            if file.endswith(extensoes_alvo):
                caminho_arquivo = os.path.join(root, file)
                
                # Impede que o próprio script seja alterado e quebre durante a execução
                if file == "rename_to_apex.py":
                    continue
                    
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                        
                    novo_conteudo = conteudo
                    
                    # Aplica as substituições
                    for antigo, novo in substituicoes.items():
                        novo_conteudo = novo_conteudo.replace(antigo, novo)
                        
                    # Se houve mudança, salva o arquivo
                    if novo_conteudo != conteudo:
                        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                            f.write(novo_conteudo)
                        print(f"✅ Atualizado: {file}")
                        arquivos_modificados += 1
                        
                except Exception as e:
                    print(f"⚠️ Aviso ao processar {file}: {e}")
                    
    print(f"\n🚀 Sucesso! A identidade foi alterada em {arquivos_modificados} arquivos.")
    print("O assistente agora atende pelo nome de APEX.")

if __name__ == "__main__":
    mudar_nome_assistente()