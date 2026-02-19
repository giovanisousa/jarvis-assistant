import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="apex_memoria.db"):
        # Garante o caminho absoluto para o banco ficar sempre na raiz do projeto
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(diretorio_atual, db_name)
        self._criar_tabelas()

    def _conectar(self):
        # Conecta sempre usando o caminho absoluto
        return sqlite3.connect(self.db_path)

    def _criar_tabelas(self):
        """Cria as tabelas caso não existam"""
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memorias_projetos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                projeto_id TEXT NOT NULL,
                projeto_nome TEXT NOT NULL,
                nota TEXT NOT NULL,
                data_registro TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    def salvar_nota(self, projeto_id, projeto_nome, nota):
        # BLINDAGEM DUPLA: Garante que a tabela existe antes de inserir 
        # (Protege contra deleção acidental e cache do Streamlit)
        self._criar_tabelas()
        
        conn = self._conectar()
        cursor = conn.cursor()
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        cursor.execute('''
            INSERT INTO memorias_projetos (projeto_id, projeto_nome, nota, data_registro)
            VALUES (?, ?, ?, ?)
        ''', (str(projeto_id), projeto_nome, nota, data_atual))
        
        conn.commit()
        conn.close()
        return True

    def buscar_notas_projeto(self, projeto_id):
        # BLINDAGEM DUPLA: Garante que a tabela existe antes de buscar
        self._criar_tabelas()
        
        conn = self._conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data_registro, nota FROM memorias_projetos
            WHERE projeto_id = ?
            ORDER BY id DESC
        ''', (str(projeto_id),))
        
        resultados = cursor.fetchall()
        conn.close()
        
        return [f"[{linha[0]}] {linha[1]}" for linha in resultados]