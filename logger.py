"""
Sistema de Logging Centralizado do Apex
Captura todos os erros e eventos do sistema
"""

import logging
import os
from datetime import datetime
from pathlib import Path

class ApexLogger:
    """Gerenciador de logs do sistema Apex"""
    
    def __init__(self, nome_modulo="apex"):
        self.nome_modulo = nome_modulo
        
        # Cria pasta de logs se não existir
        self.pasta_logs = Path("logs")
        self.pasta_logs.mkdir(exist_ok=True)
        
        # Define nomes dos arquivos de log
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        self.arquivo_geral = self.pasta_logs / f"apex_{data_hoje}.log"
        self.arquivo_erros = self.pasta_logs / "erros.log"
        self.arquivo_acoes = self.pasta_logs / "acoes.log"
        
        # Configura o logger
        self.logger = self._configurar_logger()
    
    def _configurar_logger(self):
        """Configura o sistema de logging"""
        logger = logging.getLogger(self.nome_modulo)
        logger.setLevel(logging.DEBUG)
        
        # Remove handlers existentes para evitar duplicação
        logger.handlers.clear()
        
        # Formato das mensagens
        formato = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler 1: Arquivo geral (DEBUG e acima)
        handler_geral = logging.FileHandler(self.arquivo_geral, encoding='utf-8')
        handler_geral.setLevel(logging.DEBUG)
        handler_geral.setFormatter(formato)
        logger.addHandler(handler_geral)
        
        # Handler 2: Arquivo de erros (WARNING e acima)
        handler_erros = logging.FileHandler(self.arquivo_erros, encoding='utf-8')
        handler_erros.setLevel(logging.WARNING)
        handler_erros.setFormatter(formato)
        logger.addHandler(handler_erros)
        
        # Handler 3: Console (INFO e acima)
        handler_console = logging.StreamHandler()
        handler_console.setLevel(logging.INFO)
        formato_console = logging.Formatter(
            '%(levelname)s | %(message)s'
        )
        handler_console.setFormatter(formato_console)
        logger.addHandler(handler_console)
        
        return logger
    
    def debug(self, mensagem):
        """Log de debug (detalhes técnicos)"""
        self.logger.debug(mensagem)
    
    def info(self, mensagem):
        """Log de informação (eventos normais)"""
        self.logger.info(mensagem)
    
    def warning(self, mensagem):
        """Log de aviso (atenção necessária)"""
        self.logger.warning(mensagem)
    
    def error(self, mensagem, exception=None):
        """Log de erro (falha recuperável)"""
        if exception:
            self.logger.error(f"{mensagem} | Exceção: {type(exception).__name__}: {str(exception)}")
            # Adiciona stack trace completo
            self.logger.error(f"Stack trace:", exc_info=True)
        else:
            self.logger.error(mensagem)
    
    def critical(self, mensagem, exception=None):
        """Log crítico (falha grave)"""
        if exception:
            self.logger.critical(f"{mensagem} | Exceção: {type(exception).__name__}: {str(exception)}")
            self.logger.critical(f"Stack trace:", exc_info=True)
        else:
            self.logger.critical(mensagem)
    
    def registrar_acao(self, tipo_acao, detalhes):
        """Registra ações executadas pelo Apex"""
        with open(self.arquivo_acoes, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} | {tipo_acao} | {detalhes}\n")
        
        self.info(f"AÇÃO EXECUTADA: {tipo_acao} - {detalhes}")
    
    def registrar_comando(self, usuario, comando, resposta_resumo):
        """Registra comandos do usuário e respostas"""
        self.info(f"COMANDO USUÁRIO: '{comando}'")
        self.debug(f"RESPOSTA (resumo): {resposta_resumo[:100]}...")
    
    def limpar_logs_antigos(self, dias=7):
        """Remove logs com mais de X dias"""
        from datetime import timedelta
        
        data_limite = datetime.now() - timedelta(days=dias)
        
        for arquivo_log in self.pasta_logs.glob("apex_*.log"):
            try:
                # Extrai data do nome do arquivo
                nome = arquivo_log.stem  # apex_2024-02-16
                data_str = nome.split("_")[1]
                data_arquivo = datetime.strptime(data_str, "%Y-%m-%d")
                
                if data_arquivo < data_limite:
                    arquivo_log.unlink()
                    self.info(f"Log antigo removido: {arquivo_log.name}")
            except Exception as e:
                self.warning(f"Erro ao limpar log {arquivo_log.name}: {e}")

# Singleton global para fácil acesso
_logger_instance = None

def get_logger(nome_modulo="apex"):
    """Retorna instância única do logger"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ApexLogger(nome_modulo)
    return _logger_instance

# Testes
if __name__ == "__main__":
    logger = get_logger("teste")
    
    logger.debug("Teste de mensagem DEBUG")
    logger.info("Teste de mensagem INFO")
    logger.warning("Teste de mensagem WARNING")
    logger.error("Teste de mensagem ERROR")
    
    # Simula erro com exceção
    try:
        resultado = 10 / 0
    except Exception as e:
        logger.error("Erro ao dividir por zero", exception=e)
    
    # Registra ação
    logger.registrar_acao("ENVIAR_EMAIL", "Destinatário: teste@exemplo.com")
    
    print("\n✅ Logs criados! Verifique a pasta 'logs/'")
