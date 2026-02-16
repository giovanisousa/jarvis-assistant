import os
import requests
from dotenv import load_dotenv

# Carrega suas chaves do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")

# URL de autenticação do Zoho (Geral ou .EU/.CN dependendo da sua conta, mas .COM é o padrão)
TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"

def gerar_refresh_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ ERRO: Client ID ou Secret não encontrados no arquivo .env!")
        return

    print("--- GERADOR DE REFRESH TOKEN ZOHO ---")
    print("Cole abaixo o código que você gerou no navegador (Self Client):")
    auth_code = input("Código: ").strip()

    # Monta o pedido para o Zoho
    params = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        # redirect_uri não é necessário para Self Client, mas as vezes o Zoho pede
        # Se der erro, tente remover esta linha ou usar http://localhost
    }

    try:
        response = requests.post(TOKEN_URL, data=params)
        dados = response.json()

        if "refresh_token" in dados:
            print("\n✅ SUCESSO! Aqui está seu Refresh Token:")
            print("="*60)
            print(dados["refresh_token"])
            print("="*60)
            print("👉 Copie este código e cole no seu arquivo .env no campo ZOHO_REFRESH_TOKEN")
        else:
            print("\n❌ ERRO AO GERAR TOKEN:")
            print(dados) 
            print("Dica: O código gerado no navegador expira rápido ou já foi usado.")
            
    except Exception as e:
        print(f"\n❌ Erro de conexão: {e}")

if __name__ == "__main__":
    gerar_refresh_token()