"""
Brain V2 com Sistema de Logging Integrado
Versão com monitoramento completo de erros e eventos
"""

import json
import os
import time
import traceback
from google import genai
from google.genai import types
from config import Config
from datetime import datetime
from ferramentas import ApexFerramentas
from logger import get_logger

# Inicializa logger
log = get_logger("brain_v2")

class ApexBrain:
    def __init__(self):
        log.info("="*70)
        log.info("INICIALIZANDO APEX BRAIN V2")
        log.info("="*70)
        
        try:
            if not Config.GEMINI_KEY:
                log.critical("Chave do Gemini não encontrada no .env!")
                raise ValueError("❌ Chave do Gemini não encontrada no arquivo .env!")
            
            log.debug(f"API Key Gemini configurada: {Config.GEMINI_KEY[:15]}...")
            
            self.client = genai.Client(api_key=Config.GEMINI_KEY)
            self.model_name = "gemini-flash-latest"
            log.info(f"Modelo AI: {self.model_name}")
            
            self.arquivo_memoria = "db_memoria.json"
            self.cache_nota_pendente = None 
            
            # Carrega dados
            log.debug("Carregando dados do Zoho Projects...")
            self.dados_projetos = self.carregar_dados_zoho()
            log.info(f"✅ Projetos carregados: {len(self.dados_projetos)}")
            
            log.debug("Carregando memória local (anotações)...")
            self.memoria_local = self.carregar_memoria_local()
            total_notas = sum(len(v) for v in self.memoria_local.values())
            log.info(f"✅ Anotações carregadas: {total_notas} em {len(self.memoria_local)} projetos")
            
            # Inicializa as "Ferramentas"
            log.debug("Inicializando módulo de ferramentas...")
            self.ferramentas = ApexFerramentas()
            log.info("✅ Ferramentas (email, whatsapp, automação) prontas")
            
            # Histórico de Conversa (Memória de Curto Prazo)
            self.historico_conversa = []
            self.max_historico = 10
            log.debug(f"Memória conversacional configurada: {self.max_historico} interações")
            
            data_hoje = datetime.now().strftime("%d/%m/%Y às %H:%M")
            
            # Instrução do sistema
            self.instrucao_sistema = self._construir_instrucao_sistema(data_hoje)
            log.debug(f"Sistema de instrução construído: {len(self.instrucao_sistema)} caracteres")
            
            log.info(f"🎉 Brain V2 inicializado com sucesso em {data_hoje}")
            log.info("="*70)
            
        except Exception as e:
            log.critical("FALHA CRÍTICA na inicialização do Brain!", exception=e)
            raise

    def _construir_instrucao_sistema(self, data_hoje):
        """Constrói a instrução de sistema para a IA"""
        log.debug("Construindo prompt de instrução do sistema...")
        
        return f"""Você é APEX, o assistente executivo pessoal do Giovani na Animati.
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
- Se projeto já está em fase avançada (ex: Implantação), NÃO cite tarefas de fases anteriores (ex: Infra)

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
        """Carrega projetos do arquivo JSON"""
        try:
            caminho = "db_projetos.json"
            if not os.path.exists(caminho):
                log.warning(f"Arquivo {caminho} não encontrado")
                return []
                
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                log.debug(f"Arquivo {caminho} lido com sucesso: {len(dados)} projetos")
                return dados
                
        except json.JSONDecodeError as e:
            log.error(f"Erro ao decodificar JSON de {caminho}", exception=e)
            return []
        except Exception as e:
            log.error(f"Erro inesperado ao carregar dados do Zoho", exception=e)
            return []

    def carregar_memoria_local(self):
        """Carrega anotações do gestor"""
        try:
            if not os.path.exists(self.arquivo_memoria):
                log.debug(f"Arquivo de memória não existe, criando novo: {self.arquivo_memoria}")
                with open(self.arquivo_memoria, "w", encoding="utf-8") as f:
                    json.dump({}, f)
                return {}
                
            with open(self.arquivo_memoria, "r", encoding="utf-8") as f:
                dados = json.load(f)
                log.debug(f"Memória carregada: {len(dados)} projetos com anotações")
                return dados
                
        except json.JSONDecodeError as e:
            log.error("Erro ao decodificar memória JSON", exception=e)
            return {}
        except Exception as e:
            log.error("Erro ao carregar memória local", exception=e)
            return {}

    def adicionar_ao_historico(self, role, content):
        """Adiciona mensagem ao histórico de conversa"""
        try:
            self.historico_conversa.append({
                'role': role,
                'content': content,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            
            log.debug(f"Mensagem adicionada ao histórico: {role} - {content[:50]}...")
            
            # Limita tamanho
            if len(self.historico_conversa) > self.max_historico * 2:
                removidos = len(self.historico_conversa) - (self.max_historico * 2)
                self.historico_conversa = self.historico_conversa[-self.max_historico * 2:]
                log.debug(f"Histórico limitado: {removidos} mensagens antigas removidas")
                
        except Exception as e:
            log.error("Erro ao adicionar ao histórico", exception=e)

    def construir_contexto_conversa(self):
        """Monta o histórico formatado para a IA"""
        try:
            if not self.historico_conversa:
                log.debug("Histórico vazio, sem contexto conversacional")
                return ""
            
            contexto = "\n--- HISTÓRICO DA CONVERSA ATUAL ---\n"
            ultimas_msg = self.historico_conversa[-6:]  # Últimas 3 interações
            
            for msg in ultimas_msg:
                role_label = "GIOVANI" if msg["role"] == "user" else "APEX"
                contexto += f"[{msg['timestamp']}] {role_label}: {msg['content'][:200]}\n"
            
            contexto += "--- FIM DO HISTÓRICO ---\n\n"
            log.debug(f"Contexto conversacional construído: {len(ultimas_msg)} mensagens")
            return contexto
            
        except Exception as e:
            log.error("Erro ao construir contexto conversacional", exception=e)
            return ""

    def salvar_memoria(self, projeto_id, nota):
        """Salva anotação sobre um projeto"""
        try:
            projeto_id = str(projeto_id)
            log.info(f"Salvando anotação no projeto {projeto_id}")
            log.debug(f"Nota: {nota}")
            
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
            
            log.info(f"✅ Anotação salva com sucesso no projeto {projeto_id}")
            return f"✅ Anotado no projeto {projeto_id}."
            
        except Exception as e:
            log.error(f"Erro ao salvar memória do projeto {projeto_id}", exception=e)
            return f"❌ Erro ao salvar anotação: {str(e)}"

    def extrair_texto_nota(self, frase_usuario, nome_projeto_detectado):
        """Extrai o texto da nota usando IA"""
        try:
            log.debug(f"Extraindo nota de: {frase_usuario[:100]}")
            
            prompt_extracao = (
                f"Frase: '{frase_usuario}'. Contexto: '{nome_projeto_detectado}'. "
                "Extraia apenas o fato a ser anotado. Responda curto."
            )
            
            resp = self.client.models.generate_content(
                model=self.model_name, contents=prompt_extracao
            )
            
            nota = resp.text.strip()
            log.debug(f"Nota extraída: {nota}")
            return nota
            
        except Exception as e:
            log.error("Erro ao extrair texto da nota", exception=e)
            return frase_usuario  # Fallback: usa a frase original

    def roteador_inteligente(self, pergunta):
        """Identifica projetos mencionados"""
        try:
            log.debug(f"Roteando pergunta: {pergunta[:100]}")
            pergunta_limpa = pergunta.lower()
            
            # Detecta modo de escrita
            gatilhos_escrita = ['anote', 'lembre', 'adicionar nota', 'gravar', 'registre']
            modo_escrita = any(g in pergunta_limpa for g in gatilhos_escrita)
            
            if modo_escrita:
                log.debug("Modo ESCRITA detectado")

            # Detecta consultas globais
            gatilhos_globais = ['quais', 'quantos', 'listar', 'relatório', 'resumo', 'todos', 'geral']
            
            if any(gatilho in pergunta_limpa for gatilho in gatilhos_globais) and not modo_escrita:
                log.info("Consulta GLOBAL detectada")
                return self.gerar_visao_helicoptero(self.dados_projetos), None, False

            # Busca por número de projeto
            numeros = [p for p in pergunta_limpa.split() if p.isdigit()]
            log.debug(f"Números encontrados: {numeros}")
            
            for num in numeros:
                for proj in self.dados_projetos:
                    if num in proj.get("name", ""):
                        log.info(f"Projeto identificado por número: {proj.get('name')}")
                        return [proj], None, modo_escrita

            # Busca por palavras-chave
            palavras_ignoradas = ['anote', 'que', 'sobre', 'projeto', 'no', 'na', 'o', 'a', 'para', 
                                  'fase', 'status', 'apex', 'situacao', 'situação', 'clique', 
                                  'mande', 'leia', 'email', 'whatsapp', 'mensagem']
            termos = [p for p in pergunta_limpa.split() if len(p) > 3 and p not in palavras_ignoradas]
            
            log.debug(f"Termos de busca: {termos}")
            
            projetos_encontrados = []
            if termos:
                for proj in self.dados_projetos:
                    if any(t in proj.get("name", "").lower() for t in termos):
                        projetos_encontrados.append(proj)

            if len(projetos_encontrados) == 1:
                log.info(f"Projeto único identificado: {projetos_encontrados[0].get('name')}")
                return projetos_encontrados, None, modo_escrita
            elif len(projetos_encontrados) > 1:
                log.warning(f"Múltiplos projetos encontrados: {len(projetos_encontrados)}")
                nomes = "\n".join([f"- {p['name']}" for p in projetos_encontrados])
                return projetos_encontrados, f"Qual deles? (Diga o código):\n{nomes}", modo_escrita
            
            if modo_escrita:
                log.warning("Modo escrita sem projeto identificado")
                return None, "Qual projeto? Diga o nome ou código.", False
            
            log.debug("Nenhum projeto específico identificado")
            return None, None, False
            
        except Exception as e:
            log.error("Erro no roteador inteligente", exception=e)
            return None, "Erro ao identificar projeto", False

    def gerar_visao_helicoptero(self, lista):
        """Gera visão geral dos projetos"""
        try:
            log.debug(f"Gerando visão geral de {len(lista)} projetos")
            dados = []
            
            for p in lista[:15]:
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
            
            log.debug(f"Visão geral gerada: {len(dados)} projetos processados")
            return dados
            
        except Exception as e:
            log.error("Erro ao gerar visão helicoptero", exception=e)
            return []

    def analisar(self, pergunta):
        """Método principal - COM LOGGING COMPLETO"""
        log.info("━"*70)
        log.info("NOVA SOLICITAÇÃO RECEBIDA")
        log.info(f"Pergunta: {pergunta}")
        log.info("━"*70)
        
        try:
            # Validação inicial
            if not self.dados_projetos and "email" not in pergunta.lower() and "whatsapp" not in pergunta.lower():
                log.warning("Sem dados de projetos e não é comando de ação")
                return "Sem dados de projetos disponíveis."

            print(f"\n🧠 Processando: '{pergunta[:60]}...'")

            # Adiciona ao histórico
            self.adicionar_ao_historico("user", pergunta)

            # 1. Lógica de Memória Pendente
            if self.cache_nota_pendente:
                log.debug(f"Processando nota pendente: {self.cache_nota_pendente}")
                numeros = [p for p in pergunta.split() if p.isdigit()]
                
                for num in numeros:
                    for proj in self.dados_projetos:
                        if num in proj.get("name", ""):
                            res = self.salvar_memoria(proj['id'], self.cache_nota_pendente)
                            self.cache_nota_pendente = None
                            self.adicionar_ao_historico("assistant", res)
                            log.info("Nota pendente salva")
                            return res
                
                self.cache_nota_pendente = None
                msg = "Operação cancelada. Código não reconhecido."
                self.adicionar_ao_historico("assistant", msg)
                log.warning("Código não reconhecido, nota cancelada")
                return msg

            # 2. Roteamento
            log.debug("Iniciando roteamento...")
            projetos_alvo, msg_erro, eh_escrita = self.roteador_inteligente(pergunta)
            
            if msg_erro:
                log.warning(f"Erro no roteamento: {msg_erro}")
                if eh_escrita and isinstance(projetos_alvo, list):
                    texto_nota = self.extrair_texto_nota(pergunta, "Múltiplos")
                    self.cache_nota_pendente = texto_nota
                    self.adicionar_ao_historico("assistant", msg_erro)
                    return msg_erro 
                self.adicionar_ao_historico("assistant", msg_erro)
                return msg_erro

            if eh_escrita:
                log.info("Processando anotação...")
                nota_limpa = self.extrair_texto_nota(pergunta, projetos_alvo[0]['name'])
                res = self.salvar_memoria(projetos_alvo[0]['id'], nota_limpa)
                self.adicionar_ao_historico("assistant", res)
                return res

            # 3. Preparação do Contexto
            log.debug("Construindo contexto...")
            contexto_conversa = self.construir_contexto_conversa()
            
            contexto_projetos = ""
            if projetos_alvo:
                dados_enriquecidos = []
                lista_para_contexto = projetos_alvo[:10] if isinstance(projetos_alvo, list) else projetos_alvo
                
                log.debug(f"Enriquecendo {len(lista_para_contexto) if isinstance(lista_para_contexto, list) else 1} projeto(s)")
                
                for p in lista_para_contexto:
                    p_completo = p.copy()
                    p_completo['MEMORIA_GESTOR'] = self.memoria_local.get(str(p.get('id')), [])
                    dados_enriquecidos.append(p_completo)

                contexto_projetos = f"\n--- DADOS DOS PROJETOS RELEVANTES ---\n{json.dumps(dados_enriquecidos, ensure_ascii=False)}\n"
                log.debug(f"Contexto de projetos: {len(contexto_projetos)} chars")
            
            # Monta prompt
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
            
            log.debug(f"Prompt construído: {len(prompt)} chars")
            log.debug("Chamando Gemini API...")
            
            resp = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.instrucao_sistema, 
                    temperature=0.3
                )
            )
            
            log.info("✅ Resposta recebida da API")
            resposta_texto = resp.text.strip()
            log.debug(f"Resposta (preview): {resposta_texto[:200]}...")

            # Adiciona ao histórico
            self.adicionar_ao_historico("assistant", resposta_texto[:500])

            # 4. Detecta ação
            if "```json" in resposta_texto or (resposta_texto.startswith("{") and "ferramenta" in resposta_texto):
                log.info("Resposta identificada como AÇÃO (JSON)")
                return self.executar_ferramenta(resposta_texto)

            log.info("Resposta identificada como CONSULTA (texto)")
            log.info("✅ Processamento concluído com sucesso")
            log.info("━"*70)
            return resposta_texto
            
        except Exception as e:
            log.critical("❌ ERRO CRÍTICO no método analisar()", exception=e)
            log.error(f"Pergunta que causou erro: {pergunta}")
            log.error(f"Traceback completo:\n{traceback.format_exc()}")
            
            erro_user = f"❌ Erro ao processar: {type(e).__name__}. Verifique os logs em 'logs/erros.log'"
            self.adicionar_ao_historico("assistant", erro_user)
            return erro_user

    def executar_ferramenta(self, json_texto):
        """Executor das Ferramentas"""
        try:
            log.info("Executando ferramenta...")
            log.debug(f"JSON recebido: {json_texto[:200]}")
            
            json_limpo = json_texto.replace("```json", "").replace("```", "").strip()
            comando = json.loads(json_limpo)
            
            nome = comando.get("ferramenta")
            params = comando.get("params", {})
            
            log.info(f"Ferramenta: {nome}")
            log.debug(f"Parâmetros: {params}")
            
            print(f"   ⚙️ Ativando Ferramenta: {nome}...")
            log.registrar_acao(nome, str(params))

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
                log.error(f"Ferramenta não encontrada: {nome}")
            
            log.info(f"✅ Ferramenta executada: {resultado[:100]}")
            self.adicionar_ao_historico("assistant", f"[AÇÃO: {nome}] {resultado}")
            return resultado

        except json.JSONDecodeError as e:
            log.error("Erro ao decodificar JSON da ferramenta", exception=e)
            log.error(f"JSON problemático: {json_texto}")
            return f"❌ Erro no formato JSON: {str(e)}"
        except Exception as e:
            log.error("Erro ao executar ferramenta", exception=e)
            return f"❌ Erro na execução: {str(e)}"

    def limpar_historico(self):
        """Limpa o histórico de conversa"""
        log.info("Limpando histórico de conversa")
        self.historico_conversa = []
        log.debug("Histórico limpo")
