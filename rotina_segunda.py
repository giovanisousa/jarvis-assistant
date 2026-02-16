import time
from brain import JarvisBrain
from correio import JarvisEmail
from config import Config

def gerar_relatorio_semanal():
    print("="*50)
    print("   ROBÔ DE ROTINA: BRIEFING SEMANAL")
    print("="*50)

    # 1. ACORDAR O CÉREBRO
    try:
        brain = JarvisBrain()
        print("🧠 Cérebro conectado. Analisando projetos...")
    except Exception as e:
        print(f"❌ Erro ao iniciar Brain: {e}")
        return

    # 2. GERAR A ANÁLISE (Simulamos uma pergunta do Gestor)
    prompt_relatorio = (
        "Gere um Relatório Executivo Semanal de TODOS os projetos ativos. "
        "Agrupe por status (Críticos primeiro). "
        "Para cada projeto, cite apenas: Fase Atual, % Conclusão e PENDÊNCIAS BLOQUEANTES. "
        "Não liste tarefas normais, apenas atrasos e riscos. "
        "Use formatação HTML simples (<b> para negrito, <br> para quebra de linha)."
    )
    
    # O cérebro vai pensar e devolver o texto
    relatorio_texto = brain.analisar(prompt_relatorio)
    
    # Pequeno ajuste para garantir que o HTML fique bonito no e-mail
    # O Gemini às vezes devolve Markdown (**), vamos converter para HTML (<b>)
    relatorio_html = relatorio_texto.replace("**", "<b>").replace("</b> ", "</b>").replace("\n", "<br>")

    # 3. ENVIAR O E-MAIL
    try:
        carteiro = JarvisEmail()
        assunto = "📊 Briefing Semanal: Projetos Animati"
        
        # Envia para o e-mail padrão definido no config.py
        sucesso = carteiro.enviar_email(Config.GMAIL_DESTINO_PADRAO, assunto, relatorio_html)
        
        if sucesso:
            print("✅ Relatório enviado com sucesso!")
        else:
            print("❌ Falha no envio.")
            
    except Exception as e:
        print(f"❌ Erro no correio: {e}")

if __name__ == "__main__":
    gerar_relatorio_semanal()