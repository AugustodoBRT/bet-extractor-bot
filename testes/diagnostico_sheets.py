#!/usr/bin/env python3
"""
Script de diagnóstico para entender o problema com Google Sheets
"""

import sys
from google_sheets import client, sheet

def main():
    print("\n" + "="*70)
    print("🔍 DIAGNÓSTICO: PROBLEMA COM GOOGLE SHEETS")
    print("="*70)
    
    # 1. URL da planilha
    print("\n1️⃣ QUAL PLANILHA ESTÁ SENDO USADA?")
    print("-" * 70)
    spreadsheet_id = sheet.spreadsheet.id
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    print(f"📍 URL: {url}")
    print(f"\n💡 COPIE E COLE ESTA URL NO NAVEGADOR!")
    print("   Verifique se é realmente a sua planilha BETS.\n")
    
    # 2. Qual aba está sendo usada
    print("\n2️⃣ QUAL ABA ESTÁ SENDO USADA?")
    print("-" * 70)
    print(f"📌 Aba ativa: '{sheet.title}'")
    print(f"\n📋 Todas as abas disponíveis:")
    all_sheets = sheet.spreadsheet.worksheets()
    for ws in all_sheets:
        ativo = " ← ESTÁ AQUI" if ws.title == sheet.title else ""
        print(f"   - {ws.title}{ativo}")
    
    # 3. Verificar se a aba é a certa
    print("\n3️⃣ COMO ESTÁ A ABA AGORA?")
    print("-" * 70)
    all_values = sheet.get_all_values()
    print(f"Total de linhas: {len(all_values)}")
    print(f"Total de colunas: {len(all_values[0]) if all_values else 0}")
    
    if len(all_values) > 0:
        print(f"\n📊 ESTRUTURA DA ABA:")
        print(f"Linha 1 (cabeçalho): {all_values[0][:10]}")  # primeiras 10 colunas
        print(f"Linha 2 (amostra): {all_values[1][:10] if len(all_values) > 1 else 'N/A'}")
    
    # 4. Onde o teste foi adicionado
    print("\n4️⃣ ENCONTRANDO O DADO DE TESTE")
    print("-" * 70)
    print("Procurando linhas com 'TESTE' ou data 20/03/2026...")
    
    encontradas = []
    for idx, row in enumerate(all_values, 1):
        row_str = str(row).upper()
        if "TESTE" in row_str or "20/03/2026" in str(row):
            encontradas.append((idx, row))
    
    if encontradas:
        print(f"\n✅ Encontradas {len(encontradas)} linha(s):")
        for linha_num, conteudo in encontradas[-5:]:  # últimas 5
            print(f"\n   Linha {linha_num}:")
            for col_num, valor in enumerate(conteudo[:15], 1):  # primeiras 15 colunas
                if valor:
                    print(f"      Col {col_num}: {valor}")
    else:
        print("\n❌ Nenhuma linha com 'TESTE' encontrada!")
    
    # 5. Recomendações
    print("\n" + "="*70)
    print("💡 POSSÍVEIS PROBLEMAS E SOLUÇÕES:")
    print("="*70)
    print("""
1. ❌ A URL acima NÃO é sua planilha BETS?
   → Você pode ter uma outra planilha BETS não compartilhada com o bot
   → SOLUÇÃO: Compartilhe a planilha CERTA com bot-apostas@bot-apostinha.iam.gserviceaccount.com
   
2. ✅ A URL é correta, mas os dados não aparecem?
   → Pode ser que a estrutura das colunas seja diferente
   → SOLUÇÃO: Abra a planilha e verifique o cabeçalho real no Google Sheets
   
3. ✅ Os dados aparecem na aba errada?
   → A aba pode ter sido alterada durante o desenvolvimento
   → SOLUÇÃO: Mude o nome da aba em google_sheets.py ou adicione a lógica de criar a aba correta
    """)
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
