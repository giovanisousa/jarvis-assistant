import requests
from config import Config

def descobrir_portal():
    print("🔍 Investigando Portais disponíveis...")
    
    # 1. Recuperar Token (código simplificado do zoho_sync)
    url_token = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": Config.ZOHO_REFRESH_TOKEN,
        "client_id": Config.ZOHO_CLIENT_ID,
        "client_secret": Config.ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    
    try:
        res_token = requests.post(url_token, data=params)
        if res_token.status_code != 200:
            print("❌ Erro de Token:", res_token.text)
            return
        
        access_token = res_token.json().get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Perguntar ao Zoho quais portais existem
        # Este endpoint não precisa de ID, ele LISTA os IDs
        url_portals = "https://projectsapi.zoho.com/restapi/portals/"
        
        res = requests.get(url_portals, headers=headers)
        
        if res.status_code == 200:
            portals = res.json().get("portals", [])
            print("\n✅ SUCESSO! Encontrei os seguintes portais:")
            print("="*60)
            for p in portals:
                print(f"Nome: {p.get('name')}")
                print(f"👉 ID CORRETO: {p.get('id_string')}") # Às vezes o ID vem como id ou id_string
                print(f"Link: {p.get('link').get('project').get('url')}")
                print("-" * 30)
            print("="*60)
            print("Copie o número acima (ID CORRETO) e atualize seu arquivo .env")
        else:
            print(f"❌ Erro ao listar portais: {res.status_code}")
            print(res.text)
            
    except Exception as e:
        print(f"Erro crítico: {e}")

if __name__ == "__main__":
    descobrir_portal()