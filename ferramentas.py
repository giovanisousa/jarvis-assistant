import smtplib
import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyautogui
import time
import json
import os
from google import genai
from config import Config

# Segurança do Mouse
pyautogui.FAILSAFE = True

class JarvisFerramentas:
    def __init__(self):
        self.email_user = Config.GMAIL_USER
        self.email_pass = Config.GMAIL_PASS
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.imap_server = "imap.gmail.com"
        
        if Config.GEMINI_KEY:
            self.client = genai.Client(api_key=Config.GEMINI_KEY)
            self.model_visao = "gemini-flash-latest"

    # --- MÓDULO 1: ENVIAR E-MAIL ---
    def enviar_email(self, destinatario, assunto, corpo_html):
        if not destinatario:
            destinatario = Config.GMAIL_DESTINO_PADRAO

        print(f"   📧 [Ferramenta] Enviando para {destinatario}...")
        
        msg = MIMEMultipart()
        msg['From'] = f"Jarvis <{self.email_user}>"
        msg['To'] = destinatario
        msg['Subject'] = assunto
        corpo_final = f"{corpo_html}<br><br><small>Enviado por Jarvis Assistant - Animati</small>"
        msg.attach(MIMEText(corpo_final, 'html'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_pass)
            server.sendmail(self.email_user, destinatario, msg.as_string())
            server.quit()
            return "E-mail enviado com sucesso."
        except Exception as e:
            return f"Erro ao enviar: {e}"

    # --- MÓDULO 2: BUSCAR E LER E-MAILS (TURBINADO) ---
    def buscar_emails(self, query=None, apenas_nao_lidos=False, limite=3):
        """
        Busca e-mails no Gmail usando filtros avançados.
        - query: Texto para buscar no ASSUNTO (ex: "Passagem OA")
        - apenas_nao_lidos: Se True, traz apenas os não abertos (UNSEEN)
        """
        modo = "NÃO LIDOS" if apenas_nao_lidos else "GERAL"
        termo = f"sobre '{query}'" if query else "recentes"
        print(f"   📧 [Ferramenta] Buscando e-mails ({modo}, {termo})...")
        
        resumo_emails = []
        
        try:
            # Conecta ao IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_user, self.email_pass)
            mail.select("inbox")

            # Constrói o critério de busca
            criterios = []
            
            if apenas_nao_lidos:
                criterios.append("UNSEEN")
            
            if query:
                # O Gmail aceita busca direta no assunto. O charset utf-8 é vital para acentos.
                # Ex: '(SUBJECT "Passagem")'
                criterios.append(f'(SUBJECT "{query}")')
            
            # Se a lista de critérios estiver vazia, busca TUDO (ALL)
            busca_imap = " ".join(criterios) if criterios else "ALL"
            
            # Executa a busca com suporte a UTF-8 (para acentos)
            status, messages = mail.search("utf-8", busca_imap)
            
            if status != "OK":
                return "Erro técnico na busca IMAP."

            email_ids = messages[0].split()
            
            if not email_ids:
                return "Nenhum e-mail encontrado com esses critérios."

            # Pega apenas os últimos 'limite'
            ultimos_ids = email_ids[-limite:]
            
            for e_id in reversed(ultimos_ids):
                # Pega o corpo do e-mail
                _, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decodifica Assunto
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        # Decodifica Remetente
                        from_ = msg.get("From")
                        
                        # Extrai Corpo (Texto)
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    payload = part.get_payload(decode=True)
                                    if payload: body = payload.decode(errors='ignore')
                                    break
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload: body = payload.decode(errors='ignore')

                        # Limpa quebras de linha excessivas e resume
                        body_limpo = " ".join(body.split())[:300]
                        resumo_emails.append(f"📩 DE: {from_}\n   ASSUNTO: {subject}\n   RESUMO: {body_limpo}...\n")
            
            mail.close()
            mail.logout()
            
            return "\n".join(resumo_emails)
            
        except Exception as e:
            return f"Erro ao buscar e-mails: {e}"

    # --- MÓDULO 3: VISÃO ---
    def clicar_elemento_visual(self, descricao_elemento):
        print(f"   👁️ [Ferramenta] Procurando '{descricao_elemento}'...")
        screenshot_path = "temp_visao.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        largura, altura = screenshot.size

        try:
            file_ref = self.client.files.upload(path=screenshot_path)
            prompt = (
                f"Encontre o elemento visual: '{descricao_elemento}'. "
                "Retorne JSON: [ymin, xmin, ymax, xmax] (0-1000). Se não achar, []."
            )
            resp = self.client.models.generate_content(
                model=self.model_visao, contents=[file_ref, prompt]
            )
            coords = json.loads(resp.text.replace("```json", "").replace("```", "").strip())
            
            if not coords: return f"Não encontrei '{descricao_elemento}'."

            ymin, xmin, ymax, xmax = coords
            cx = int(((xmin + xmax) / 2 / 1000) * largura)
            cy = int(((ymin + ymax) / 2 / 1000) * altura)
            
            pyautogui.moveTo(cx, cy, duration=0.8)
            pyautogui.click()
            return f"Cliquei em '{descricao_elemento}'."
        except Exception as e:
            return f"Erro na visão: {e}"
        finally:
            if os.path.exists(screenshot_path): os.remove(screenshot_path)

    def digitar_texto(self, texto):
        print(f"   ⌨️ [Ferramenta] Digitando...")
        # Escreve caractere por caractere para o WhatsApp Web não bugar
        pyautogui.write(texto, interval=0.01)
        pyautogui.press('enter')
        return "Texto digitado."
    
    
    # --- MÓDULO 4: WHATSAPP (MACRO DE VISÃO) ---
    # --- MÓDULO 4: WHATSAPP (CORRIGIDO) ---
    def enviar_whatsapp(self, contato, mensagem):
        """
        Versão Otimizada para AnyDesk/Web:
        Prioriza atalhos de teclado para evitar erros de clique em janelas remotas.
        """
        print(f"   📱 [Ferramenta] Iniciando WhatsApp para '{contato}'...")
        
        # 1. Trazer o foco para a página e resetar qualquer estado anterior
        pyautogui.press('esc') 
        time.sleep(0.5)
        pyautogui.press('esc')
        
        # 2. Forçar foco no campo de busca via Atalho (Independente de visão)
        # O atalho Ctrl+Alt+/ é o padrão do WhatsApp Web para busca
        print("   ⌨️ Acionando atalho de busca (Ctrl+Alt+/)...")
        pyautogui.hotkey('ctrl', 'alt', '/')
        time.sleep(1.2) # Tempo para o AnyDesk processar o comando remoto

        # 3. Limpeza Total do campo (Caso tenha lixo ou o nome anterior)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.5)

        # 4. Digitar o nome do contato com cadência humana
        # Usamos o nome exato que o cérebro capturou
        print(f"   ✍️ Digitando contato: {contato}")
        pyautogui.write(contato, interval=0.1)
        
        # 5. Seleção e Envio
        time.sleep(2.5) # Espera carregar os resultados na lista
        pyautogui.press('enter') # Entra na conversa selecionada
        time.sleep(1.2)
        
        # Digita a mensagem
        print(f"   💬 Enviando mensagem...")
        pyautogui.write(mensagem, interval=0.02)
        pyautogui.press('enter')
        
        return f"✅ Mensagem enviada para {contato}."

# --- TESTE RÁPIDO ---
if __name__ == "__main__":
    tools = JarvisFerramentas()
    
    # Teste: Buscar e-mails com a palavra "Suporte" no assunto
    # Mude "Suporte" para algo que você sabe que tem na sua caixa agora
    print(tools.buscar_emails(query="Suporte", apenas_nao_lidos=False))