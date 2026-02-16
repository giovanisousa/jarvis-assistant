import json
import os
from datetime import datetime

ARQUIVO_HISTORICO = "db_historico_percentual.json"
ARQUIVO_PROJETOS = "db_projetos.json"

def carregar_projetos():
    if not os.path.exists(ARQUIVO_PROJETOS):
        return []
    with open(ARQUIVO_PROJETOS, "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_historico():
    if not os.path.exists(ARQUIVO_HISTORICO):
        return {}
    with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_snapshot():
    """Grava o % atual de todos os projetos para comparação futura"""
    projetos = carregar_projetos()
    historico = carregar_historico()
    
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    snapshot = {}

    print(f"💾 Salvando snapshot de percentuais ({data_hoje})...")
    
    for p in projetos:
        p_id = str(p.get('id'))
        percent = p.get('percent_complete', 0)
        nome = p.get('name')
        
        snapshot[p_id] = {
            "name": nome,
            "percent": percent,
            "data_registro": data_hoje
        }
        print(f"   - {nome}: {percent}%")

    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=4, ensure_ascii=False)
    
    print("✅ Histórico atualizado com sucesso!")

def obter_comparativo():
    """Retorna quem evoluiu e quem estagnou"""
    projetos_atuais = carregar_projetos()
    historico_antigo = carregar_historico()
    
    estagnados = []
    evoluiram = []
    
    for p in projetos_atuais:
        p_id = str(p.get('id'))
        percent_atual = int(p.get('percent_complete', 0))
        
        # Busca dados antigos
        dados_antigos = historico_antigo.get(p_id)
        
        if dados_antigos:
            percent_anterior = int(dados_antigos.get('percent', 0))
            delta = percent_atual - percent_anterior
            
            if delta == 0:
                estagnados.append({
                    "nome": p.get('name'),
                    "percent": percent_atual
                })
            else:
                evoluiram.append({
                    "nome": p.get('name'),
                    "antes": percent_anterior,
                    "agora": percent_atual,
                    "delta": delta
                })
        else:
            # Projeto novo (não tinha histórico)
            pass
            
    return estagnados, evoluiram

if __name__ == "__main__":
    # Se rodar este arquivo direto, ele salva o estado atual
    salvar_snapshot()