import json
import os
import time
from google import genai
from google.genai import types
from config import Config
from datetime import datetime
from ferramentas import ApexFerramentas

class ApexBrain:
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
        
        # Inicializa as "Ferramentas"
        self.ferramentas = ApexFerramentas()
        
        # **NOVA**: Histórico de Conversa (Memória de Curto Prazo)
        self.historico_conversa = []
        self.max_historico = 10  # Mantém últimas 10 interações
        
        data_hoje = datetime.now().strftime("%d/%m/%Y às %H:%M")

        # --- INSTRUÇÃO DE SISTEMA MELHORADA (CONVERSACIONAL) ---
        self.instrucao_sistema = f"""Você é APEX, o assistente executivo pessoal do Giovani na Animati.
Data/Hora atual: {data_hoje}

# PERSONALIDADE E TOM
- Seja DIRETO, CONCISO e NATURAL como em uma conversa real
- Use tom profissional mas amigável (como no filme Homem de Ferro)
- Evite saudações longas ou formalidades excessivas
- NUNCA repita informações já ditas na conversa
- Se não souber algo, admita honestamente

# FONTES DE DADOS
1. **Zoho Projects**: Dados técnicos dos projetos (tarefas, %, prazos)
2. **Memória do Gestor**: Anotações contextuais que Giovani fez sobre os projetos
3. **Histórico da Conversa**: O que já foi discutido nesta sessão

# REGRAS DE NEGÓCIO (ANIMATI)
- Fluxo: DEIP → Infra → Implantação (netRIS/PACS) → Homologação → Virada → OA → DPI
- Prazos: netRIS (35d), PACS (30d), OA (15d)
- FOQUE NO GARGALO: Fale apenas do que trava/atrasa, não liste tudo que está ok
- Se projeto já está em fase avançada (ex: Implantação), NÃO cite tarefas de fases antigas (ex: Infra)

# DETECÇÃO DE INTENÇÕES
Você deve identificar automaticamente a intenção do usuário e agir:

## INTENÇÕES DE CONSULTA (Responda em texto natural)
- Perguntas sobre status de projetos
- Pedidos de resumo/relatório
- Análises de situação
- Comparações entre projetos

## INTENÇÕES DE AÇÃO (Execute via ferramentas)
Quando o usuário pedir para FAZER algo, use JSON discretamente:

**EMAIL**: "envie email", "mande um email", "comunique por email"
→ {{"ferramenta": "enviar_email", "params": {{"destinatario": "email", "assunto": "X", "corpo_html": "Y"}}}}

**BUSCAR EMAIL**: "veja meus emails", "tem algum email sobre X", "checa o email"
→ {{"ferramenta": "buscar_emails", "params": {{"query": "termo", "apenas_nao_lidos": true/false}}}}

**WHATSAPP**: "manda mensagem pra X", "avisa a Patricia", "fala pro João"
→ {{"ferramenta": "enviar_whatsapp", "params": {{"contato": "Nome Exato", "mensagem": "texto"}}}}

**CLICAR NA TELA**: "clica no botão X", "abre o programa Y"
→ {{"ferramenta": "clicar_elemento_visual", "params": {{"descricao_elemento": "descrição visual"}}}}

**DIGITAR**: "escreve X", "digita Y"
→ {{"ferramenta": "digitar_texto", "params": {{"texto": "conteúdo"}}}}

# IMPORTANTE
- Para ações de WhatsApp, use o NOME EXATO mencionado pelo usuário
- Não force JSON se o usuário só quer conversar
- Adapte sua resposta ao contexto da conversa anterior
- Se for uma pergunta de acompanhamento, considere o histórico

# ANOTAÇÕES NA MEMÓRIA
Se o usuário disser "anote que...", "lembre que...", "registre que...":
1. Identifique o projeto mencionado
2. Extraia o fato relevante
3. Confirme a anotação de forma breve
"""

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

    def adicionar_ao_historico(self, role, content):
        """Adiciona mensagem ao histórico de conversa"""
        self.historico_conversa.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Limita tamanho do histórico
        if len(self.historico_conversa) > self.max_historico * 2:  # *2 porque cada interação tem user+assistant
            self.historico_conversa = self.historico_conversa[-self.max_historico * 2:]

    def construir_contexto_conversa(self):
        """Monta o histórico formatado para a IA"""
        if not self.historico_conversa:
            return ""
        
        contexto = "\n--- HISTÓRICO DA CONVERSA ATUAL ---\n"
        for msg in self.historico_conversa[-6:]:  # Últimas 3 interações
            role_label = "GIOVANI" if msg["role"] == "user" else "APEX"
            contexto += f"[{msg['timestamp']}] {role_label}: {msg['content'][:200]}\n"
        contexto += "--- FIM DO HISTÓRICO ---\n\n"
        return contexto

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
        
        return f"✅ Anotado no projeto {projeto_id}."

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
        """Identifica projetos mencionados na pergunta"""
        pergunta_limpa = pergunta.lower()
        
        # Detecta modo de escrita
        gatilhos_escrita = ['anote', 'lembre', 'adicionar nota', 'gravar', 'registre']
        modo_escrita = any(g in pergunta_limpa for g in gatilhos_escrita)

        # Detecta consultas globais
        gatilhos_globais = ['quais', 'quantos', 'listar', 'relatório', 'resumo', 'todos', 'geral']
        
        if any(gatilho in pergunta_limpa for gatilho in gatilhos_globais) and not modo_escrita:
             return self.gerar_visao_helicoptero(self.dados_projetos), None, False

        # Busca por número de projeto
        numeros = [p for p in pergunta_limpa.split() if p.isdigit()]
        for num in numeros:
            for proj in self.dados_projetos:
                if num in proj.get("name", ""):
                    return [proj], None, modo_escrita

        # Busca por palavras-chave do nome
        palavras_ignoradas = ['anote', 'que', 'sobre', 'projeto', 'no', 'na', 'o', 'a', 'para', 
                              'fase', 'status', 'apex', 'situacao', 'situação', 'clique', 
                              'mande', 'leia', 'email', 'whatsapp', 'mensagem']
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
            
        # Se não achou projeto específico, retorna None para análise geral
        return None, None, False

    def gerar_visao_helicoptero(self, lista):
        dados = []
        for p in lista[:15]:  # Limita para não estourar tokens
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
        """Método principal de análise - MELHORADO"""
        if not self.dados_projetos and "email" not in pergunta.lower() and "whatsapp" not in pergunta.lower():
            return "Sem dados de projetos disponíveis."

        print(f"\n🧠 Processando: '{pergunta[:60]}...'")

        # Adiciona pergunta ao histórico
        self.adicionar_ao_historico("user", pergunta)

        # 1. Lógica de Memória Pendente
        if self.cache_nota_pendente:
            numeros = [p for p in pergunta.split() if p.isdigit()]
            for num in numeros:
                for proj in self.dados_projetos:
                    if num in proj.get("name", ""):
                        res = self.salvar_memoria(proj['id'], self.cache_nota_pendente)
                        self.cache_nota_pendente = None
                        self.adicionar_ao_historico("assistant", res)
                        return res
            self.cache_nota_pendente = None
            msg = "Operação cancelada. Código não reconhecido."
            self.adicionar_ao_historico("assistant", msg)
            return msg

        # 2. Roteamento (Identifica Projetos)
        projetos_alvo, msg_erro, eh_escrita = self.roteador_inteligente(pergunta)
        
        if msg_erro:
            if eh_escrita and isinstance(projetos_alvo, list):
                texto_nota = self.extrair_texto_nota(pergunta, "Múltiplos")
                self.cache_nota_pendente = texto_nota
                self.adicionar_ao_historico("assistant", msg_erro)
                return msg_erro 
            self.adicionar_ao_historico("assistant", msg_erro)
            return msg_erro

        if eh_escrita:
            nota_limpa = self.extrair_texto_nota(pergunta, projetos_alvo[0]['name'])
            res = self.salvar_memoria(projetos_alvo[0]['id'], nota_limpa)
            self.adicionar_ao_historico("assistant", res)
            return res

        # 3. Preparação do Contexto
        contexto_conversa = self.construir_contexto_conversa()
        
        # Monta dados dos projetos se aplicável
        contexto_projetos = ""
        if projetos_alvo:
            dados_enriquecidos = []
            lista_para_contexto = projetos_alvo[:10] if isinstance(projetos_alvo, list) else projetos_alvo
            
            for p in lista_para_contexto:
                p_completo = p.copy()
                p_completo['MEMORIA_GESTOR'] = self.memoria_local.get(str(p.get('id')), [])
                dados_enriquecidos.append(p_completo)

            contexto_projetos = f"\n--- DADOS DOS PROJETOS RELEVANTES ---\n{json.dumps(dados_enriquecidos, ensure_ascii=False)}\n"
        
        # Monta prompt final
        prompt = (
            f"{contexto_conversa}"
            f"{contexto_projetos}"
            f"\n--- SOLICITAÇÃO ATUAL ---\n{pergunta}\n\n"
            "INSTRUÇÕES:\n"
            "- Se for uma pergunta sobre projetos: responda em texto natural, direto e conversacional\n"
            "- Se for um pedido de AÇÃO (email, whatsapp, clicar): responda APENAS com o JSON da ferramenta\n"
            "- Considere o histórico da conversa para dar contexto às suas respostas\n"
            "- NÃO repita informações já mencionadas anteriormente\n"
        )
        
        try:
            resp = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.instrucao_sistema, 
                    temperature=0.3  # Mais criativo para conversa natural
                )
            )
            resposta_texto = resp.text.strip()

            # Adiciona resposta ao histórico
            self.adicionar_ao_historico("assistant", resposta_texto[:500])  # Limita tamanho no histórico

            # 4. Detecta se é ação (JSON)
            if "```json" in resposta_texto or (resposta_texto.startswith("{") and "ferramenta" in resposta_texto):
                return self.executar_ferramenta(resposta_texto)

            return resposta_texto
            
        except Exception as e:
            erro_msg = f"Erro no processamento: {e}"
            self.adicionar_ao_historico("assistant", erro_msg)
            return erro_msg

    def executar_ferramenta(self, json_texto):
        """Executor das Ferramentas"""
        try:
            json_limpo = json_texto.replace("```json", "").replace("```", "").strip()
            comando = json.loads(json_limpo)
            
            nome = comando.get("ferramenta")
            params = comando.get("params", {})
            
            print(f"   ⚙️ Ativando Ferramenta: {nome}...")

            resultado = None
            
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
                resultado = self.ferramentas.enviar_whatsapp(
                    params.get("contato"), 
                    params.get("mensagem")
                )
            else:
                resultado = f"❌ Ferramenta '{nome}' não encontrada."
            
            # Adiciona resultado ao histórico
            self.adicionar_ao_historico("assistant", f"[AÇÃO EXECUTADA: {nome}] {resultado}")
            return resultado

        except Exception as e:
            erro = f"Erro ao executar ação: {e}"
            self.adicionar_ao_historico("assistant", erro)
            return erro

    def limpar_historico(self):
        """Limpa o histórico de conversa"""
        self.historico_conversa = []
        print("🧹 Histórico de conversa limpo.")
