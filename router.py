import json
import time
from google import genai
from google.genai import types
from config import Config

class ApexRouter:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_KEY)
        self.model_name = "gemini-flash-latest" # Modelo estável
        
        self.instrucao_roteador = """Você é o Roteador de Intenções do sistema APEX da Animati.
Sua única função é ler a mensagem do usuário e classificar a intenção em um JSON estrito.

CATEGORIAS PERMITIDAS:
- "CONVERSA": Saudações, perguntas gerais, papo furado ("bom dia", "quem é você").
- "CONSULTA_ZOHO": Perguntas sobre status de projetos, cronogramas, atrasos ou resumo de clientes.
- "ACAO_SISTEMA": Comandos imperativos para realizar ações (enviar whatsapp, enviar email, clicar, digitar, fechar app).
- "MEMORIA": Comandos explícitos para guardar uma anotação ("anote que", "lembre-se de").

REGRAS:
- Retorne APENAS um objeto JSON válido. Nenhuma palavra a mais.
- Se identificar um nome de cliente ou projeto, coloque na lista "projetos_mencionados".

EXEMPLO DE SAÍDA ESPERADA:
{
    "categoria": "ACAO_SISTEMA",
    "projetos_mencionados": ["Unimed"],
    "acao_detectada": "enviar_whatsapp"
}
"""

    def classificar(self, pergunta, tentativas=3):
        """Tenta classificar a intenção. Se a API estiver lotada (503), tenta de novo."""
        for tentativa in range(tentativas):
            try:
                resp = self.client.models.generate_content(
                    model=self.model_name,
                    contents=pergunta,
                    config=types.GenerateContentConfig(
                        system_instruction=self.instrucao_roteador,
                        temperature=0.0,
                        response_mime_type="application/json"
                    )
                )
                return json.loads(resp.text)
            except Exception as e:
                print(f"⚠️ [Router Error - Tentativa {tentativa + 1}/{tentativas}]: {e}")
                if tentativa < tentativas - 1:
                    time.sleep(2)  # Espera 2 segundos antes de tentar de novo
                else:
                    # Se falhou todas as vezes, não permite que ele alucine caindo em 'CONVERSA'
                    return {"categoria": "ERRO_SISTEMA", "projetos_mencionados": [], "acao_detectada": None}