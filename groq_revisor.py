import os
import json
import re
import groq
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT_EXTRAIR = """
Você é um assistente que extrai apostas de mensagens recebidas no Telegram.
A mensagem contém o texto enviado pelo usuário (caption) e o texto extraído da(s) imagem(ns) (OCR).

LEIA CUIDADOSAMENTE e extraia TODAS as apostas que vir.

IMPORTANTE - Como Identificar Uma Aposta:
Uma aposta consiste em:
1. PARTIDA: O NOME DO JOGO/CONFRONTO entre os dois times (ex: "Houston Rockets x NY Knicks", "MEM Grizzlies @ DEN Nuggets").
   - Para esportes em equipe (futebol, NBA), a partida NUNCA é o nome de um jogador, sempre os TIMES que estão jogando.
   - A partida pode estar em letras pequenas, rodapé, ou com "@" entre os times.
2. MERCADO: O tipo de aposta (ex: "Menos de 6.5 Rebotes", "Vitória", "Ambas Marcam")
   - ATENÇÃO EXTREMA: Se houver VÁRIAS LINHAS de mercado/seleção abaixo de uma partida (ex: Criar Aposta, Bet Builder), você DEVE capturar TODAS ELAS. Não pule nenhuma linha!
3. ODD: Um número decimal (ex: 1.64, 2.25, 3.45)
4. VALOR: Um valor em "u" ou "%" (ex: 1u, 1.5u, 0.75%, 2%)
5. RESULTADO: "GREEN", "RED" ou "PENDENTE". Baseado em emojis (✅/✔️=GREEN, ❌/✖️=RED).

COMO PROCEDER COM MÚLTIPLAS APOSTAS E LISTAS DE VALORES/RESULTADOS:
- É muito comum o usuário enviar uma lista com os valores e resultados na mensagem (ex: "0.5u ❌ \n 1u ✅ \n 1.25u ✅").
- Se houver uma lista assim, você DEVE fazer a correspondência na mesma ordem:
  A 1ª aposta do OCR recebe o 1º valor e resultado da lista.
  A 2ª aposta do OCR recebe o 2º valor e resultado da lista.
  A 3ª aposta do OCR recebe o 3º valor e resultado da lista, e assim por diante.
- Se não houver lista, procure os dados junto de cada aposta ou use "PENDENTE" se não souber o resultado, e "" para valor se não achar.

REGRAS OBRIGATÓRIAS:
- "partida": EXTRAIR O CONFRONTO (Teams). Ex: "Houston Rockets x NY Knicks" ou "MEM Grizzlies @ DEN Nuggets". NUNCA coloque o nome de um único jogador aqui na partida.
- "tip": O mercado/tipo de aposta completo.
  * MÚLTIPLAS/CRIAR APOSTA: Uma Múltipla ou Criar Aposta é UMA ÚNICA APOSTA (um único bloco JSON) que contém várias seleções. Junte TODAS AS LINHAS de seleções em uma única string separada por " & ". Exemplo: "Resultado da Partida - Casa & 1º metade - Resultado - Casa & Ambos os times marcam - Sim". NUNCA ignore seleções! Leia todas as linhas de mercado até chegar na odd/valor e junte-as na tip.
  * SIMPLES: Cada aposta comum ou leg individual deve ser um bloco separado. Ex: "Jamal Murray - Menos de 3.5 Cestas".
- "odd": SÓ número decimal. NUNCA inclua "u" ou "%". Se houver um "@" indicando a odd (ex: "@2.35" ou "@ 1.80"), a odd será EXATAMENTE esse número.
- "valor": O valor exato (ex: "1u", "0.5u").
- "casa": Nome da casa (ex: "Bet365", "Novibet").
- "resultado": "GREEN", "RED" ou "PENDENTE" (sempre em maiúsculo).
- SEMPRE retorne um JSON array [], mesmo para 1 aposta.
- NÃO invente dados.

FORMATO DE RESPOSTA ESPERADO:
[
  {
    "partida": "NSH Predators & UTA Mammoth",
    "tip": "Matthew Wood - Para Marcar um Gol & Luke Evangelista - Para Marcar um Gol",
    "odd": "27.00",
    "valor": "0.25u",
    "casa": "Bet365",
    "resultado": "PENDENTE"
  },
  {
    "partida": "NSH Predators & UTA Mammoth",
    "tip": "Matthew Wood - Para Marcar um Gol",
    "odd": "4.50",
    "valor": "0.5u",
    "casa": "Bet365",
    "resultado": "PENDENTE"
  }
]

Responda SOMENTE com o JSON array, sem nenhum texto antes ou depois.
"""

def revisar_aposta_groq(texto):
    """
    Função única que extrai TODAS as apostas de uma mensagem.
    Sempre retorna um array de apostas.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PROMPT_EXTRAIR},
                {"role": "user", "content": texto}
            ],
            temperature=0
        )
    except groq.RateLimitError:
        print("⏳ Rate limit atingido para llama-3.1-8b-instant. Tentando com llama-3.3-70b-versatile...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PROMPT_EXTRAIR},
                {"role": "user", "content": texto}
            ],
            temperature=0
        )

    conteudo = response.choices[0].message.content.strip()

    print("\n🧠 RESPOSTA BRUTA DA IA:\n", conteudo, "\n")

    try:
        inicio = conteudo.find("[")
        fim = conteudo.rfind("]") + 1

        if inicio == -1 or fim == 0:
            raise ValueError("JSON array não encontrado na resposta da IA")

        json_str = conteudo[inicio:fim]
        apostas = json.loads(json_str)
        
        # Garante que é uma lista
        if not isinstance(apostas, list):
            apostas = [apostas]
        
        return apostas

    except Exception as e:
        print("⚠️ Falha ao parsear JSON:", e)
        raise