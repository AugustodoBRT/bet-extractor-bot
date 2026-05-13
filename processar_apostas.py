import re
import json
import time
from groq_revisor import revisar_aposta_groq
from salvar_csv import salvar_csv
from google_sheets import salvar_sheets
from config import VALOR_UNIDADE, CASAS_APOSTAS

def limpar_sufixo_casa(casa_raw):
    """
    Remove sufixos como (Simples), (Multipla), (Singles), (Aposta) do nome da casa.
    Exemplo: "Novibet (Simples)" → "Novibet"
    """
    if not casa_raw:
        return ""
    
    # Remove texto entre parênteses e espaços extras
    casa_limpo = re.sub(r'\s*\([^)]*\)\s*', '', casa_raw).strip()
    return casa_limpo

def normalizar_casa(casa_raw):
    """Normaliza o nome da casa de apostas para o nome exato da planilha."""
    if not casa_raw:
        return ""
    
    # Primeiro remove sufixos como (Simples), (Multipla)
    casa_limpa = limpar_sufixo_casa(casa_raw)
    casa_lower = casa_limpa.strip().lower()
    
    # Busca exata no dicionário
    if casa_lower in CASAS_APOSTAS:
        return CASAS_APOSTAS[casa_lower]
    
    # Busca parcial — se o nome da casa contém alguma das chaves
    for chave, nome_exato in CASAS_APOSTAS.items():
        if chave in casa_lower or casa_lower in chave:
            return nome_exato
    
    # Se não encontrou, retorna como veio (pode ser uma casa nova)
    print(f"⚠️ Casa '{casa_raw}' não encontrada no mapeamento. Usando como está.")
    return casa_limpa.strip()


def detectar_resultado(texto):
    """Detecta GREEN/RED/PENDENTE baseado em emojis (✅, ✔️, ❌, ✖️, etc)."""
    # Apenas emojis ou palavras inteiras muito específicas
    verde_emojis = ["✅", "✔️", "🟢"]
    vermelho_emojis = ["❌", "✖️", "✖", "🔴"]
    void_emojis = ["🔙"]
    
    txt = str(texto).upper()
    
    if "ANULADA" in txt:
        return "ANULADA"
        
    for e in void_emojis:
        if e in txt:
            return "VOID"
    
    for e in verde_emojis:
        if e in txt:
            return "GREEN"
    for e in vermelho_emojis:
        if e in txt:
            return "RED"
            
    # Busca por palavras inteiras para evitar falsos positivos (ex: "WINNER" vira "WIN")
    if re.search(r"WIN", txt):
        return "GREEN"
    if re.search(r"LOSS", txt):
        return "RED"
            
    return "PENDENTE"


def calcular_valor(valor_raw):
    """
    Converte porcentagem/unidade para valor em reais baseado na banca.
    Ex: "0.5%" ou "0.5u" com VALOR_UNIDADE=2.0 → "R$ 1,00"
        "2%" ou "2u"   com VALOR_UNIDADE=2.0 → "R$ 4,00"
        "1.5%" ou "1.5u" com VALOR_UNIDADE=2.0 → "R$ 3,00"
    Se não for porcentagem nem unidade, retorna como está.
    """
    if not valor_raw:
        return ""
    
    valor_str = valor_raw.strip()
    
    # Tenta extrair porcentagem/unidade (ex: "0.5%", "2u", "1,5%", "0,75u")
    match = re.search(r'(\d+[.,]?\d*)\s*[%u]', valor_str)
    if match:
        pct_str = match.group(1).replace(",", ".")
        try:
            pct = float(pct_str)
            valor_reais = pct * VALOR_UNIDADE
            # Formata como "X,XX" sem o R$
            return f"{valor_reais:,.2f}".replace(".", ",")
        except ValueError:
            pass
    
    # Se já tem R$ ou não é porcentagem, retorna como está
    return valor_str


