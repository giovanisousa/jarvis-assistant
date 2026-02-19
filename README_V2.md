# 🤖 APEX - Assistente Executivo Conversacional V2

![Status](https://img.shields.io/badge/Status-Pronto-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

Assistente de voz inteligente inspirado no Apex do Homem de Ferro, com controle por voz, automação de tarefas e integração com projetos Zoho.

---

## 🎯 CARACTERÍSTICAS PRINCIPAIS

### ✨ **Versão 2.0 - Melhorias**
- 🧠 **Memória Conversacional**: Lembra do contexto das últimas 10 interações
- 🎙️ **Modo Contínuo**: Ative uma vez e converse naturalmente por 60 segundos
- 🤖 **IA Natural**: Respostas adaptadas ao contexto, menos robóticas
- ⚡ **Detecção Inteligente**: Identifica automaticamente se é consulta ou ação
- 📊 **Otimizado**: Melhor gestão de tokens e performance

### 🛠️ **Funcionalidades**
- ✉️ Enviar e receber emails automaticamente
- 💬 Enviar mensagens via WhatsApp Web
- 🖱️ Automação de interface (clicar, digitar)
- 📋 Consultar status de projetos (Zoho Projects)
- 📝 Sistema de anotações e memória
- 🎤 Controle 100% por voz

---

## 📦 INSTALAÇÃO

### **Pré-requisitos**
- Python 3.8 ou superior
- Microfone funcional
- Conexão com internet
- Conta Google (para email)
- API Key do Google Gemini

### **Passo 1: Clonar/Baixar o Projeto**
```bash
git clone https://github.com/seu-usuario/apex-assistant.git
cd apex-assistant
```

### **Passo 2: Instalar Dependências**
```bash
pip install -r requirements.txt
```

**Ou manualmente:**
```bash
pip install pyttsx3 SpeechRecognition keyboard pyautogui google-generativeai requests python-dotenv
```

### **Passo 3: Configurar Credenciais**

#### 3.1 Criar arquivo `.env` na raiz do projeto:
```env
# === GEMINI API (OBRIGATÓRIO) ===
GEMINI_API_KEY=sua_chave_gemini_aqui

# === EMAIL (OBRIGATÓRIO para funções de email) ===
GMAIL_USER=seu_email@gmail.com
GMAIL_PASS=sua_senha_app_gmail
GMAIL_DESTINO_PADRAO=destinatario@gmail.com

# === ZOHO (OPCIONAL) ===
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=
ZOHO_REFRESH_TOKEN=
ZOHO_PORTAL_ID=
ZOHO_MY_USER_ID=

# === USUÁRIO ===
USER_NAME=Seu Nome
```

#### 3.2 Obter Credenciais

**Google Gemini API:**
1. Acesse: https://makersuite.google.com/app/apikey
2. Crie uma API Key
3. Cole no campo `GEMINI_API_KEY`

**Gmail (Senha de App):**
1. Ative autenticação em 2 etapas: https://myaccount.google.com/security
2. Gere senha de app: https://myaccount.google.com/apppasswords
3. Use esta senha no campo `GMAIL_PASS`

**Zoho (Opcional):**
- Necessário apenas se usar integração com Zoho Projects
- Veja documentação em: `setup_zoho.py`

### **Passo 4: Ativar Versão V2 (Recomendado)**

**Opção A: Script Automático**
```bash
python setup_v2.py
```
Siga o menu interativo para ativar a V2.

**Opção B: Manual**
```bash
# Fazer backup
cp brain.py brain_original.py
cp main.py main_original.py

# Ativar V2
cp brain_v2.py brain.py
cp main_v2.py main.py
```

---

## 🚀 USO

### **Iniciar o Assistente**
```bash
python main.py
```

### **Fluxo de Uso**

1. **Ativação**
   ```
   VOCÊ: "Apex"
   APEX: "Sim, senhor? Como posso ajudar?"
   ```

2. **Modo Contínuo (60s)**
   ```
   VOCÊ: "Qual a situação do projeto Rivelare?"
   APEX: [responde]
   
   VOCÊ: "E o cronograma?" ← não precisa dizer "Apex"
   APEX: [responde sobre Rivelare]
   ```

3. **Comandos de Ação**
   ```
   VOCÊ: "Manda email pro João atualizando ele"
   APEX: [envia email automaticamente]
   ```

### **Exemplos de Comandos**

#### 📊 Consultas
```
"Qual a situação do projeto 1236?"
"Quantos projetos estão em implantação?"
"Me fala dos projetos atrasados"
"Qual o percentual do Rivelare?"
```

#### ✉️ Email
```
"Checa meus emails não lidos"
"Tem algum email sobre passagem OA?"
"Manda email pro cliente avisando do atraso"
```

#### 💬 WhatsApp
```
"Avisa a Patricia que terminei o projeto"
"Manda mensagem pro João"
"Fala pra Maria que preciso conversar"
```

#### 🖱️ Automação
```
"Clica no botão enviar"
"Abre o Google Chrome"
"Digita 'olá mundo'"
```

#### 📝 Anotações
```
"Anote que cliente está insatisfeito"
"Lembre que projeto precisa de reunião"
```

#### ⚙️ Sistema
```
"Limpar histórico" → reseta conversa
"Sair" / "Desligar" → encerra
```

---

## ⚙️ CONFIGURAÇÕES

### **main_v2.py**
```python
# Timeout de sessão (segundos)
SESSAO_TIMEOUT = 60

# Modo contínuo (não precisa repetir "Apex")
MODO_CONTINUO = True  # True/False
```

### **brain_v2.py**
```python
# Histórico de conversa
self.max_historico = 10  # Número de interações

# Criatividade da IA
temperature=0.3  # 0.0-1.0

# Modelo Gemini
self.model_name = "gemini-2.0-flash-exp"
```

---

## 📁 ESTRUTURA DO PROJETO

```
apex-assistant/
│
├── brain_v2.py          # Cérebro melhorado (memória + contexto)
├── main_v2.py           # Interface melhorada (modo contínuo)
├── voz.py               # Sistema de voz (TTS + STT)
├── ferramentas.py       # Ferramentas de ação (email, whatsapp, etc)
├── config.py            # Configurações e .env
│
├── brain.py             # Versão original (backup)
├── main.py              # Versão original (backup)
│
├── correio.py           # Sistema de email
├── zoho_sync.py         # Sincronização Zoho Projects
├── tracker.py           # Rastreador de progresso
│
├── db_projetos.json     # Dados dos projetos
├── db_memoria.json      # Anotações do usuário
├── db_historico_percentual.json  # Histórico de %
│
├── setup_v2.py          # Instalador/configurador
├── GUIA_V2.md           # Guia detalhado de uso
├── README.md            # Este arquivo
├── requirements.txt     # Dependências
└── .env                 # Credenciais (não versionar!)
```

---

## 🆚 VERSÕES

| Recurso | V1 (Original) | V2 (Melhorado) |
|---------|---------------|----------------|
| Memória de conversa | ❌ | ✅ (10 interações) |
| Modo contínuo | ❌ | ✅ (60s) |
| Detecção de contexto | ❌ | ✅ Automática |
| Respostas naturais | 🟡 Básico | ✅ Avançado |
| Gestão de tokens | 🟡 Limitado | ✅ Otimizado |
| Timeout sessão | 30s | 60s (configurável) |

**Recomendação:** Use sempre a **V2**

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### **Problema: Microfone não funciona**
✅ Verifique se o microfone está conectado
✅ Teste com: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`
✅ Configure o microfone padrão do sistema

### **Problema: Voz não sintetiza**
✅ Windows: Instale vozes em PT-BR
✅ Teste com: `python listar_vozes.py`
✅ Verifique volume do sistema

### **Problema: "Erro no Gemini"**
✅ Verifique se a API Key está correta no `.env`
✅ Confirme que a API está ativa: https://makersuite.google.com
✅ Verifique cotas de uso

### **Problema: Email não envia**
✅ Use senha de app (não a senha normal)
✅ Ative autenticação 2 fatores no Google
✅ Verifique firewall/antivírus

### **Problema: WhatsApp não funciona**
✅ Abra WhatsApp Web no navegador primeiro
✅ Mantenha janela visível (não minimizada)
✅ Use nomes exatos dos contatos

---

## 📚 DOCUMENTAÇÃO ADICIONAL

- **GUIA_V2.md**: Guia completo de uso e recursos
- **setup_v2.py**: Script interativo de configuração
- Comentários inline nos arquivos `.py`

---

## 🔒 SEGURANÇA

⚠️ **IMPORTANTE:**
- Nunca compartilhe seu arquivo `.env`
- Use senhas de app (não senhas reais)
- Adicione `.env` ao `.gitignore`
- Revogue credenciais se comprometidas

---

## 🤝 CONTRIBUINDO

Contribuições são bem-vindas! 

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/melhoria`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/melhoria`)
5. Abra um Pull Request

---

## 📄 LICENÇA

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 🙏 AGRADECIMENTOS

- Google Gemini pela API de IA
- Comunidade Python
- Inspiração: Apex (Homem de Ferro - Marvel)

---

## 📞 SUPORTE

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/apex-assistant/issues)
- **Documentação**: Veja `GUIA_V2.md`
- **Email**: seu-email@exemplo.com

---

## 🗺️ ROADMAP

### Versão 2.1 (Planejado)
- [ ] Integração com Google Calendar
- [ ] Lembretes proativos
- [ ] Modo offline básico
- [ ] Interface gráfica (GUI)

### Versão 3.0 (Futuro)
- [ ] Reconhecimento de gestos (webcam)
- [ ] Controle de casa inteligente
- [ ] Multi-idiomas
- [ ] App mobile

---

**Desenvolvido com ❤️ para aumentar a produtividade**

*Última atualização: Fevereiro 2026*
