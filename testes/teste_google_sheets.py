#!/usr/bin/env python3
"""
Script para testar a conexão com Google Sheets
Execute: python teste_google_sheets.py
"""

import os
import sys
import json

def teste_1_credenciais():
    """Verifica se credenciais.json existe"""
    print("\n" + "="*60)
    print("✓ TESTE 1: Verificando credenciais.json")
    print("="*60)
    
    if os.path.exists("credenciais.json"):
        print("✅ Arquivo encontrado!")
        
        # tenta ler e validar JSON
        try:
            with open("credenciais.json", "r") as f:
                creds = json.load(f)
            
            client_email = creds.get("client_email", "")
            print(f"✅ Email da conta: {client_email}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Erro: JSON inválido - {e}")
            return False
    else:
        print("❌ ARQUIVO NÃO ENCONTRADO!")
        print("📍 Esperado em:", os.path.abspath("credenciais.json"))
        print("\n💡 SOLUÇÃO: Siga o guia em ERRO_GOOGLE_SHEETS.md")
        return False


def teste_2_dependencias():
    """Verifica se as dependências estão instaladas"""
    print("\n" + "="*60)
    print("✓ TESTE 2: Verificando dependências")
    print("="*60)
    
    dependencias = ["gspread", "google", "google.oauth2"]
    faltam = []
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep} instalado")
        except ImportError:
            print(f"❌ {dep} NÃO instalado")
            faltam.append(dep)
    
    if faltam:
        print(f"\n💡 SOLUÇÃO: Execute:")
        print("pip install -r requirements.txt")
        return False
    
    return True


def teste_3_conexao():
    """Tenta conectar ao Google Sheets"""
    print("\n" + "="*60)
    print("✓ TESTE 3: Conectando ao Google Sheets")
    print("="*60)
    
    try:
        from google_sheets import sheet, salvar_sheets
        
        if sheet is None:
            print("❌ Conexão falhou")
            print("Possíveis causas:")
            print("  1. credenciais.json não existe ou é inválido")
            print("  2. APIs não ativadas no Google Cloud")
            print("  3. Planilha 'BETS' não existe")
            return False
        
        print(f"✅ Conectado!")
        print(f"✅ Sheet: {sheet.title}")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_4_salvar():
    """Tenta salvar um dado de teste"""
    print("\n" + "="*60)
    print("✓ TESTE 4: Salvando dados de teste")
    print("="*60)
    
    try:
        from google_sheets import salvar_sheets
        
        dados_teste = {
            "esporte": "TESTE",
            "partida": "Teste vs Teste",
            "tip": "Teste",
            "casa": "Testbet",
            "valor": "1",
            "odd": "1.01"
        }
        
        print("Enviando dados...")
        salvar_sheets(dados_teste)
        print("✅ Dados salvos com sucesso!")
        print("💡 Verifique sua planilha BETS no Google Sheets")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  TESTE DE CONEXÃO - GOOGLE SHEETS".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    resultados = []
    
    # Executa testes
    resultados.append(("Credenciais", teste_1_credenciais()))
    
    if resultados[0][1]:  # só continua se credenciais exist
        resultados.append(("Dependências", teste_2_dependencias()))
        
        if resultados[1][1]:  # só continua se dependências ok
            resultados.append(("Conexão", teste_3_conexao()))
            
            if resultados[2][1]:  # só continua se conexão ok
                resultados.append(("Salvar dados", teste_4_salvar()))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for nome, resultado in resultados:
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{status} - {nome}")
    
    # Status final
    todos_ok = all(r for _, r in resultados)
    
    print("\n" + "="*60)
    if todos_ok:
        print("🎉 TUDO FUNCIONANDO! O bot está pronto!")
    else:
        print("❌ Alguns testes falharam. Veja os erros acima.")
        print("📖 Leia: ERRO_GOOGLE_SHEETS.md para soluções")
    print("="*60 + "\n")
    
    return 0 if todos_ok else 1


if __name__ == "__main__":
    sys.exit(main())