def remover_apostas_duplicadas(apostas_list):
    """
    Remove apostas EXATAMENTE iguais do array.
    Se a IA retornou a mesma aposta 2x, remove 1.
    """
    if not apostas_list:
        return []
    
    apostas_unicas = []
    apostas_vistas = []
    
    for aposta in apostas_list:
        # Criar uma representação hashable da aposta para comparação
        aposta_str = json.dumps(aposta, sort_keys=True)
        
        if aposta_str not in apostas_vistas:
            apostas_unicas.append(aposta)
            apostas_vistas.append(aposta_str)
        else:
            print(f"⚠️ Aposta duplicada removida: {aposta.get('tip', '')} - {aposta.get('odd', '')}")
    
    return apostas_unicas


def processar_aposta_individual(dados, texto, esporte_fixo=None, tipster=None, casa_fallback=None):
    """
    Processa UMA APOSTA individual com toda a lógica de validação.
    Argumentos:
    - dados: dict com os dados da aposta (retornado pela IA)
    - texto: texto original para extrair informações complementares
    - esporte_fixo: esporte fixo a adicionar aos dados
    
    Retorna: dict com dados processados e validados
    """
    # Cria cópia para não modificar o original
    dados_processado = dados.copy() if isinstance(dados, dict) else {}
    
    # Fallback mínimo se IA não retornar nada
    if not dados_processado:
        dados_processado = {
            "partida": "",
            "tip": "",
            "odd": "",
            "valor": "",
            "casa": ""
        }
    
    if esporte_fixo:
        dados_processado["esporte"] = esporte_fixo
    else:
        dados_processado["esporte"] = dados.get("esporte", "Não identificado")
        
    if tipster:
        dados_processado["tipster"] = tipster
    
    # 📊 Extrai a odd correta com validações
    odd_final = ""
    odd_seq = dados_processado.get("odd_seq", "")
    
    # 0) Busca sequencial da odd identificada após o @ (maior prioridade pedida pelo usuário)
    if odd_seq:
        odd_final = odd_seq
        print(f"📊 Odd sequencial (@): {odd_final}")
    else:
        # Se não tem seq, usa o que a IA retornou (mas NUNCA se contiver 'u' ou '%')
        odd_ia = dados_processado.get("odd", "")
        if odd_ia and 'u' not in odd_ia.lower() and '%' not in odd_ia:
            odd_final = re.sub(r'[^\d.,]', '', odd_ia)
        else:
            odd_final = ""
    # Se ainda não achou nada, tenta busca global como último recurso (apenas se não houver >> )
    if not odd_final:
        todas_odds_seta = re.findall(r'(?:>>|»)\s*(\d+[.,]?\d*)', texto)
        if todas_odds_seta:
            odd_final = todas_odds_seta[-1]
            print(f"📊 Odd após >>: {odd_final}")

    
    # Corrige OCR que perde decimal
    if odd_final and "," not in odd_final and "." not in odd_final:
        try:
            num = int(odd_final)
            if num >= 100:
                odd_corrigida = num / 100
                print(f"📊 Odd corrigida (OCR): {odd_final} → {odd_corrigida}")
                odd_final = f"{odd_corrigida:.2f}"
        except ValueError:
            pass
    
    # Validação final: odd deve estar entre 1.00 e 9999.99
    if odd_final:
        try:
            odd_num = float(odd_final.replace(",", "."))
            if odd_num < 1.0 or odd_num > 9999.99:
                print(f"⚠️ Odd inválida: {odd_final} (fora do range)")
                odd_final = ""
        except ValueError:
            odd_final = ""
    
    # Converte ponto para vírgula para a planilha
    dados_processado["odd"] = odd_final.replace(".", ",") if odd_final else ""
    
    # 💰 Calcula valor baseado na banca
    valor_seq = dados_processado.get("valor_seq", "")
    valor_ia = dados_processado.get("valor", "")
    
    if valor_seq:
        valor_base = valor_seq
        print(f"💰 Valor sequencial utilizado: {valor_base}")
    elif valor_ia and ("%" in valor_ia or "u" in valor_ia):
        valor_base = valor_ia
    else:
        valor_base = ""
        # Fallback global: busca "vale X%", "vale Xu", etc.
        valor_match = re.search(r'(?:vale|valor\s*[%u]?\s*:?)\s*(\d+[.,]?\d*)\s*([%u])', texto, re.IGNORECASE)
        if not valor_match:
            valor_match = re.search(r'(\d+[.,]?\d*)\s*([%u])', texto)
        if valor_match:
            valor_base = valor_match.group(1) + valor_match.group(2)
            print(f"💰 Valor extraído (fallback global): {valor_base}")
    
    valor_convertido = calcular_valor(valor_base)
    
    # Verifica limite da mensagem para não apostar muito alto
    if valor_convertido:
        try:
            valor_num = float(valor_convertido.replace(".", "").replace(",", ".").strip())
            
            # Usa o limite extraído sequencialmente da linha (se houver)
            limite_valor = dados_processado.get("limite_seq")
            if limite_valor is not None:
                if valor_num > limite_valor:
                    print(f"⚠️ Valor calculado ({valor_num:.2f}) ultrapassa o limite da bet ({limite_valor:.2f}). Usando o limite.")
                    valor_convertido = f"{limite_valor:,.2f}".replace(".", ",")
            else:
                # Proteção global (aumentado para evitar erros com apostas propositais longas)
                if valor_num > 2000:
                    print(f"⚠️ Valor descartado por ser irreal: {valor_convertido} (original: {valor_ia})")
                    valor_convertido = ""
        except:
            pass
    
    dados_processado["valor"] = valor_convertido
    dados_processado["unidades"] = str(valor_base).strip().replace('u', '').replace('%', '') if valor_base else ""
    
    # 🎯 Resultado (GREEN/RED/VOID/PENDENTE)
    resultado_seq = dados_processado.get("resultado_seq", "PENDENTE")
    resultado_ia = str(dados_processado.get("resultado", "")).strip().upper()
    resultado_global = detectar_resultado(texto)
    
    # Prioridade ABSOLUTA para mensagens anuladas
    if resultado_global in ["ANULADA", "VOID"]:
        dados_processado["resultado"] = resultado_global
        print(f"🎯 Resultado global utilizado (prioridade): {resultado_global}")
    elif resultado_seq != "PENDENTE":
        dados_processado["resultado"] = resultado_seq
        print(f"🎯 Resultado sequencial utilizado: {resultado_seq}")
    elif resultado_ia in ["GREEN", "RED", "VOID", "ANULADA"]:
        dados_processado["resultado"] = resultado_ia
    else:
        dados_processado["resultado"] = resultado_global
    
    # Casa sugerida do script vs Casa da IA
    casa_raw_script = casa_fallback.strip().lower() if casa_fallback else ""
    casa_raw_ia = str(dados_processado.get("casa", "")).strip().lower()

    # Lista de palavras banidas que nunca podem ser o nome de uma casa
    palavras_banidas = ["simples", "multipla", "múltipla", "single", "multi", "aposta", "vencida", "aberta"]

    casa_final = ""
    
    # 1. Tenta achar a casa sugerida pelo script no dicionário
    if casa_raw_script and casa_raw_script not in palavras_banidas:
        for chave, nome_exato in sorted(CASAS_APOSTAS.items(), key=lambda x: len(x[0]), reverse=True):
            if chave in casa_raw_script:
                casa_final = nome_exato
                break
                    
    # 2. Se não achou a do script, tenta achar a da IA no dicionário
    if not casa_final and casa_raw_ia and casa_raw_ia not in palavras_banidas:
        for chave, nome_exato in sorted(CASAS_APOSTAS.items(), key=lambda x: len(x[0]), reverse=True):
            if chave in casa_raw_ia:
                casa_final = nome_exato
                break
                
    # 3. Se nenhuma está no dicionário, usa a da IA (com primeira maiúscula)
    if not casa_final:
        if casa_raw_ia and casa_raw_ia not in palavras_banidas:
            casa_final = casa_raw_ia.title()
        elif casa_raw_script and casa_raw_script not in palavras_banidas:
            casa_final = casa_raw_script.title()

            
            
    dados_processado["casa"] = casa_final
    return dados_processado

