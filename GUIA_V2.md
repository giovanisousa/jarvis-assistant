# 🤖 APEX V2 - SISTEMA DE ASSISTENTE CONVERSACIONAL

## 🎯 MELHORIAS IMPLEMENTADAS

### 1. **CONVERSA NATURAL E FLUIDA**
- ✅ Sistema de memória de curto prazo (lembra últimas 10 interações)
- ✅ Detecção automática de contexto conversacional
- ✅ Respostas adaptadas ao histórico da conversa
- ✅ Tom mais natural e menos robótico

### 2. **MODO CONTÍNUO DE CONVERSA**
- ✅ Você diz "APEX" uma vez e ele fica ativo por 60 segundos
- ✅ Durante esse tempo, pode conversar normalmente sem repetir "Apex"
- ✅ Timer renovado automaticamente a cada interação
- ✅ Indicador visual do tempo restante de sessão

### 3. **DETECÇÃO INTELIGENTE DE INTENÇÕES**
- ✅ Não força JSON - detecta automaticamente quando é ação vs conversa
- ✅ Entende pedidos em linguagem natural (ex: "avisa a Patricia que terminei")
- ✅ Contexto de conversa anterior influencia respostas
- ✅ Menos falsos positivos em detecção de ferramentas

### 4. **MELHOR GESTÃO DE TOKENS**
- ✅ Limita histórico para evitar estouro de contexto
- ✅ Envia apenas projetos relevantes (não todo o banco)
- ✅ Usa modelo mais recente: gemini-2.0-flash-exp

### 5. **EXPERIÊNCIA DO USUÁRIO**
- ✅ Feedback visual melhorado (status, timer, ícones)
- ✅ Comando "LIMPAR HISTÓRICO" para resetar conversa
- ✅ Interrupção de fala mais responsiva
- ✅ Mensagens de erro mais claras

---

## 📋 COMO USAR

### **Ativação Inicial**
```
VOCÊ: "Apex"
APEX: "Sim, senhor? Como posso ajudar?"
```

### **Conversas Naturais (Modo Contínuo)**
```
VOCÊ: "Apex, qual a situação do projeto 1236?"
APEX: [responde]

VOCÊ: "E o 1237?" ← não precisa dizer "Apex" de novo
APEX: [responde considerando contexto]

VOCÊ: "Manda um email pro cliente avisando"
APEX: [executa ação de email]
```

### **Exemplos de Comandos**

#### 📊 Consultas sobre Projetos
```
"Qual a situação do Rivelare?"
"Me fala sobre o projeto 1236"
"Quais projetos estão atrasados?"
"Quantos projetos temos em implantação?"
```

#### ✉️ Ações de Email
```
"Manda um email pro joão atualizando sobre o projeto"
"Verifica se tem email sobre passagem OA"
"Checa meus emails não lidos"
```

#### 💬 WhatsApp
```
"Avisa a Patricia que o projeto foi finalizado"
"Manda mensagem pro João falando que vou atrasar"
"Fala pra Maria que preciso conversar"
```

#### 🖱️ Automação de Tela
```
"Clica no botão de enviar"
"Abre o Google Chrome"
"Digita 'Bom dia, tudo bem?'"
```

#### 📝 Anotações
```
"Anote que o projeto Rivelare está travado na infra"
"Lembre que cliente pediu prorrogação"
```

#### 🗑️ Limpeza de Contexto
```
"Limpar histórico" ← reseta a conversa
```

---

## ⚙️ CONFIGURAÇÕES

### **Arquivo: main_v2.py**

```python
# Timeout de sessão (em segundos)
SESSAO_TIMEOUT = 60  # Padrão: 60s

# Modo contínuo (não precisa repetir "Apex")
MODO_CONTINUO = True  # True = ativo | False = wake word sempre
```

### **Arquivo: brain_v2.py**

```python
# Tamanho do histórico de conversa
self.max_historico = 10  # Número de interações mantidas

# Temperatura da IA (criatividade)
temperature=0.3  # 0.0 = robótico | 1.0 = criativo

# Modelo usado
self.model_name = "gemini-2.0-flash-exp"  # Mais recente
```

---

## 🔄 COMO TROCAR PARA A VERSÃO V2

