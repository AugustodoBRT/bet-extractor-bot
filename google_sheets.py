import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# escopos
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# conecta
try:
    if not os.path.exists("credenciais.json"):
        raise FileNotFoundError("❌ Arquivo 'credenciais.json' não encontrado! Baixe em: https://console.cloud.google.com/")
    
    creds = Credentials.from_service_account_file("credenciais.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    
    # abre planilha
    spreadsheet = client.open("GeogeTips")
    
    # abre a aba correta
    NOME_ABA = "Abril26"
    sheet = spreadsheet.worksheet(NOME_ABA)
    print(f"✅ Conectado à planilha GeogeTips, aba: {NOME_ABA}")
        
except Exception as e:
    print(f"❌ Erro ao conectar Google Sheets: {e}")
    print("💡 SOLUÇÃO: Coloque o arquivo 'credenciais.json' na pasta do projeto")
    sheet = None


def salvar_sheets(dados):
    global sheet
    
    if sheet is None:
        raise Exception("❌ Conexão com Google Sheets não estabelecida!")
    
    # ✅ FORMATO CORRETO (conforme planilha BETS):
    # Col A: (vazio)
    # Col B: DATA
    # Col C: ESPORTE
    # Col D: TIPSTER
    # Col E: PARTIDA
    # Col F: TIP
    # Col G: BOOKIE (CASA)
    # Col H: VALOR
    # Col I: ODD
    # Col J: RESULTADO
    # Col K: LUCRO/PERDA
    
    # Próxima linha vazia na coluna B (DATA)
    # Pega só a coluna B para encontrar a primeira linha sem data preenchida
    col_b = sheet.col_values(2)  # coluna B = 2
    
    # Procura a primeira célula vazia a partir da linha 4 (após header na linha 3)
    next_row = 4  # começa na primeira linha de dados
    for i in range(3, len(col_b)):  # índice 3 = linha 4 (0-indexed)
        if col_b[i].strip() != "":
            next_row = i + 2  # pula para a próxima linha
        else:
            next_row = i + 1  # esta linha está vazia, usa ela
            break
    else:
        # se todas as linhas têm conteúdo, vai pra próxima após a última
        next_row = len(col_b) + 1
    
    print(f"   📍 Inserindo na linha {next_row}")
    
    # Prepara lista de células para atualizar
    cells_to_update = []
    
    valores = [
        "",  # A
        datetime.now().strftime("%d/%m/%Y"),  # B: DATA
        dados.get("esporte", ""),  # C: ESPORTE
        dados.get("tipster", ""),  # D: TIPSTER
        dados.get("partida", ""),  # E: PARTIDA
        dados.get("tip", ""),  # F: TIP
        dados.get("casa", ""),  # G: BOOKIE (CASA)
        dados.get("valor", ""),  # H: VALOR
        dados.get("odd", ""),  # I: ODD
        dados.get("resultado", "PENDENTE"),  # J: RESULTADO
        ""   # K: LUCRO/PERDA
    ]
    
    # Coloca cada valor na célula corresp onda
    for col_idx, valor in enumerate(valores, 1):
        cell = gspread.Cell(row=next_row, col=col_idx, value=valor)
        cells_to_update.append(cell)
    
    # Atualiza todas as células
    sheet.update_cells(cells_to_update)
    
    # Formata a linha para ficar centralizada e com bordas
    try:
        sheet.format(f"B{next_row}:K{next_row}", {
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "borders": {
                "top": {"style": "SOLID", "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                "bottom": {"style": "SOLID", "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                "left": {"style": "SOLID", "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                "right": {"style": "SOLID", "color": {"red": 0.0, "green": 0.0, "blue": 0.0}}
            }
        })
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível formatar aparência da célula - {e}")
        
    print(f"✅ Aposta salva com sucesso!")
    print(f"   📍 Linha {next_row} adicionada na planilha EuTips")
    print(f"   📊 {dados.get('esporte')} - {dados.get('partida')}")