import json
import os
import time
from google import genai
from google.genai import types
from config import Config
from datetime import datetime
from ferramentas import ApexFerramentas
from router import ApexRouter
from database import DatabaseManager # IMPORTANDO O BANCO DE DADOS

class ApexBrain:
    def __init__(self):
        if not Config.GEMINI_KEY:
            raise ValueError("❌ Chave do Gemini não encontrada no arquivo .env!")
        
        self.client = genai.Client(api_key=Config.GEMINI_KEY)
        self.model_name = "gemini-flash-latest" # Modelo estável
        
        # Módulos Internos
        self.ferramentas = ApexFerramentas()
        self.router = ApexRouter()
        self.db = DatabaseManager()
        
        # Diretório Físico de Projetos (Para guardar arquivos no PC)
        self.pasta_projetos = os.path.join(os.getcwd(), "Projetos_Animati")
        if not os.path.exists(self.pasta_projetos):
            os.makedirs(self.pasta_projetos)

        # Estados e Memórias
        self.dados_projetos = self.carregar_dados_zoho()
        self.historico_conversa = []
        self.max_historico = 10
        
        # Travas de Segurança
        self.acao_pendente = None 
        
        self.data_hoje = datetime.now().strftime("%d/%m/%Y às %H:%M")

        # System Prompt Atualizado com o conhecimento dos Custom Fields
        self.instrucao_conversa = f"""Você é APEX, o assistente executivo pessoal do Giovani na Animati.
Data atual: {self.data_hoje}

INFORMAÇÕES DE PROJETOS E FASES:
Os projetos possuem 'custom_fields' que ditam o cronograma real.
- "Data de Onboarding": Reunião inicial.
- "Data Liberação Servidor": Fim da Infra, início da Implantação.
- "Data de Inicio da Implantação": Sistema sendo instalado.
- "Data de Homologação": Cliente testando.
- "Data de Virada": Entrada em Produção (Go-Live).
- "Data de Inicio da OA": Operação Assistida.
- "Link do Google": Pasta do Drive do cliente.

REGRA DE RESPOSTA:
Seja DIRETO, CONCISO e PROFISSIONAL. Não liste todas as datas se o usuário não pedir. 
Cruze os dados: se o usuário perguntar o status, use os custom_fields para determinar a fase exata e leia as notas (MEMORIA_GESTOR) para dar o contexto humano.
"""

    def carregar_dados_zoho(self):
        try:
            with open("db_projetos.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def garantir_pasta_projeto(self, nome_projeto):
        """Garante que o projeto tem uma pasta física no PC"""
        nome_seguro = "".join(c for c in nome_projeto if c.isalnum() or c in (' ', '_', '-')).rstrip()
        caminho_pasta = os.path.join(self.pasta_projetos, nome_seguro)
        
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
            print(f"📂 Pasta de projeto verificada/criada: {caminho_pasta}")
        return caminho_pasta

    def adicionar_ao_historico(self, role, content):
        self.historico_conversa.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        if len(self.historico_conversa) > self.max_historico * 2:
            self.historico_conversa = self.historico_conversa[-self.max_historico * 2:]

    def construir_contexto_conversa(self):
        if not self.historico_conversa: return ""
        contexto = "\n[CONTEXTO RECENTE]\n"
        for msg in self.historico_conversa[-6:]:
            ator = "GIOVANI" if msg["role"] == "user" else "APEX"
            contexto += f"{ator}: {msg['content'][:250]}\n"
        return contexto + "\n"

    def buscar_dados_projetos(self, nomes_mencionados):
        if not nomes_mencionados: return []
        projetos_encontrados = []
        for nome_busca in nomes_mencionados:
            termo_limpo = str(nome_busca).lower()
            for proj in self.dados_projetos:
                if termo_limpo in proj.get("name", "").lower():
                    if proj not in projetos_encontrados:
                        projetos_encontrados.append(proj)
        return projetos_encontrados

    def extrair_texto_nota(self, frase_usuario, nome_projeto_detectado):
        prompt_extracao = (
            f"Frase: '{frase_usuario}'. Contexto: '{nome_projeto_detectado}'. "
            "Extraia apenas o fato a ser anotado no banco de dados. Responda curto."
        )
        resp = self.client.models.generate_content(model=self.model_name, contents=prompt_extracao)
        return resp.text.strip()

    def analisar(self, pergunta):
        print(f"\n🗣️ Giovani: '{pergunta}'")
        self.adicionar_ao_historico("user", pergunta)

        # 1. MODO DE SEGURANÇA (Confirmação de Ação)
        if self.acao_pendente:
            resp = pergunta.lower()
            if any(p in resp for p in ["sim", "pode", "manda", "vai", "confirmo", "ok"]):
                resultado = self._executar_ferramenta(self.acao_pendente)
                self.acao_pendente = None
                self.adicionar_ao_historico("assistant", resultado)
                return resultado
            elif any(p in resp for p in ["não", "nao", "cancela", "parar", "abortar"]):
                self.acao_pendente = None
                aviso = "Ação cancelada, senhor."
                self.adicionar_ao_historico("assistant", aviso)
                return aviso
            else:
                return "⚠️ Ação pendente! Por favor, responda 'Sim' para executar ou 'Não' para cancelar."

        # 2. ROTEAMENTO
        decisao = self.router.classificar(pergunta)
        categoria = decisao.get("categoria", "CONVERSA")
        projetos_menc = decisao.get("projetos_mencionados", [])
        
        print(f"🧠 [Router]: {categoria} | Projetos detectados: {projetos_menc}")

        # 3. EXECUÇÃO
        if categoria == "ERRO_SISTEMA":
            msg_erro = "Senhor, os servidores da IA estão instáveis no momento. Por favor, tente novamente em instantes."
            self.adicionar_ao_historico("assistant", msg_erro)
            return msg_erro

        elif categoria == "ACAO_SISTEMA":
            return self._processar_acao(pergunta)
            
        elif categoria == "CONSULTA_ZOHO":
            return self._processar_consulta(pergunta, projetos_menc)
            
        elif categoria == "MEMORIA":
            if projetos_menc:
                dados = self.buscar_dados_projetos(projetos_menc)
                if dados:
                    proj = dados[0] 
                    
                    # 1. SOLUÇÃO DA PASTA: Garante a criação física da pasta ao anotar!
                    self.garantir_pasta_projeto(proj['name'])
                    
                    # 2. SOLUÇÃO DO TRAVAMENTO: Prints de rastreio para você não ficar às cegas
                    print(f"   ⏳ [Rastreio] Enviando nota para a API do Google resumir...")
                    nota_limpa = self.extrair_texto_nota(pergunta, proj['name'])
                    
                    print(f"   💾 [Rastreio] Salvando no Banco de Dados: '{nota_limpa}'...")
                    self.db.salvar_nota(proj['id'], proj['name'], nota_limpa) 
                    
                    res = f"✅ Anotação salva no banco de dados para o projeto {proj['name']} e pasta do projeto verificada/criada."
                    self.adicionar_ao_historico("assistant", res)
                    return res
            return "Senhor, não consegui identificar a qual projeto essa anotação pertence."

    def _processar_acao(self, pergunta, tentativas=3):
        prompt_acao = f"""O usuário quer executar uma ação no sistema.
Extraia os parâmetros estritos da frase e preencha o JSON da ferramenta apropriada.

ESQUEMAS JSON ESPERADOS:
- WhatsApp: {{"ferramenta": "enviar_whatsapp", "params": {{"contato": "Nome", "mensagem": "texto"}}}}
- Email: {{"ferramenta": "enviar_email", "params": {{"destinatario": "email", "assunto": "X", "corpo_html": "Y"}}}}
- Buscar Email: {{"ferramenta": "buscar_emails", "params": {{"query": "termo", "apenas_nao_lidos": true}}}}
- Clicar: {{"ferramenta": "clicar_elemento_visual", "params": {{"descricao_elemento": "X"}}}}
- Digitar: {{"ferramenta": "digitar_texto", "params": {{"texto": "X"}}}}

Frase: "{pergunta}"
Retorne APENAS o JSON válido."""

        for tentativa in range(tentativas):
            try:
                resp = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt_acao,
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.0)
                )
                comando_json = json.loads(resp.text)
                self.acao_pendente = comando_json
                
                ferramenta = comando_json.get("ferramenta")
                params = comando_json.get("params", {})
                detalhes = "\n".join([f"- {k.capitalize()}: {v}" for k, v in params.items()])
                msg = f"⏳ Preparando para executar: '{ferramenta}'.\nParâmetros:\n{detalhes}\n\nDevo prosseguir?"
                
                self.adicionar_ao_historico("assistant", msg)
                return msg
            except Exception as e:
                print(f"⚠️ [Extração JSON Error - Tentativa {tentativa + 1}/{tentativas}]: {e}")
                if tentativa < tentativas - 1:
                    time.sleep(2)
                else:
                    return "❌ Senhor, a API do Google está muito instável. Não consegui formatar a ação."

    def _processar_consulta(self, pergunta, projetos_menc):
        dados = self.buscar_dados_projetos(projetos_menc)
        if not dados and not projetos_menc: 
             dados = self.dados_projetos[:10]

        contexto_projetos = ""
        if dados:
            dados_enriquecidos = []
            for p in dados[:10]:
                p_completo = p.copy()
                
                # 1. Pega as notas do Banco SQLite (A parte Humana)
                p_completo['MEMORIA_GESTOR'] = self.db.buscar_notas_projeto(p.get('id'))
                
                # 2. Garante a Pasta Local (Integração com Sistema)
                self.garantir_pasta_projeto(p.get('name'))
                
                # Limpa a lista de tarefas para economizar tokens (a IA vai focar nos custom_fields agora)
                if 'tasks' in p_completo:
                    del p_completo['tasks']
                    
                dados_enriquecidos.append(p_completo)
                
            contexto_projetos = json.dumps(dados_enriquecidos, ensure_ascii=False)
        
        prompt = (
            f"{self.construir_contexto_conversa()}"
            f"DADOS DO SISTEMA (ZOHO/DB):\n{contexto_projetos}\n\n"
            f"PERGUNTA DO GESTOR: {pergunta}\n\n"
            "Responda baseada APENAS nos dados. Use as datas dos custom_fields para inferir o status e a MEMORIA_GESTOR para o contexto da operação."
        )
        
        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=self.instrucao_conversa, temperature=0.3)
        )
        
        self.adicionar_ao_historico("assistant", resp.text)
        return resp.text.strip()

    def _processar_conversa(self, pergunta):
        prompt = f"{self.construir_contexto_conversa()}\nPERGUNTA: {pergunta}"
        
        try:
            resp = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=self.instrucao_conversa, temperature=0.7)
            )
            
            # VALIDAÇÃO CONTRA O ERRO "NONE":
            texto_resposta = resp.text if resp.text else "Tudo operacional por aqui, senhor. Em que posso ajudar?"
            texto_resposta = texto_resposta.strip()
            
            self.adicionar_ao_historico("assistant", texto_resposta)
            return texto_resposta
            
        except Exception as e:
            print(f"⚠️ [Conversa Error]: {e}")
            msg_erro = "❌ Senhor, estou com dificuldades de conexão com meus servidores lógicos. Poderia repetir?"
            self.adicionar_ao_historico("assistant", msg_erro)
            return msg_erro

    def _executar_ferramenta(self, comando):
        nome = comando.get("ferramenta")
        params = comando.get("params", {})
        print(f"   ⚙️ Executando Mecanicamente: {nome}...")
        try:
            if nome == "buscar_emails":
                resultado = self.ferramentas.buscar_emails(**params)
            elif nome == "enviar_email":
                resultado = self.ferramentas.enviar_email(**params)
            elif nome == "clicar_elemento_visual":
                time.sleep(1)
                resultado = self.ferramentas.clicar_elemento_visual(params.get("descricao_elemento"))
            elif nome == "digitar_texto":
                resultado = self.ferramentas.digitar_texto(params.get("texto"))
            elif nome == "enviar_whatsapp":
                time.sleep(1)
                resultado = self.ferramentas.enviar_whatsapp(params.get("contato"), params.get("mensagem"))
            else:
                resultado = f"❌ Ferramenta '{nome}' não configurada."
            return f"Ação Concluída: {resultado}"
        except Exception as e:
            return f"Falha na execução mecânica: {e}"

    def limpar_historico(self):
        self.historico_conversa = []
        print("🧹 Histórico de conversa limpo.")