# 📋 GUIA DO SISTEMA DE LOGGING - JARVIS

## 🎯 VISÃO GERAL

O sistema de logging captura **TODOS** os eventos, erros e ações do Jarvis, permitindo debug fácil e rastreamento completo.

---

## 📁 ARQUIVOS CRIADOS

### **logger.py**
Módulo centralizado de logging. Gerencia todos os logs do sistema.

### **brain_v2_logged.py**
Versão do brain com logging integrado. Substitui o brain_v2.py.

### **view_logs.py**
Ferramenta interativa para visualizar e analisar logs.

---

## 📂 ESTRUTURA DE LOGS

Pasta `logs/` será criada automaticamente com:

```
logs/
├── jarvis_2026-02-16.log    # Log completo do dia (DEBUG+)
├── erros.log                # Apenas erros e warnings
├── acoes.log                # Ações executadas (emails, whatsapp, etc)
└── jarvis_2026-02-15.log    # Logs de dias anteriores
```

---

## 🚀 COMO ATIVAR

### **Passo 1: Ativar Brain com Logging**

**Opção A: Renomear (Recomendado)**
```bash
# Backup do brain atual
cp brain_v2.py brain_v2_sem_log.py

# Ativar versão com logging
cp brain_v2_logged.py brain_v2.py
```

**Opção B: Importar Direto**
Edite seu `main_v2.py` ou `app_v2.py`:
```python
# Trocar esta linha:
from brain_v2 import JarvisBrain

# Por esta:
from brain_v2_logged import JarvisBrain
```

---

## 📊 TIPOS DE LOG

### **🔵 DEBUG** - Detalhes técnicos
```
2026-02-16 14:30:15 | DEBUG | brain_v2 | analisar:252 | Roteando pergunta: qual situação rivelare
```
- Usado para: rastreamento detalhado do fluxo
- Só aparece em: `jarvis_YYYY-MM-DD.log`

### **🟢 INFO** - Eventos normais
```
2026-02-16 14:30:16 | INFO | brain_v2 | analisar:260 | NOVA SOLICITAÇÃO RECEBIDA
```
- Usado para: eventos importantes mas normais
- Aparece em: logs diários + console

### **🟡 WARNING** - Avisos
```
2026-02-16 14:30:20 | WARNING | brain_v2 | roteador_inteligente:225 | Múltiplos projetos encontrados: 3
```
- Usado para: situações que precisam atenção
- Aparece em: logs diários + `erros.log`

### **🟠 ERROR** - Erros recuperáveis
```
2026-02-16 14:30:25 | ERROR | brain_v2 | analisar:340 | Erro ao processar: KeyError: 'name'
```
- Usado para: falhas que o sistema consegue lidar
- Aparece em: logs diários + `erros.log` + console

### **🔴 CRITICAL** - Erros graves
```
2026-02-16 14:30:30 | CRITICAL | brain_v2 | __init__:15 | Chave do Gemini não encontrada!
```
- Usado para: falhas que impedem funcionamento
- Aparece em: todos os logs + console

---

## 🔍 VISUALIZANDO LOGS

### **Ferramenta Interativa**
```bash
python view_logs.py
```

**Menu:**
```
  1. jarvis_2026-02-16.log  |  125.3 KB | 16/02 14:30
  2. jarvis_2026-02-15.log  |   89.1 KB | 15/02 18:20
  3. erros.log              |   12.4 KB | 16/02 14:25

Opções:
  E - Ver apenas ERROS
  A - Ver apenas AÇÕES
  H - Ver log de HOJE
  T - Ver TODOS (tail)
  L - LIMPAR logs antigos
  0 - Sair
```

### **Linha de Comando**

**Ver últimos erros:**
```bash
tail -n 50 logs/erros.log
```

**Ver log de hoje:**
```bash
cat logs/jarvis_$(date +%Y-%m-%d).log
```

**Buscar termo específico:**
```bash
grep "Rivelare" logs/jarvis_*.log
```

**Ver ações executadas:**
```bash
cat logs/acoes.log
```

---

## 🐛 DEBUGANDO ERROS

### **Cenário 1: "Jarvis não responde a perguntas sobre projeto"**

1. **Veja o log de hoje:**
   ```bash
   python view_logs.py
   # Escolha opção H (Hoje)
   ```

2. **Procure por:**
   - `NOVA SOLICITAÇÃO RECEBIDA` → confirma que recebeu
   - `Projeto identificado` → vê se achou o projeto
   - `ERROR` → identifica onde falhou

3. **Exemplo de erro encontrado:**
   ```
   ERROR | brain_v2 | roteador_inteligente:218 | KeyError: 'name'
   ```
   **Solução:** Projeto sem campo 'name' no JSON

### **Cenário 2: "Erro ao enviar email"**

1. **Veja erros:**
   ```bash
   python view_logs.py
   # Escolha opção E (Erros)
   ```

2. **Procure por:**
   - `enviar_email` → localiza tentativa
   - Stack trace completo → vê causa exata

3. **Exemplo:**
   ```
   ERROR | ferramentas | enviar_email:35 | SMTPAuthenticationError: Username and Password not accepted
   ```
   **Solução:** Senha de app inválida

### **Cenário 3: "Jarvis trava ao processar"**

1. **Veja último log:**
   ```bash
   tail -100 logs/jarvis_$(date +%Y-%m-%d).log
   ```

2. **Procure pela última linha:**
   - Se parou em `Chamando Gemini API...` → problema na API
   - Se parou em `Construindo contexto...` → problema no JSON

