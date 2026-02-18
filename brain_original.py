import json
import os
import time
from google import genai
from google.genai import types
from config import Config
from datetime import datetime
from ferramentas import JarvisFerramentas  # <--- NOVA IMPORTAÇÃO

class JarvisBrain:
    def __init__(self):
        if not Config.GEMINI_KEY:
            raise ValueError("❌ Chave do Gemini não encontrada no arquivo .env!")
        
        self.client = genai.Client(api_key=Config.GEMINI_KEY)
        self.model_name = "gemini-flash-latest" 
        self.arquivo_memoria = "db_memoria.json"
        self.cache_nota_pendente = None 
        
        # Carrega dados
        self.dados_projetos = self.carregar_dados_zoho()
        self.memoria_local = self.carregar_memoria_local()
        
        # Inicializa os "Braços"
        self.ferramentas = JarvisFerramentas() # <--- INICIALIZAÇÃO DOS BRAÇOS
        
        data_hoje = datetime.now().strftime("%d/%m/%Y")

        # --- INSTRUÇÃO DE SISTEMA HÍBRIDA (GP + OPERADOR) ---
        self.instrucao_sistema = (
            f"Você é o Jarvis, assistente executivo da Animati. Hoje é {data_hoje}. "
            "Seu gestor é o Giovani. "
            "FONTE DE DADOS: Zoho Projects (Técnico) + Memória do Gestor (Contexto).\n\n"
            
            "--- PERFIL E REGRAS DE NEGÓCIO (ANIMATI) ---\n"
            "1. SEJA BREVE: Sem saudações longas. Vá direto ao ponto.\n"
            "2. FOCO NO GARGALO: Não liste o que está bom. Fale apenas do que trava o projeto.\n"
            "3. REGRA DE RESUMO: Se o projeto já está numa fase avançada (ex: Implantação), NÃO liste tarefas de fases anteriores (ex: Infra) a menos que solicitado.\n"
            "4. FLUXO: DEIP -> Infra -> Implantação (netRIS/PACS) -> Homologação -> Virada -> OA -> DPI.\n"
            "5. PRAZOS: netRIS (35d), PACS (30d), OA (15d).\n\n"
            "6. Ao usar enviar_whatsapp, use o nome EXATO do contato que o usuário falou, sem resumir ou alterar.\n"

            "--- SUAS FERRAMENTAS (AÇÃO NO MUNDO REAL) ---\n"
            "Além de responder, você pode executar ações. Se o usuário pedir uma ação, RESPONDA APENAS COM ESTE JSON:\n"
            "```json\n"
            "{\n"
            '  "ferramenta": "nome_da_funcao",\n'
            '  "params": { "parametro": "valor" }\n'
            "}\n"
            "```\n"
            "LISTA DE FERRAMENTAS:\n"
            "1. buscar_emails(query='texto', apenas_nao_lidos=True/False) -> Ler/Procurar e-mails.\n"
            "2. enviar_email(destinatario='email', assunto='titulo', corpo_html='texto') -> Escrever e-mails.\n"
            "3. clicar_elemento_visual(descricao_elemento='texto visual') -> Clicar na tela (Ex: 'Clique no botão X').\n"
            "4. digitar_texto(texto='mensagem') -> Digitar onde o cursor está.\n\n"
            "5. enviar_whatsapp(contato='Nome', mensagem='Texto') -> Use para mandar msg. Ex: 'Avise a Patricia que terminei'.\n\n"
            
            "--- DECISÃO FINAL ---\n"
            "- Pergunta sobre Projetos? -> Responda em TEXTO (Regras Animati).\n"
            "- Pedido de Ação/E-mail? -> Responda em JSON."
        )

    def carregar_dados_zoho(self):
        try:
            with open("db_projetos.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def carregar_memoria_local(self):
        if not os.path.exists(self.arquivo_memoria):
            with open(self.arquivo_memoria, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}  
        try:
            with open(self.arquivo_memoria, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def salvar_memoria(self, projeto_id, nota):
        projeto_id = str(projeto_id)
        if not os.path.exists(self.arquivo_memoria):
             with open(self.arquivo_memoria, "w", encoding="utf-8") as f:
                json.dump({}, f)

        timestamp = datetime.now().strftime("%d/%m")
        nova_entrada = f"[{timestamp}] {nota}"
        
        if projeto_id not in self.memoria_local:
            self.memoria_local[projeto_id] = []
        
        self.memoria_local[projeto_id].append(nova_entrada)
        
        with open(self.arquivo_memoria, "w", encoding="utf-8") as f:
            json.dump(self.memoria_local, f, indent=4, ensure_ascii=False)
        
        return f"Anotado no projeto {projeto_id}."

    def extrair_texto_nota(self, frase_usuario, nome_projeto_detectado):
        prompt_extracao = (
            f"Frase: '{frase_usuario}'. Contexto: '{nome_projeto_detectado}'. "
            "Extraia apenas o fato a ser anotado. Responda curto."
        )
        resp = self.client.models.generate_content(
            model=self.model_name, contents=prompt_extracao
        )
        return resp.text.strip()

    def roteador_inteligente(self, pergunta):
        pergunta_limpa = pergunta.lower()
        
        gatilhos_escrita = ['anote', 'lembre', 'adicionar nota', 'gravar', 'registre']
        modo_escrita = any(g in pergunta_limpa for g in gatilhos_escrita)

        gatilhos_globais = ['quais', 'quantos', 'listar', 'relatório', 'resumo', 'todos', 'geral']
        
        if any(gatilho in pergunta_limpa for gatilho in gatilhos_globais) and not modo_escrita:
             return self.gerar_visao_helicoptero(self.dados_projetos), None, False

        numeros = [p for p in pergunta_limpa.split() if p.isdigit()]
        for num in numeros:
            for proj in self.dados_projetos:
                if num in proj.get("name", ""):
                    return [proj], None, modo_escrita

        palavras_ignoradas = ['anote', 'que', 'sobre', 'projeto', 'no', 'na', 'o', 'a', 'para', 'fase', 'status', 'jarvis', 'situacao', 'situação', 'clique', 'mande', 'leia']
        termos = [p for p in pergunta_limpa.split() if len(p) > 3 and p not in palavras_ignoradas]
        
        projetos_encontrados = []
        if termos:
            for proj in self.dados_projetos:
                if any(t in proj.get("name", "").lower() for t in termos):
                    projetos_encontrados.append(proj)

        if len(projetos_encontrados) == 1:
            return projetos_encontrados, None, modo_escrita
        elif len(projetos_encontrados) > 1:
            nomes = "\n".join([f"- {p['name']}" for p in projetos_encontrados])
            return projetos_encontrados, f"Qual deles? (Diga o código):\n{nomes}", modo_escrita
        
        if modo_escrita:
            return None, "Qual projeto? Diga o nome ou código.", False
            
        # Se não achou projeto específico, retorna visão geral (útil se for pergunta de e-mail/ação)
        return self.gerar_visao_helicoptero(self.dados_projetos), None, False

    def gerar_visao_helicoptero(self, lista):
        dados = []
        for p in lista:
            notas = self.memoria_local.get(str(p['id']), [])
            fase = "Indefinida"
            for t in p.get("tasks", []):
                status = str(t.get("status", "")).lower()
                if status not in ["completed", "concluído", "cancelled", "fechado"]:
                    fase = t.get("tasklist", "Geral")
                    break
            
            dados.append({
                "id": p['id'],
                "name": p['name'],
                "percent": p['percent_complete'],
                "fase_real": fase,
                "NOTAS": notas 
            })
        return dados

    def analisar(self, pergunta):
        if not self.dados_projetos: return "Sem dados."

        print(f"\n🧠 Processando...")

        # 1. Lógica de Memória Pendente (Prioridade)
        if self.cache_nota_pendente:
            numeros = [p for p in pergunta.split() if p.isdigit()]
            for num in numeros:
                for proj in self.dados_projetos:
                    if num in proj.get("name", ""):
                        res = self.salvar_memoria(proj['id'], self.cache_nota_pendente)
                        self.cache_nota_pendente = None
                        return res
            self.cache_nota_pendente = None
            return "Operação cancelada. Código não reconhecido."

        # 2. Roteamento (Identifica Projetos Envolvidos)
        projetos_alvo, msg_erro, eh_escrita = self.roteador_inteligente(pergunta)
        
        if msg_erro:
            if eh_escrita and isinstance(projetos_alvo, list):
                texto_nota = self.extrair_texto_nota(pergunta, "Múltiplos")
                self.cache_nota_pendente = texto_nota
                return msg_erro 
            return msg_erro

        if eh_escrita:
            nota_limpa = self.extrair_texto_nota(pergunta, projetos_alvo[0]['name'])
            return self.salvar_memoria(projetos_alvo[0]['id'], nota_limpa)

        # 3. Preparação do Prompt (Leitura ou Ação)
        dados_enriquecidos = []
        # Limita quantidade para não estourar tokens se for lista geral
        lista_para_contexto = projetos_alvo[:15] if isinstance(projetos_alvo, list) else projetos_alvo
        
        for p in lista_para_contexto:
            p_completo = p.copy()
            p_completo['MEMORIA_GESTOR'] = self.memoria_local.get(str(p.get('id')), [])
            dados_enriquecidos.append(p_completo)

        contexto = json.dumps(dados_enriquecidos, ensure_ascii=False)
        
        prompt = (
            f"--- CONTEXTO ATUAL (PROJETOS) ---\n{contexto}\n\n"
            f"--- SOLICITAÇÃO ---\n{pergunta}\n\n"
            "Se for pergunta sobre projeto, use HTML (<b>, <br>). "
            "Se for pedido de ação (email, clique), use JSON."
        )
        
        try:
            resp = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.instrucao_sistema, temperature=0.1
                )
            )
            resposta_texto = resp.text.strip()

            # 4. O "Gatilho" da Ação (Detecção de JSON)
            if "```json" in resposta_texto:
                return self.executar_ferramenta(resposta_texto)
            elif resposta_texto.startswith("{") and "ferramenta" in resposta_texto:
                return self.executar_ferramenta(resposta_texto)

            return resposta_texto
            
        except Exception as e:
            return f"Erro: {e}"

    def executar_ferramenta(self, json_texto):
        """Executor dos Braços"""
        try:
            json_limpo = json_texto.replace("```json", "").replace("```", "").strip()
            comando = json.loads(json_limpo)
            
            nome = comando.get("ferramenta")
            params = comando.get("params", {})
            
            print(f"   ⚙️ Ativando Ferramenta: {nome}...")

            if nome == "buscar_emails":
                return self.ferramentas.buscar_emails(**params)
            elif nome == "enviar_email":
                return self.ferramentas.enviar_email(**params)
            elif nome == "clicar_elemento_visual":
                time.sleep(1) # Tempo para usuário soltar microfone
                return self.ferramentas.clicar_elemento_visual(params.get("descricao_elemento"))
            elif nome == "digitar_texto":
                return self.ferramentas.digitar_texto(params.get("texto"))
            elif nome == "enviar_whatsapp":  # <--- NOVO
                time.sleep(1) # Tempo para você soltar o microfone
                return self.ferramentas.enviar_whatsapp(
                    params.get("contato"), 
                    params.get("mensagem")
                )
            else:
                return f"Ferramenta {nome} não encontrada."

        except Exception as e:
            return f"Erro ao executar ação: {e}"