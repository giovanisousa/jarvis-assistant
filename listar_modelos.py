from google import genai
from config import Config

def listar_modelos():
    print("🔍 Consultando modelos...")
    try:
        client = genai.Client(api_key=Config.GEMINI_KEY)
        
        # Pega a lista bruta
        for m in client.models.list():
            # Filtra apenas se tiver "gemini" no nome
            if "gemini" in m.name:
                print(f"   ✅ Achei: {m.name}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    listar_modelos()