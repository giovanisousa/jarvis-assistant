import requests
import json
from config import Config

def investigar_projeto(project_id):
    print(f"🔍 Investigando o projeto ID: {project_id}...")
    
    # 1. Pegar o Token de acesso
    url_token = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": Config.ZOHO_REFRESH_TOKEN,
        "client_id": Config.ZOHO_CLIENT_ID,
        "client_secret": Config.ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    
    res_token = requests.post(url_token, data=params)
    access_token = res_token.json().get("access_token")
    
    # 2. Buscar APENAS os detalhes deste projeto específico
    base_url = f"https://projectsapi.zoho.com/restapi/portal/{Config.ZOHO_PORTAL_ID}"
    url_projeto = f"{base_url}/projects/{project_id}/"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    res_projeto = requests.get(url_projeto, headers=headers)
    
    if res_projeto.status_code == 200:
        dados = res_projeto.json()
        projeto = dados.get("projects", [{}])[0] 
        
        print("\n" + "="*50)
        print("📦 PAYLOAD COMPLETO DO PROJETO (RAIO-X):")
        print("="*50)
        # Imprime ABSOLUTAMENTE TUDO formatado
        print(json.dumps(projeto, indent=4, ensure_ascii=False))
        print("="*50 + "\n")
        
    else:
        print(f"❌ Erro na busca: {res_projeto.status_code}")
        print(res_projeto.text)

if __name__ == "__main__":
    # Inserindo o ID que você identificou para o teste
    investigar_projeto("2376502000007159085")