### **Método 1: Renomear Arquivos (Recomendado)**
```bash
# Backup dos originais
mv brain.py brain_original.py
mv main.py main_original.py

# Ativar versão V2
mv brain_v2.py brain.py
mv main_v2.py main.py

# Rodar normalmente
python main.py
```

### **Método 2: Rodar Direto a V2**
```bash
python main_v2.py
```

---

## 🆚 COMPARAÇÃO: ANTES vs DEPOIS

| Aspecto | Versão Original | Versão V2 |
|---------|----------------|-----------|
| **Wake Word** | Obrigatório sempre | Opcional (modo contínuo) |
| **Memória** | Sem histórico | Últimas 10 interações |
| **Detecção de Ação** | JSON forçado | Automática e natural |
| **Timeout** | 30s | 60s (configurável) |
| **Contexto** | Só projeto atual | Conversa completa |
| **Respostas** | Robóticas | Naturais e adaptadas |
| **Tokens** | Risco de estouro | Otimizado |
| **Feedback** | Básico | Rico (timer, status) |

---

## 🐛 TROUBLESHOOTING

### **Problema: "Apex não responde"**
✅ Verifique se o microfone está funcionando
✅ Fale "APEX" claramente para ativar
✅ Aguarde o indicador "🟢 ATIVO"

### **Problema: "Ele não entende comandos de ação"**
✅ Seja mais específico: "manda email" em vez de "comunique"
✅ Use nomes completos em WhatsApp
✅ Verifique se as ferramentas estão configuradas (ferramentas.py)

### **Problema: "Respostas muito longas"**
✅ Use o comando "seja mais breve nas próximas respostas"
✅ Ajuste a temperatura para 0.1 em brain_v2.py
✅ Aperte ESPAÇO para interromper

### **Problema: "Sessão expira muito rápido"**
✅ Aumente SESSAO_TIMEOUT em main_v2.py
✅ Ative MODO_CONTINUO = True

---

## 🎓 DICAS DE USO AVANÇADO

### **1. Aproveite o Contexto**
```
VOCÊ: "Qual a situação do Rivelare?"
APEX: [explica]

VOCÊ: "E quanto ao cronograma?" ← ele sabe que é do Rivelare
APEX: [responde sobre cronograma do Rivelare]
```

### **2. Combine Consulta + Ação**
```
VOCÊ: "Verifica o status do projeto 1236 e manda email pro cliente"
APEX: [analisa projeto] + [envia email automaticamente]
```

### **3. Use Anotações como Memória**
```
VOCÊ: "Anote que o cliente do Rivelare está insatisfeito com prazo"
[Semana depois]
VOCÊ: "Qual a situação do Rivelare?"
APEX: "... além disso, você anotou que cliente está insatisfeito..."
```

### **4. Limpe o Histórico em Mudanças de Contexto**
```
VOCÊ: [conversando sobre projetos de SP]
VOCÊ: "Limpar histórico"
VOCÊ: "Agora me fala dos projetos do RJ" ← conversa fresca
```

---

## 📦 ARQUIVOS DA VERSÃO V2

- **brain_v2.py** → Cérebro melhorado (memória + contexto)
- **main_v2.py** → Interface melhorada (modo contínuo)
- **GUIA_V2.md** → Este documento

**Arquivos não modificados:**
- voz.py
- ferramentas.py
- config.py
- correio.py
- tracker.py
- zoho_sync.py

---

## 🚀 PRÓXIMOS PASSOS (Sugestões)

1. **Integração com Calendário** → "Apex, marca reunião amanhã às 14h"
2. **Lembretes Proativos** → Ele avisa quando projeto está atrasando
3. **Comandos por Gestos** → Controle com webcam
4. **Interface Gráfica** → Dashboard visual estilo Homem de Ferro
5. **Modo Telefone** → Atender ligações e ler mensagens

---

## 📞 SUPORTE

Se encontrar bugs ou tiver sugestões:
1. Documente o erro com print/log
2. Verifique configurações em config.py e .env
3. Teste com comandos simples primeiro
4. Aumente verbosidade: adicione prints em brain_v2.py

---

**Versão:** 2.0  
**Data:** Fevereiro 2026  
**Status:** ✅ Pronto para Produção
