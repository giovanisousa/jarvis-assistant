import pyttsx3
import speech_recognition as sr
import keyboard  # Nova biblioteca para interrupção física

class JarvisVoz:
    def __init__(self):
        # --- BOCA (TTS) ---
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 190)
        self.engine.setProperty('volume', 1.0)
        
        # Seleção do Daniel
        voices = self.engine.getProperty('voices')
        voz_selecionada = False
        for voice in voices:
            if "daniel" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                voz_selecionada = True
                break
        if not voz_selecionada:
            for voice in voices:
                if "brazil" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break

        # --- OUVIDOS (STT) - MODO PACIENTE ---
        self.recognizer = sr.Recognizer()
        
        # AQUI ESTÁ A MÁGICA PARA NÃO CORTAR:
        self.recognizer.pause_threshold = 2.0  # Espera 2s de silêncio antes de cortar (era 0.8)
        self.recognizer.energy_threshold = 300 # Sensibilidade (ajuste se tiver muito ruído de fundo)
        self.recognizer.dynamic_energy_threshold = True # Ajusta sozinho ao ruído da sala

    def falar(self, texto):
        """
        Fala verificando se o usuário apertou ESPAÇO para interromper.
        """
        try:
            # Verifica interrupção antes de começar
            if keyboard.is_pressed('space'):
                print("   🛑 Fala interrompida pelo usuário.")
                return

            self.engine.say(texto)
            self.engine.runAndWait()
        except Exception:
            pass

    def ouvir(self):
        """Escuta com mais paciência"""
        with sr.Microphone() as source:
            print("\n🎤 [Ouvindo...] (Pode falar, tenho paciência)")
            
            # Calibragem rápida de ruído (ajuda com TV/Bebê ao fundo)
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # phrase_time_limit=20: Dá até 20 segundos para você completar a frase
                # timeout=None: Fica ouvindo para sempre até você começar a falar
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=20)
                
                print("   ⌛ Processando áudio...")
                texto = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"🗣️ VOCÊ: {texto}")
                return texto
            
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None # Não entendeu nada (silêncio ou barulho)
            except Exception as e:
                print(f"Erro no microfone: {e}")
                return None