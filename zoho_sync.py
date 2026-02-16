import requests
import json
from config import Config

class ZohoSync:
    def __init__(self):
        self.access_token = None
        self.base_url = f"https://projectsapi.zoho.com/restapi/portal/{Config.ZOHO_PORTAL_ID}"

    def get_access_token(self):
        url = "https://accounts.zoho.com/oauth/v2/token"
        params = {
            "refresh_token": Config.ZOHO_REFRESH_TOKEN,
            "client_id": Config.ZOHO_CLIENT_ID,
            "client_secret": Config.ZOHO_CLIENT_SECRET,
            "grant_type": "refresh_token"
        }
        try:
            response = requests.post(url, data=params)
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
                return True
            else:
                print(f"❌ Erro ao renovar token: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erro de ligação: {e}")
            return False

    def get_paginated_data(self, endpoint, key_name):
        """Busca todos os registos lidando com a paginação do Zoho"""
        all_items = []
        index = 0
        range_val = 100 
        
        while True:
            separator = "&" if "?" in endpoint else "?"
            url = f"{self.base_url}{endpoint}{separator}index={index}&range={range_val}"
            
            res = requests.get(url, headers={"Authorization": f"Bearer {self.access_token}"})
            if res.status_code != 200:
                print(f"❌ Erro na busca ({endpoint}): {res.status_code}")
                break
                
            data = res.json()
            items = data.get(key_name, [])
            all_items.extend(items)
            
            if len(items) < range_val:
                break
            
            index += range_val
            
        return all_items

    def sync_my_data(self):
        """Faz a extração utilizando o Custom Status do Zoho"""
        if not self.access_token and not self.get_access_token():
            return

        print("⏳ A descarregar a lista inicial de projetos...")
        all_projects = self.get_paginated_data("/projects/", "projects")
        
        # Filtro Nível 1: Apenas os seus projetos
        meus_projetos = [p for p in all_projects if p.get("owner_id") == Config.ZOHO_MY_USER_ID]
        print(f"✅ Filtro Nível 1: {len(meus_projetos)} projetos sob a sua gestão.")
        
        # Lista letal de palavras que indicam que o projeto acabou
        PALAVRAS_BLOQUEADAS = ["completed", "cancelled", "concluído", "cancelado", "finalizado", "arquivado"]
        
        dados_completos = []
        
        print("🔍 Aplicando filtro por Custom Status...")
        for proj in meus_projetos:
            proj_id = proj.get("id")
            proj_name = proj.get("name")
            
            # Pega o Custom Status Name (se não existir, fica vazio)
            custom_status = str(proj.get("custom_status_name", "")).lower()
            
            # FILTRO NÍVEL 2: A Mágica do Custom Status
            if custom_status in PALAVRAS_BLOQUEADAS:
                print(f"   🚫 Ignorando projeto ({custom_status}): {proj_name}")
                continue # Pula imediatamente!
            
            print(f"📥 A descarregar tarefas do projeto ATIVO: {proj_name}")
            
            # Só descarrega tarefas se o projeto for realmente ativo
            tasks_endpoint = f"/projects/{proj_id}/tasks/"
            all_tasks = self.get_paginated_data(tasks_endpoint, "tasks")
            
            project_data = {
                "id": proj_id,
                "name": proj_name,
                "status": proj.get("custom_status_name", "Ativo"),
                # Busca 'project_percent' primeiro, se não achar tenta 'percent_complete', senão 0
                "percent_complete": proj.get("project_percent", proj.get("percent_complete", 0)), 
                "tasks": []
            }
            
            for t in all_tasks:
                task_info = {
                    "name": t.get("name"),
                    "status": t.get("status", {}).get("name") if isinstance(t.get("status"), dict) else "Sem status",
                    "percent": t.get("percent_complete", 0),
                    "end_date": t.get("end_date", "Sem data"),
                    "priority": t.get("priority", "Normal"),
                    "tasklist": t.get("tasklist", {}).get("name", "Sem lista"),
                    "milestone": t.get("milestone", {}).get("name", "Sem Phase")
                }
                project_data["tasks"].append(task_info)
                
            dados_completos.append(project_data)
            
        # Gravar a "memória" limpa
        with open("db_projetos.json", "w", encoding="utf-8") as f:
            json.dump(dados_completos, f, indent=4, ensure_ascii=False)
            
        print(f"\n🚀 SPRINT 1 CONCLUÍDA! Ficaram {len(dados_completos)} projetos reais no 'db_projetos.json'.")

if __name__ == "__main__":
    bot = ZohoSync()
    bot.sync_my_data()