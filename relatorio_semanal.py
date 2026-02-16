import json
import time
from datetime import datetime, timedelta
from brain import JarvisBrain
from correio import JarvisEmail
from tracker import obter_comparativo
from config import Config

def parse_data_zoho(data_str):
    """Tenta converter datas do Zoho (MM-DD-YYYY ou YYYY-MM-DD)"""
    if not data_str: return None
    formatos = ["%m-%d-%Y", "%Y-%m-%d", "%d/%m/%Y"]
    for fmt in formatos:
        try:
            return datetime.strptime(data_str, fmt)
        except ValueError:
            continue
    return None

def gerar_relatorio_cobranca():
    print("="*50)
    print("   ROBÔ DE COBRANÇA SEMANAL (OTIMIZADO)")
    print("="*50)
    
    # 1. Obter Dados Locais
    try:
        with open("db_projetos.json", "r", encoding="utf-8") as f:
            projetos = json.load(f)
    except:
        print("Erro ao ler projetos.")
        return

    # 2. Definir Período
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday()) 
    fim_semana = inicio_semana + timedelta(days=4)
    
    print(f"📅 Analisando período: {inicio_semana.strftime('%d/%m')} a {fim_semana.strftime('%d/%m')}")

    # 3. FILTRAGEM VIA PYTHON (Para economizar Tokens da IA)
    # Em vez de mandar o JSON bruto, criamos strings resumidas
    
    texto_vencidas = ""
    texto_estagnados = ""
    texto_evolucao = ""
    
    # A. Filtra Tarefas Vencidas
    count_vencidas = 0
    for p in projetos:
        nome_proj = p.get('name')
        tem_atraso = False
        tarefas_proj = []
        
        for t in p.get('tasks', []):
            status = str(t.get('status', '')).lower()
            data_fim_str = t.get('end_date')
            
            if status not in ['completed', 'concluído', 'fechado', 'cancelled']:
                data_fim = parse_data_zoho(data_fim_str)
                if data_fim and data_fim <= fim_semana:
                    atraso = (hoje - data_fim).days
                    # Adiciona à lista local
                    tarefas_proj.append(f"   - {t.get('name')} (Vencia em {data_fim.strftime('%d/%m')}, {atraso}d atraso)")
                    count_vencidas += 1
        
        if tarefas_proj:
            texto_vencidas += f"\nPROJETO: {nome_proj}\n" + "\n".join(tarefas_proj) + "\n"

    if count_vencidas == 0:
        texto_vencidas = "Nenhuma atividade vencida nesta semana."

    # B. Filtra Estagnação (Via Tracker)
    estagnados, evoluiram = obter_comparativo()
    
    if estagnados:
        for item in estagnados:
            texto_estagnados += f"- {item['nome']}: Travado em {item['percent']}%\n"
    else:
        texto_estagnados = "Todos os projetos tiveram alguma movimentação."

    if evoluiram:
        for item in evoluiram:
            texto_evolucao += f"- {item['nome']}: Avançou de {item['antes']}% para {item['agora']}% (+{item['delta']}%)\n"

    # 4. CONSTRUÇÃO DO PROMPT LEVE
    # Agora mandamos para o Gemini APENAS o resumo já mastigado
    prompt = (
        f"DATA: {hoje.strftime('%d/%m/%Y')}\n\n"
        f"--- DADOS PRÉ-PROCESSADOS ---\n"
        f"1. TAREFAS VENCIDAS:\n{texto_vencidas}\n\n"
        f"2. PROJETOS ESTAGNADOS (Sem mudança de %):\n{texto_estagnados}\n\n"
        f"3. EVOLUÇÃO:\n{texto_evolucao}\n\n"
        f"--- INSTRUÇÃO ---\n"
        "Atue como um Secretário Executivo. Escreva um e-mail HTML formal e direto para o Gestor Giovani."
        "Use estes dados para cobrar resultados. "
        "Destaque em VERMELHO o que está vencido e estagnado. "
        "Destaque em VERDE a evolução."
        "Não invente dados. Use apenas a lista acima."
    )
    
    print("🧠 Gerando e-mail (Payload Reduzido)...")
    
    # Retry simples caso ainda dê erro (mas é improvável agora)
    try:
        brain = JarvisBrain()
        corpo_email = brain.analisar(prompt)
    except Exception as e:
        print(f"⚠️ Erro na IA: {e}. Tentando novamente em 5s...")
        time.sleep(5)
        brain = JarvisBrain()
        corpo_email = brain.analisar(prompt)

    # Limpeza HTML
    corpo_email_html = corpo_email.replace("```html", "").replace("```", "")

    # 5. Enviar
    carteiro = JarvisEmail()
    carteiro.enviar_email(Config.GMAIL_DESTINO_PADRAO, "⚠️ Relatório de Cobrança Semanal", corpo_email_html)

if __name__ == "__main__":
    gerar_relatorio_cobranca()