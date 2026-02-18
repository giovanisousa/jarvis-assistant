import time
import re
import keyboard
from voz import JarvisVoz
from brain_v2 import JarvisBrain

# Configuração de Tempo
SESSAO_TIMEOUT = 60  # 1 minuto de timeout (aumentado)
MODO_CONTINUO = True  # Se True, não precisa dizer "Jarvis" após ativar

def limpar_texto_para_fala(texto):
    """Remove formatação Markdown/HTML para leitura fluida"""
    # Remove JSON se aparecer na resposta
    if "```json" in texto or texto.strip().startswith("{"):
        return "Executando ação solicitada."
    
    texto_limpo = texto.replace("*", "").replace("#", "").replace("- ", "")
    texto_limpo = texto_limpo.replace("<b>", "").replace("</b>", "")
    texto_limpo = texto_limpo.replace("<br>", ". ")
    texto_limpo = re.sub(r'\n+', '. ', texto_limpo)
    return texto_limpo

def iniciar_assistente():
    print("="*60)
    print("   🤖 JARVIS - ASSISTENTE EXECUTIVO INTELIGENTE")
    print("="*60)
    print(f"   ⚡ Modo: {'CONTÍNUO' if MODO_CONTINUO else 'WAKE WORD'}")
    print(f"   ⏱️  Timeout de sessão: {SESSAO_TIMEOUT}s")
    print("   🎤 Diga 'JARVIS' para ativar")
    print("   ⌨️  Aperte ESPAÇO para interromper a fala")
    print("   🛑 Diga 'SAIR' ou 'DESLIGAR' para encerrar")
    print("   🧹 Diga 'LIMPAR HISTÓRICO' para resetar a conversa")
    print("="*60)

    try:
        brain = JarvisBrain()
    except Exception as e:
        print(f"❌ Erro crítico no cérebro: {e}")
        return

    # Variáveis de Estado
    ultimo_comando_time = 0
    sessao_ativa = False
    
    # Mensagem inicial
    try:
        voz_temp = JarvisVoz()
        voz_temp.falar("Sistemas online. Estou pronto, senhor.")
        del voz_temp
    except Exception as e:
        print(f"⚠️ Aviso de voz: {e}")

    # Loop Principal
    while True:
        # Verifica timeout da sessão
        tempo_sem_falar = time.time() - ultimo_comando_time
        
        if sessao_ativa and tempo_sem_falar > SESSAO_TIMEOUT:
            sessao_ativa = False
            print(f"\n💤 Sessão expirada após {SESSAO_TIMEOUT}s de inatividade.")
            print("   Diga 'Jarvis' novamente para reativar.\n")

        # Indicador Visual de Status
        if sessao_ativa:
            status_icone = "🟢 ATIVO"
            status_msg = f" [Sessão ativa - {int(SESSAO_TIMEOUT - tempo_sem_falar)}s restantes]"
        else:
            status_icone = "💤 STANDBY"
            status_msg = " [Aguardando 'Jarvis'...]"
        
        print(f"\n{status_icone}{status_msg}")
        print("🎤 Ouvindo... ", end="", flush=True)

        # 1. CAPTURA DE VOZ
        voz_ouvir = JarvisVoz()
        comando_usuario = voz_ouvir.ouvir()
        del voz_ouvir 
        
        if not comando_usuario:
            continue 

        comando_lower = comando_usuario.lower()
        print(f"\n📝 Captado: '{comando_usuario}'")

        # --- SISTEMA DE WAKE WORD INTELIGENTE ---
        
        # Se sessão NÃO está ativa, precisa da palavra mágica
        if not sessao_ativa:
            if "jarvis" in comando_lower:
                print("   ⚡ JARVIS ATIVADO!")
                sessao_ativa = True
                ultimo_comando_time = time.time()
                
                # Remove "jarvis" do comando para processar o resto
                comando_processado = comando_lower.replace("jarvis", "").strip()
                comando_processado = comando_processado.replace(",", "").strip()
                
                # Se ele disse SÓ "Jarvis", pergunta o que quer
                if len(comando_processado) < 3:
                    voz_resp = JarvisVoz()
                    voz_resp.falar("Sim, senhor? Como posso ajudar?")
                    del voz_resp
                    continue
                
                # Se disse "Jarvis + comando", processa o comando
                comando_usuario = comando_processado
            else:
                # Ignora comandos sem wake word
                print(f"   ⏭️  Ignorado (sem wake word): '{comando_usuario}'")
                continue
        else:
            # Sessão já está ativa
            if MODO_CONTINUO:
                # No modo contínuo, renova o timer a cada interação
                ultimo_comando_time = time.time()
            else:
                # No modo wake word, verifica se disse "jarvis" de novo
                if "jarvis" not in comando_lower:
                    print("   ⏭️  Ignorado (modo wake word - diga 'Jarvis' antes)")
                    continue
                ultimo_comando_time = time.time()
                comando_usuario = comando_lower.replace("jarvis", "").replace(",", "").strip()

        # --- COMANDOS DE SISTEMA ---
        if any(w in comando_lower for w in ["sair", "desligar", "encerrar", "tchau"]):
            voz_tchau = JarvisVoz()
            voz_tchau.falar("Desligando sistemas. Até logo, senhor.")
            del voz_tchau
            break

        if "limpar histórico" in comando_lower or "limpa histórico" in comando_lower:
            brain.limpar_historico()
            voz_limpar = JarvisVoz()
            voz_limpar.falar("Histórico de conversa limpo. Começando do zero.")
            del voz_limpar
            continue

        # --- PROCESSAMENTO PRINCIPAL ---
        print("🧠 Analisando...")
        
        try:
            resposta_texto = brain.analisar(comando_usuario)
            
            # Exibir resposta no terminal
            print(f"\n{'='*60}")
            print(f"🤖 JARVIS:\n{resposta_texto}")
            print(f"{'='*60}\n")
            
            # Preparar texto para fala
            texto_falado = limpar_texto_para_fala(resposta_texto)
            
            # Verificar se a resposta é muito curta (confirmações)
            if len(texto_falado.split()) <= 3:
                # Respostas curtas: fala direto
                voz_falar = JarvisVoz()
                voz_falar.falar(texto_falado)
                del voz_falar
            else:
                # Respostas longas: permite interrupção
                voz_falar = JarvisVoz()
                
                # Divide em frases
                frases = re.split(r'(?<=[.!?])\s+', texto_falado)
                
                parar_fala = False
                for i, frase in enumerate(frases):
                    if not frase.strip(): 
                        continue
                    if parar_fala: 
                        break

                    # Checagem de interrupção (Espaço)
                    if keyboard.is_pressed('space'):
                        print("   🛑 Fala interrompida pelo usuário!")
                        parar_fala = True
                        break 
                    
                    voz_falar.falar(frase)
                    
                    # Pequena pausa entre frases (mais natural)
                    if i < len(frases) - 1:
                        time.sleep(0.3)
                
                del voz_falar

            # Ao terminar, renova o tempo (permite resposta imediata)
            ultimo_comando_time = time.time()

        except KeyboardInterrupt:
            print("\n\n⚠️ Interrompido pelo usuário (Ctrl+C)")
            voz_inter = JarvisVoz()
            voz_inter.falar("Operação interrompida.")
            del voz_inter
            sessao_ativa = False
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            voz_erro = JarvisVoz()
            voz_erro.falar("Desculpe, ocorreu um erro. Por favor, tente novamente.")
            del voz_erro

def main():
    """Ponto de entrada com tratamento de erros"""
    try:
        iniciar_assistente()
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando JARVIS...")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        print("   Verifique as configurações e tente novamente.")

if __name__ == "__main__":
    main()
