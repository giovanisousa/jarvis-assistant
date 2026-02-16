import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para a memória
load_dotenv()

# --- Classe de Configuração ---
class Config:
    # Dados do Zoho
    ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
    ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
    ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
    ZOHO_PORTAL_ID = os.getenv("ZOHO_PORTAL_ID")
    ZOHO_MY_USER_ID = os.getenv("ZOHO_MY_USER_ID")
    
    # Dados do Gemini
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    GMAIL_USER = os.getenv("GMAIL_USER")
    GMAIL_PASS = os.getenv("GMAIL_PASS")
    GMAIL_DESTINO_PADRAO = os.getenv("GMAIL_DESTINO_PADRAO", GMAIL_USER) # Se não tiver, envia para si mesmo
    
    # Configurações Gerais
    USER_NAME = os.getenv("USER_NAME", "Usuário") # Se não tiver no .env, usa "Usuário"

# Verificação simples para garantir que carregou
if __name__ == "__main__":
    if Config.ZOHO_CLIENT_ID:
        print("✅ Configuração carregada com sucesso!")
        print(f"👋 Olá, {Config.USER_NAME}. O ambiente está pronto.")
    else:
        print("❌ Erro: Arquivo .env não encontrado ou vazio.")