import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class JarvisEmail:
    def __init__(self):
        self.remetente = Config.GMAIL_USER
        self.senha = Config.GMAIL_PASS
        self.servidor_smtp = "smtp.gmail.com"
        self.porta = 587

    def enviar_email(self, destinatario, assunto, corpo_html):
        """Envia um e-mail formatado em HTML"""
        if not destinatario:
            destinatario = Config.EMAIL_DESTINO_PADRAO

        print(f"   📧 Preparando envio para: {destinatario}...")

        # Estrutura do E-mail
        msg = MIMEMultipart()
        msg['From'] = f"Jarvis Assistant <{self.remetente}>"
        msg['To'] = destinatario
        msg['Subject'] = f"🤖 {assunto}"

        # Corpo (HTML para ficar bonito com negrito e listas)
        # Adicionamos uma assinatura automática
        corpo_final = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #f4f4f4; padding: 20px; border-radius: 10px;">
                <h2 style="color: #2c3e50;">Relatório Jarvis</h2>
                <div style="background-color: white; padding: 20px; border-radius: 5px; border-left: 5px solid #3498db;">
                    {corpo_html}
                </div>
                <p style="font-size: 12px; color: #7f8c8d; margin-top: 20px;">
                    Enviado automaticamente pelo Sistema Jarvis.<br>
                    Gestão de Projetos Animati.
                </p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(corpo_final, 'html'))

        try:
            # Conexão Segura com o Gmail
            server = smtplib.SMTP(self.servidor_smtp, self.porta)
            server.starttls() # Criptografia
            server.login(self.remetente, self.senha)
            text = msg.as_string()
            server.sendmail(self.remetente, destinatario, text)
            server.quit()
            
            print(f"   ✅ E-mail enviado com sucesso!")
            return True
        except Exception as e:
            print(f"   ❌ Falha ao enviar e-mail: {e}")
            return False

# --- TESTE UNITÁRIO ---
if __name__ == "__main__":
    # Teste rápido para ver se a senha funciona
    carteiro = JarvisEmail()
    carteiro.enviar_email(
        Config.GMAIL_DESTINO_PADRAO,
        "Teste de Conexão Jarvis", 
        "<p>Olá Giovani, este é um teste de <b>envio HTML</b> do sistema.</p>"
    )