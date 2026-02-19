#!/usr/bin/env python3
"""
Visualizador de Logs do Apex
Ferramenta para analisar e debugar erros
"""

import os
from pathlib import Path
from datetime import datetime
import sys

class LogViewer:
    def __init__(self):
        self.pasta_logs = Path("logs")
        
    def listar_arquivos_log(self):
        """Lista todos os arquivos de log disponíveis"""
        if not self.pasta_logs.exists():
            print("❌ Pasta 'logs/' não encontrada!")
            return []
        
        arquivos = list(self.pasta_logs.glob("*.log"))
        return sorted(arquivos, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def exibir_menu(self):
        """Exibe menu interativo"""
        print("="*70)
        print("🔍 VISUALIZADOR DE LOGS - APEX")
        print("="*70)
        
        arquivos = self.listar_arquivos_log()
        
        if not arquivos:
            print("\n❌ Nenhum arquivo de log encontrado!")
            print("Execute o Apex primeiro para gerar logs.\n")
            return
        
        print("\nArquivos disponíveis:\n")
        for i, arquivo in enumerate(arquivos, 1):
            tamanho = arquivo.stat().st_size / 1024  # KB
            modificado = datetime.fromtimestamp(arquivo.stat().st_mtime)
            print(f"  {i}. {arquivo.name:<30} | {tamanho:>7.1f} KB | {modificado.strftime('%d/%m %H:%M')}")
        
        print("\nOpções:")
        print("  E - Ver apenas ERROS (erros.log)")
        print("  A - Ver apenas AÇÕES (acoes.log)")
        print("  H - Ver log de HOJE")
        print("  T - Ver TODOS os logs (modo tail)")
        print("  L - LIMPAR logs antigos")
        print("  0 - Sair")
        print()
        
        escolha = input("Escolha uma opção: ").strip().upper()
        
        if escolha == '0':
            return
        elif escolha == 'E':
            self.ver_erros()
        elif escolha == 'A':
            self.ver_acoes()
        elif escolha == 'H':
            self.ver_log_hoje()
        elif escolha == 'T':
            self.ver_todos_tail()
        elif escolha == 'L':
            self.limpar_logs_antigos()
        elif escolha.isdigit() and 1 <= int(escolha) <= len(arquivos):
            self.ver_arquivo(arquivos[int(escolha) - 1])
        else:
            print("❌ Opção inválida!")
    
    def ver_erros(self):
        """Mostra apenas erros"""
        arquivo = self.pasta_logs / "erros.log"
        
        if not arquivo.exists():
            print("\n✅ Nenhum erro registrado! Sistema rodando perfeitamente.\n")
            return
        
        print("\n" + "="*70)
        print("❌ REGISTRO DE ERROS")
        print("="*70 + "\n")
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        if not linhas:
            print("✅ Nenhum erro registrado!\n")
            return
        
        # Mostra últimos 50 erros
        for linha in linhas[-50:]:
            if "ERROR" in linha or "CRITICAL" in linha:
                print(f"🔴 {linha.strip()}")
            elif "WARNING" in linha:
                print(f"🟡 {linha.strip()}")
        
        print(f"\n📊 Total de linhas no arquivo: {len(linhas)}")
        print("="*70 + "\n")
        
        input("Pressione ENTER para continuar...")
    
    def ver_acoes(self):
        """Mostra ações executadas"""
        arquivo = self.pasta_logs / "acoes.log"
        
        if not arquivo.exists():
            print("\n📭 Nenhuma ação registrada ainda.\n")
            return
        
        print("\n" + "="*70)
        print("⚡ AÇÕES EXECUTADAS")
        print("="*70 + "\n")
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        # Mostra últimas 30 ações
        for linha in linhas[-30:]:
            print(f"⚙️  {linha.strip()}")
        
        print(f"\n📊 Total de ações: {len(linhas)}")
        print("="*70 + "\n")
        
        input("Pressione ENTER para continuar...")
    
    def ver_log_hoje(self):
        """Mostra log do dia atual"""
        hoje = datetime.now().strftime("%Y-%m-%d")
        arquivo = self.pasta_logs / f"apex_{hoje}.log"
        
        if not arquivo.exists():
            print(f"\n❌ Log de hoje ({hoje}) não encontrado.")
            print("O Apex ainda não foi executado hoje.\n")
            return
        
        self.ver_arquivo(arquivo)
    
    def ver_arquivo(self, caminho):
        """Visualiza conteúdo de um arquivo"""
        print("\n" + "="*70)
        print(f"📄 ARQUIVO: {caminho.name}")
        print("="*70 + "\n")
        
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Colorização básica
            for linha in conteudo.split('\n'):
                if "CRITICAL" in linha:
                    print(f"🔴 {linha}")
                elif "ERROR" in linha:
                    print(f"🟠 {linha}")
                elif "WARNING" in linha:
                    print(f"🟡 {linha}")
                elif "INFO" in linha:
                    print(f"🔵 {linha}")
                elif "DEBUG" in linha:
                    print(f"⚪ {linha}")
                else:
                    print(linha)
            
            print("\n" + "="*70 + "\n")
            
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}\n")
        
        input("Pressione ENTER para continuar...")
    
    def ver_todos_tail(self):
        """Mostra últimas linhas de todos os logs (estilo tail -f)"""
        print("\n" + "="*70)
        print("📜 ÚLTIMAS ATIVIDADES (Tail)")
        print("="*70 + "\n")
        
        arquivos = self.listar_arquivos_log()
        
        for arquivo in arquivos[:3]:  # 3 mais recentes
            print(f"\n--- {arquivo.name} ---")
            
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                
                for linha in linhas[-10:]:  # Últimas 10 linhas
                    print(f"  {linha.rstrip()}")
                    
            except Exception as e:
                print(f"  ❌ Erro: {e}")
        
        print("\n" + "="*70 + "\n")
        input("Pressione ENTER para continuar...")
    
    def limpar_logs_antigos(self):
        """Remove logs com mais de 7 dias"""
        from datetime import timedelta
        
        print("\n🧹 Limpando logs antigos...")
        
        data_limite = datetime.now() - timedelta(days=7)
        removidos = 0
        
        for arquivo in self.pasta_logs.glob("apex_*.log"):
            try:
                nome = arquivo.stem
                data_str = nome.split("_")[1]
                data_arquivo = datetime.strptime(data_str, "%Y-%m-%d")
                
                if data_arquivo < data_limite:
                    arquivo.unlink()
                    print(f"  ✅ Removido: {arquivo.name}")
                    removidos += 1
                    
            except Exception as e:
                print(f"  ⚠️  Erro ao processar {arquivo.name}: {e}")
        
        if removidos == 0:
            print("  📭 Nenhum log antigo para remover.")
        else:
            print(f"\n✅ {removidos} arquivo(s) removido(s)!")
        
        print()
        input("Pressione ENTER para continuar...")
    
    def buscar_erro_especifico(self, termo):
        """Busca termo específico nos logs de erro"""
        arquivo = self.pasta_logs / "erros.log"
        
        if not arquivo.exists():
            print("\n✅ Nenhum arquivo de erros encontrado!\n")
            return
        
        print(f"\n🔍 Buscando '{termo}' em erros...")
        print("="*70 + "\n")
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            encontrados = [linha for linha in f if termo.lower() in linha.lower()]
        
        if not encontrados:
            print(f"❌ Nenhuma ocorrência de '{termo}' encontrada.\n")
        else:
            for linha in encontrados:
                print(f"🔴 {linha.strip()}")
            print(f"\n📊 {len(encontrados)} ocorrência(s) encontrada(s)!\n")
        
        input("Pressione ENTER para continuar...")

def main():
    viewer = LogViewer()
    
    while True:
        try:
            viewer.exibir_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Saindo...\n")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}\n")

if __name__ == "__main__":
    main()
