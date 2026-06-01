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
    NOME_ABA = "Junho26"
    sheet = spreadsheet.worksheet(NOME_ABA)
    print(f"✅ Conectado à planilha GeogeTips, aba: {NOME_ABA}")
        
except Exception as e:
    print(f"❌ Erro ao conectar Google Sheets: {e}")
    print("💡 SOLUÇÃO: Coloque o arquivo 'credenciais.json' na pasta do projeto")
    sheet = None


import time

def salvar_sheets(dados):
    global sheet
    
    if sheet is None:
        raise Exception("❌ Conexão com Google Sheets não estabelecida!")
    
    tentativa = 1
    while True:
        try:
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
            # Col L: RECORD ID (Invisível/Para controle)
            
            record_id = dados.get("record_id")
            target_row = None
            existing_row = []
            
            if record_id:
                try:
                    col_l = sheet.col_values(12)  # coluna L = 12
                    if record_id in col_l:
                        target_row = col_l.index(record_id) + 1
                        # Busca a linha existente para não sobrescrever dados com vazio
                        existing_row = sheet.row_values(target_row)
                        existing_row += [""] * (12 - len(existing_row))  # Preenche com vazio se for menor
                        print(f"   🔄 Atualizando registro existente na linha {target_row}")
                except Exception as e:
                    # Catch and handle specific quota errors inside here too, though the outer loop will catch it
                    # if it's not swallowed. Actually, if it's swallowed, it won't trigger the retry.
                    # Wait, col_values can hit quota. We should not swallow quota errors.
                    error_str = str(e).lower()
                    if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                        raise e # re-raise to outer loop
                    pass # other exceptions are ignored
                    
            if target_row:
                next_row = target_row
                
                novo_resultado = dados.get("resultado", "PENDENTE")
                resultado_final = novo_resultado if novo_resultado != "PENDENTE" else existing_row[9]
                if not resultado_final:
                    resultado_final = "PENDENTE"
                    
                valores = [
                    existing_row[0],  # A: mantém
                    existing_row[1],  # B: DATA (mantém original)
                    dados.get("esporte") or existing_row[2],
                    dados.get("tipster") or existing_row[3],
                    dados.get("partida") or existing_row[4],
                    dados.get("tip") or existing_row[5],
                    dados.get("casa") or existing_row[6],
                    dados.get("valor") or existing_row[7],
                    dados.get("odd") or existing_row[8],
                    resultado_final,  # J: RESULTADO
                    existing_row[10],  # K: LUCRO/PERDA (mantém fórmula)
                    record_id  # L
                ]
            else:
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
                
                print(f"   📍 Inserindo na nova linha {next_row}")
                
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
                    "",  # K: LUCRO/PERDA
                    record_id or "" # L: RECORD ID
                ]
            
            # Prepara lista de células para atualizar
            cells_to_update = []
            
            # Coloca cada valor na célula corresp onda
            for col_idx, valor in enumerate(valores, 1):
                if col_idx == 11: # NUNCA sobrescreve a coluna K (LUCRO/PERDA) para preservar fórmulas
                    continue
                cell = gspread.Cell(row=next_row, col=col_idx, value=valor)
                cells_to_update.append(cell)
            
            # Atualiza todas as células usando USER_ENTERED para que o Google Sheets reconheça números e moedas
            sheet.update_cells(cells_to_update, value_input_option='USER_ENTERED')
            
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
                error_str = str(e).lower()
                if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                    raise e # re-raise to outer loop
                print(f"⚠️ Aviso: Não foi possível formatar aparência da célula - {e}")
                
            print(f"✅ Aposta salva com sucesso!")
            print(f"   📍 Linha {next_row} (EuTips)")
            print(f"   📊 {dados.get('esporte')} - {dados.get('partida')}")
            
            # Deu certo, sai do loop
            break
            
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str or "exhausted" in error_str or "rate limit" in error_str:
                print(f"⚠️ Limite da API do Google Sheets atingido (Quota 429).")
                print(f"⏳ Aguardando 60 segundos antes de tentar novamente... (Tentativa {tentativa})")
                time.sleep(60)
                tentativa += 1
            else:
                # Se for outro erro (ex: falha de rede), joga para cima
                raise e