3. **Ver stack trace completo:**
   ```
   CRITICAL | brain_v2 | analisar:342 | Traceback completo:
   Traceback (most recent call last):
     File "brain_v2_logged.py", line 320, in analisar
       resp = self.client.models.generate_content(...)
   ```

---

## 📈 MONITORAMENTO

### **Verificação Diária**

```bash
# Ver se há erros
python view_logs.py
# Opção E

# Se não houver erros:
✅ Nenhum erro registrado! Sistema rodando perfeitamente.
```

### **Análise de Performance**

Conte quantas chamadas à API:
```bash
grep "Chamando Gemini API" logs/jarvis_*.log | wc -l
```

Veja tempo de resposta (logs DEBUG):
```bash
grep "Resposta recebida" logs/jarvis_*.log
```

### **Auditoria de Ações**

Ver todos os emails enviados:
```bash
grep "enviar_email" logs/acoes.log
```

Ver todas as mensagens WhatsApp:
```bash
grep "enviar_whatsapp" logs/acoes.log
```

---

## 🧹 MANUTENÇÃO

### **Limpeza Automática**

O logger limpa logs com mais de 7 dias automaticamente.

**Manual:**
```bash
python view_logs.py
# Opção L (Limpar)
```

### **Rotação de Logs**

Logs são organizados por dia automaticamente:
- `jarvis_2026-02-16.log` ← hoje
- `jarvis_2026-02-15.log` ← ontem
- `jarvis_2026-02-14.log` ← 2 dias atrás

Arquivo `erros.log` e `acoes.log` são cumulativos.

---

## 💡 DICAS AVANÇADAS

### **1. Filtrar por Hora**
```bash
grep "14:30" logs/jarvis_2026-02-16.log
```

### **2. Ver apenas chamadas à API**
```bash
grep "Gemini API" logs/jarvis_*.log
```

### **3. Exportar erros para análise**
```bash
grep "ERROR" logs/erros.log > analise_erros.txt
```

### **4. Monitorar em tempo real**
```bash
tail -f logs/jarvis_$(date +%Y-%m-%d).log
```

### **5. Contar tipos de erro**
```bash
grep -c "KeyError" logs/erros.log
grep -c "ValueError" logs/erros.log
grep -c "Exception" logs/erros.log
```

---

## 🔧 CONFIGURAÇÕES

### **Alterar Nível de Log**

Em `logger.py` (linha 34):
```python
# Mais verboso (mostra tudo no console)
handler_console.setLevel(logging.DEBUG)

# Menos verboso (só erros no console)
handler_console.setLevel(logging.ERROR)
```

### **Alterar Dias de Retenção**

Em `brain_v2_logged.py` ou via código:
```python
log.limpar_logs_antigos(dias=30)  # Manter 30 dias
```

### **Desativar Logging**

**Temporário (só console):**
```python
import logging
logging.getLogger("brain_v2").setLevel(logging.CRITICAL)
```

**Permanente:**
Volte para `brain_v2.py` sem logging.

---

## 📞 TROUBLESHOOTING

### **"Pasta logs/ não é criada"**
- Execute o Jarvis uma vez
- A pasta é criada automaticamente

### **"Logs muito grandes"**
- Execute a limpeza: `python view_logs.py` → opção L
- Reduza nível de log para INFO ou WARNING

### **"Não consigo ler os logs"**
- Use `view_logs.py` para visualização formatada
- Ou abra com editor de texto (VSCode, Notepad++)

---

## ✅ CHECKLIST DE ATIVAÇÃO

- [x] Copiar `logger.py` para pasta do projeto
- [x] Copiar `brain_v2_logged.py` para pasta do projeto
- [x] Copiar `view_logs.py` para pasta do projeto
- [ ] Ativar brain com logging (renomear ou importar)
- [ ] Executar Jarvis uma vez
- [ ] Verificar se pasta `logs/` foi criada
- [ ] Executar `python view_logs.py` para testar
- [ ] Fazer uma pergunta ao Jarvis
- [ ] Ver log no visualizador

---

## 🎓 EXEMPLOS PRÁTICOS

### **Exemplo 1: Debug de pergunta que falha**

```bash
# 1. Pergunte ao Jarvis: "Qual situação do Rivelare?"
# (supondo que deu erro)

# 2. Ver o que aconteceu:
python view_logs.py
# Opção H (log de hoje)

# 3. Procure:
NOVA SOLICITAÇÃO RECEBIDA
Pergunta: Qual situação do Rivelare?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Iniciando roteamento...
Projeto identificado por número: 1236 - Rivelare
Enriquecendo 1 projeto(s)
Contexto de projetos: 4523 chars
Chamando Gemini API...
ERROR | analisar:340 | ValueError: Invalid JSON response

# 4. Identifica: API retornou JSON inválido
# Solução: Problema na API ou prompt muito longo
```

### **Exemplo 2: Ver todas as ações da semana**

```bash
python view_logs.py
# Opção A (Ações)

# Saída:
2026-02-16 10:15:23 | enviar_email | {'destinatario': 'cliente@exemplo.com', 'assunto': 'Atualização'}
2026-02-16 11:30:45 | enviar_whatsapp | {'contato': 'Patricia', 'mensagem': 'Projeto finalizado'}
2026-02-16 14:22:10 | buscar_emails | {'query': 'passagem OA', 'apenas_nao_lidos': True}
```

---

**Sistema de Logging Completo e Pronto para Produção!** 🚀
