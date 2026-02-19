import time
import re
import keyboard
from voz import ApexVoz
from brain import ApexBrain

# Configuração de Tempo
SESSAO_TIMEOUT = 30  # Segundos que ele fica "acordado" sem você dizer Apex de novo

def limpar_texto_para_fala(texto):
    """Remove formatação Markdown para leitura fluida"""
    texto_limpo = texto.replace("*", "").replace("#", "").replace("- ", "")
    texto_limpo = re.sub(r'\n+', '. ', texto_limpo)
    return texto_limpo

def iniciar_assistente():
    print("="*50)
    print("   APEX - MODO WAKE WORD (Ativação por Voz)")
    print(f"   [INFO] Diga 'APEX' para ativar. A sessão dura {SESSAO_TIMEOUT}s.")
    print("   [DICA] Aperte ESPAÇO para interromper a fala.")
    print("="*50)

    try:
        brain = ApexBrain()
    except Exception as e:
        print(f"Erro crítico no cérebro: {e}")
        return

    # Variáveis de Estado
    ultimo_comando_time = 0
    sessao_ativa = False
    
    # Instância de voz inicial (apenas para carregar drivers)
    try:
        voz_temp = ApexVoz()
        voz_temp.falar("Sistemas online. Estou em espera.")
        del voz_temp
    except: pass

    while True:
        # Verifica se a sessão expirou
        tempo_sem_falar = time.time() - ultimo_comando_time
        
        if sessao_ativa and tempo_sem_falar > SESSAO_TIMEOUT:
            sessao_ativa = False
            print("\n💤 Sessão expirada. Entrando em modo Standby (Diga 'Apex')...")
            # Opcional: Avisar por voz que vai dormir
            # voz_aviso = ApexVoz()
            # voz_aviso.falar("Entrando em espera.")
            # del voz_aviso

        # Indicador Visual
        status_icone = "🟢" if sessao_ativa else "💤"
        print(f"\n{status_icone} [Ouvindo...] ", end="", flush=True)

        # 1. OUVIR
        voz_ouvir = ApexVoz()
        comando_usuario = voz_ouvir.ouvir()
        del voz_ouvir 
        
        if not comando_usuario:
            continue 

        comando_lower = comando_usuario.lower()

        # --- LÓGICA DO WAKE WORD (O GUARDIÃO) ---
        
        # Se a sessão NÃO está ativa, precisamos da palavra mágica
        if not sessao_ativa:
            if "apex" in comando_lower:
                print("   ⚡ ACORDANDO SISTEMA!")
                sessao_ativa = True
                ultimo_comando_time = time.time()
                # Se ele disse SÓ "Apex", a gente pergunta o que ele quer
                if len(comando_lower.split()) <= 1:
                    voz_resp = ApexVoz()
                    voz_resp.falar("Sim, senhor?")
                    del voz_resp
                    continue
                # Se ele disse "Apex, qual a situação", segue o fluxo normal...
            else:
                # Ignora o comando (ruído ou conversa paralela)
                print(f"   (Ignorado: '{comando_usuario}')")
                continue
        else:
            # Sessão já está ativa, renova o tempo
            ultimo_comando_time = time.time()

        # Comandos de Sistema
        if any(w in comando_lower for w in ["sair", "desligar", "encerrar"]):
            voz_tchau = ApexVoz()
            voz_tchau.falar("Desligando sistemas.")
            break

        # --- PROCESSAMENTO (CÉREBRO) ---
        print("🧠 Pensando...")
        
        try:
            resposta_texto = brain.analisar(comando_usuario)
            
            # Exibir
            print(f"\n🤖 APEX:\n{resposta_texto}\n")
            
            # Falar
            texto_falado = limpar_texto_para_fala(resposta_texto)
            voz_falar = ApexVoz()
            
            # Divisão por frases para permitir interrupção
            frases = re.split(r'(?<=[.!?])\s+', texto_falado)
            
            parar_fala = False
            for frase in frases:
                if not frase.strip(): continue
                if parar_fala: break

                # Checagem de interrupção (Espaço)
                if keyboard.is_pressed('space'):
                    print("   🛑 Interrompido pelo usuário!")
                    parar_fala = True
                    break 
                
                voz_falar.falar(frase)
            
            del voz_falar

            # Ao terminar de falar, renova o tempo para você poder responder sem dizer Apex
            ultimo_comando_time = time.time()

        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    iniciar_assistente()