def processar_aposta(texto, esporte_fixo=None, tipster=None, message_id=None):
    print("="*50)
    print("📩 TEXTO RECEBIDO PELO PROCESSADOR:\n")
    print(texto)
    print(f"🆔 Message ID: {message_id}")
    print("="*50)
    
    # MENSAGEM DO USUÁRIO é a primeira parte antes do separador do OCR (se houver)
    mensagem_usuario = str(texto).split("\n\n-----\n\n")[0]
    
    # Extrai a casa de forma mais inteligente (linha logo abaixo da odd)
    linhas_msg = [l.strip() for l in mensagem_usuario.split("\n") if l.strip()]
    
    casa_ultima_linha = ""
    indice_odd = -1
    for i, linha in enumerate(linhas_msg):
        if re.search(r'(?:@|odd)\s*(\d+[.,]?\d*)', linha, re.IGNORECASE):
            indice_odd = i
            
    if indice_odd != -1 and indice_odd + 1 < len(linhas_msg):
        casa_ultima_linha = linhas_msg[indice_odd + 1]
    elif linhas_msg:
        casa_ultima_linha = linhas_msg[-1]
        
    print(f"🏠 Casa identificada pelo script: {casa_ultima_linha}")
    # A casa será extraída e normalizada individualmente por aposta
    casa_global = ""


    apostas_list = []

    # 🤖 IA - Sempre retorna um array de apostas
    try:
        apostas_list = revisar_aposta_groq(texto)
        if not isinstance(apostas_list, list):
            apostas_list = [apostas_list]
        
        # Remove apostas EXATAMENTE duplicadas (IA retornou mesma aposta 2x)
        apostas_list = remover_apostas_duplicadas(apostas_list)
        
        print(f"🤖 IA OK - {len(apostas_list)} aposta(s) extraída(s)")

    except Exception as e:
        print("🤖 IA falhou:", e)
        # Fallback: cria uma aposta vazia
        apostas_list = [{
            "partida": "",
            "tip": "",
            "odd": "",
            "valor": "",
            "casa": ""
        }]

    # 🔄 Processa determinístico (lista na mensagem)
    lista_valores_seq = []
    # Usamos mensagem_usuario para extrair a lista, assim não pega OCR lixo
    matches = list(re.finditer(r'(\d+[.,]?\d*\s*[%u])', mensagem_usuario, re.IGNORECASE))
    for i, m in enumerate(matches):
        val = m.group(1).strip()
        start_idx = m.start() # Pega desde o valor
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(mensagem_usuario)
        fragmento = mensagem_usuario[start_idx:end_idx]
        fragmento_upper = fragmento.upper()
        
        verde = ["✅", "✔️", "✔", "🟢", "WIN"]
        vermelho = ["❌", "✖️", "✖", "🔴", "LOSS"]
        void_emojis = ["🔙", "VOID", "DEVOLVIDA", "REEMBOLSO"]
        resultado = "PENDENTE"
        
        for e in void_emojis:
            if e in fragmento_upper:
                resultado = "VOID"
                break
        if resultado == "PENDENTE":
            for v in verde:
                if v in fragmento_upper:
                    resultado = "GREEN"
                    break
        if resultado == "PENDENTE":
            for v in vermelho:
                if v in fragmento_upper:
                    resultado = "RED"
                    break
        
        # Procura odd no fragmento, suportando inteiros "@7" e decimais "@2.1"
        odd_seq = ""
        odd_match = re.search(r'(?:@|odd)\s*(\d+[.,]?\d*)', fragmento, re.IGNORECASE)
        if odd_match:
            odd_seq = odd_match.group(1)
            
        # Procura limite no fragmento, como "limite 100"
        limite_seq = None
        limite_match = re.search(r'limite\s+(\d+[.,]?\d*)', fragmento, re.IGNORECASE)
        if limite_match:
            limite_seq = float(limite_match.group(1).replace(",", "."))
                    
        lista_valores_seq.append({"valor": val, "resultado": resultado, "odd": odd_seq, "limite": limite_seq})
    
    if lista_valores_seq:
        print(f"📊 {len(lista_valores_seq)} Linhas de valores extraídas da mensagem: {lista_valores_seq}")
        
        # ⚠️ REGRA DE OURO DO USUÁRIO: O número de linhas (unidades) dita o número exato de apostas.
        qtd_unidades = len(lista_valores_seq)
        qtd_apostas_ia = len(apostas_list)
        
        if qtd_apostas_ia > qtd_unidades:
            if qtd_unidades == 1:
                print(f"⚠️ IA retornou {qtd_apostas_ia} apostas, mas há apenas 1 linha de unidade. Combinando como Múltipla...")
                
                partidas_combinadas = []
                tips_combinadas = []
                
                for a in apostas_list:
                    p = a.get("partida", "").strip()
                    t = a.get("tip", "").strip()
                    
                    if p and p not in partidas_combinadas:
                        partidas_combinadas.append(p)
                        
                    if t:
                        # Sempre inclui o tip completo, independente do tamanho.
                        # Se o mercado (tip) já menciona a partida, usa só o tip.
                        # Caso contrário, prefixa com a partida para maior clareza.
                        if p and p not in t:
                            tips_combinadas.append(f"{p} - {t}")
                        else:
                            tips_combinadas.append(t)
                
                aposta_unica = apostas_list[0].copy()
                aposta_unica["partida"] = " / ".join(partidas_combinadas) if partidas_combinadas else aposta_unica.get("partida", "")
                aposta_unica["tip"] = " & ".join(tips_combinadas) if tips_combinadas else aposta_unica.get("tip", "")
                
                apostas_list = [aposta_unica]
            else:
                print(f"⚠️ IA retornou {qtd_apostas_ia} apostas, mas há apenas {qtd_unidades} linhas. Truncando...")
                apostas_list = apostas_list[:qtd_unidades]
        elif qtd_apostas_ia < qtd_unidades:
            print(f"⚠️ IA retornou {qtd_apostas_ia} apostas, mas há {qtd_unidades} linhas. Preenchendo a diferença...")
            while len(apostas_list) < qtd_unidades:
                if apostas_list:
                    apostas_list.append(apostas_list[-1].copy())
                else:
                    apostas_list.append({"partida": "", "tip": "", "odd": "", "valor": "", "casa": ""})

    # 🔄 Processa CADA APOSTA
    for idx, dados_aposta in enumerate(apostas_list, 1):
        print(f"\n{'='*50}")
        print(f"📌 PROCESSANDO APOSTA {idx}/{len(apostas_list)}")
        print(f"{'='*50}")
        
        if (idx - 1) < len(lista_valores_seq):
            dados_aposta["valor_seq"] = lista_valores_seq[idx - 1]["valor"]
            dados_aposta["resultado_seq"] = lista_valores_seq[idx - 1]["resultado"]
            if lista_valores_seq[idx - 1].get("odd"):
                dados_aposta["odd_seq"] = lista_valores_seq[idx - 1]["odd"]
            if lista_valores_seq[idx - 1].get("limite") is not None:
                dados_aposta["limite_seq"] = lista_valores_seq[idx - 1]["limite"]

        # Processa a aposta individual
        dados_processado = processar_aposta_individual(dados_aposta, texto, esporte_fixo, tipster, casa_ultima_linha)
        
        # 💾 Salva a aposta usando a casa extraída pela IA e normalizada
        dados_linha = dados_processado.copy()
        if message_id:
            dados_linha["record_id"] = f"{message_id}_{idx}"

        print(f"\n📋 DADOS FINAIS (aposta {idx}, casa: {dados_linha.get('casa')}):")
        for k, v in dados_linha.items():
            print(f"   {k}: {v}")

        # Tenta salvar no Google Sheets
        try:
            salvar_sheets(dados_linha)
            print(f"✅ Salvo no Google Sheets")
        except Exception as e:
            print(f"⚠️ Erro ao salvar no Google Sheets: {e}")
            # Fallback: salva no CSV
            salvar_csv(dados_linha)
            print(f"✅ Salvo no CSV como fallback")
            
        print("⏳ Pausa de 3 segundos para não sobrecarregar as APIs...")
        time.sleep(3)