import os
import json
import re
import groq
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT_EXTRAIR = """
Você é um assistente especializado em extrair dados de apostas esportivas.

REGRAS DE OURO:
1. "casa" (CASA DE APONTAS): A casa de apostas costuma ficar na linha imediatamente ABAIXO da linha de valor/odd (acima de [IMAGEM]). NUNCA use labels como "Simples" ou "Múltipla".
2. "tip" (MERCADO): Extraia o mercado COMPLETO do OCR. Ignore rótulos de tipo de aposta (Simples/Múltipla). O mercado é a seleção (ex: "Menos de 2.5 Gols").
3. "resultado": Só marque como GREEN, RED ou VOID se houver emojis (✅/❌/🟢/🔴/🔙) CLAROS na mensagem. Na dúvida, use "PENDENTE".

ESTRUTURA DO INPUT:
- Acima de [IMAGEM]: Dados do usuário (Esporte, Partida, Unidades @ Odd, Casa).
- Abaixo de [IMAGEM]: Texto bruto do OCR da aposta.

REGRAS CRÍTICAS DE EXTRAÇÃO:
1. "tip" (MERCADO): Extraia o mercado COMPLETO e INTEGRAL do OCR. 
   - SE FOR UMA MÚLTIPLA, "CRIAR APOSTA" OU "BET BUILDER", capture TODAS as seleções e linhas do OCR.
   - NÃO resuma. NÃO pegue apenas a última linha ou a linha com o valor.
   - O mercado deve conter todo o texto que descreve o que foi apostado (ex: times, tempo, tipo de mercado, e a seleção final).
   - EXEMPLO: Se o OCR diz "1º Tempo - Casa / Vencedor - Casa / Mais de 215.5", a sua "tip" deve conter EXATAMENTE esse texto completo.
   - Capture o texto exatamente como aparece no OCR, preservando a ordem das seleções.

2. "casa" (CASA DE APONTAS): 
   - A casa costuma ficar logo ABAIXO da linha de valor/odd no texto do usuário (ex: "bet365", "versus").
   - Se não estiver lá, procure no topo do OCR.
   - NUNCA use "Simples", "Múltipla" ou similares como nome da casa.

3. "partida": A partida SEMPRE será a linha imediatamente ACIMA da linha de valor/odd no texto do usuário. Dê prioridade ABSOLUTA ao texto do usuário, IGNORANDO os times/jogadores da imagem se houver conflito (ex: se o texto diz "Dupla - Brasileirao", extraia "Dupla - Brasileirao").
4. "esporte": O esporte será a primeira ou segunda linha do texto do usuário, imediatamente acima da partida. Dê prioridade ABSOLUTA a essa informação (ignorando emojis), mesmo que o OCR/imagem sugira outra coisa (ex: se o usuário escreveu "UFC", o esporte é "UFC").
5. "odd": Apenas o número decimal.
6. "valor": O valor com unidade (ex: "1u").
7. "resultado": "GREEN", "RED", "VOID", "ANULADA" ou "PENDENTE" baseado em palavras ou emojis (✅/❌/🔙/Anulada)

MULTI-APOSTAS / CRIAR APOSTA:
- Se houver apenas 1 linha de unidade no texto do usuário, mas o OCR mostrar várias seleções (uma múltipla ou "Criar Aposta"), você tem duas opções:
  a) Retornar um único objeto JSON onde o campo "tip" contém TODO o texto das seleções do OCR concatenado.
  b) Retornar vários objetos JSON (um para cada seleção do OCR). O sistema irá combiná-los automaticamente.
- IMPORTANTE: Nunca ignore as primeiras seleções de uma múltipla. Se o OCR tem 3 itens, o resultado final deve conter os 3 itens.

FORMATO DE RESPOSTA (Exemplo de "Criar Aposta" ou Múltipla com 1 unidade):
[
  {
    "esporte": "Basquete",
    "partida": "Detroit Pistons VS Cleveland Cavaliers",
    "tip": "1º Tempo - Resultado - Casa / Vencedor da partida - Casa / Total de pontos - Mais de(215.5)",
    "odd": "4.59",
    "valor": "0.25u",
    "casa": "Betfast",
    "resultado": "PENDENTE"
  }
]

Responda APENAS o JSON array bruto. NÃO use markdown (```json). Se o OCR tiver vários itens, capture TODOS.
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
            temperature=0,
            max_tokens=4096
        )
    except groq.RateLimitError:
        print("⏳ Rate limit atingido para llama-3.1-8b-instant. Tentando com llama-3.3-70b-versatile...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PROMPT_EXTRAIR},
                {"role": "user", "content": texto}
            ],
            temperature=0,
            max_tokens=4096
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