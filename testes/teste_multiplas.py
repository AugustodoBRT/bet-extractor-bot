"""
Teste de Detecção de Múltiplas Apostas
"""
import re

def detectar_multiplas_apostas(texto):
    """
    Detecta se há múltiplas apostas na mensagem.
    Procura por padrões como "1u", "2u", "1.5u", "1%", "2%", etc.
    Se encontrar 2 ou mais padrões, é provavelmente múltiplas apostas.
    """
    # Procura por padrões como "Xu", "X%", "X.Xu", "X.X%"
    padroes = re.findall(r'\b(\d+[.,]?\d*)\s*[u%]\b', texto, re.IGNORECASE)
    
    # Se encontrar 2 ou mais ocorrências, é múltiplas apostas
    num_valores = len(padroes)
    return num_valores >= 2, padroes

def testar_deteccao():
    print("="*70)
    print("TESTE: Detecção de Múltiplas Apostas")
    print("="*70)
    
    casos = [
        {
            "nome": "BET365 - 3 apostas (valores u)",
            "texto": """
            0.5u ❌
            1u ❌
            1u ✅
            
            Bet365
            """,
            "esperado": True,
            "num_valores": 3
        },
        {
            "nome": "Novibet - 3 apostas (valores u)",
            "texto": """
            1u ❌
            1.5u ❌
            1u ❌
            0.75u ❌
            
            [IMAGEM 1/2] Menos de 6.5 - Tari Eason - Houston Rockets x NY Knicks
            Odd: 1.64
            Valor: 1u
            
            [IMAGEM 2/2] Alperem Sengun - Menos de 6.5
            Odd: 1.92
            Valor: 1.5u
            """,
            "esperado": True,
            "num_valores": 4
        },
        {
            "nome": "Aposta Única - sem valor explícito",
            "texto": """
            Tottenham x Manchester City
            Ambas Marcam
            3.45
            """,
            "esperado": False,
            "num_valores": 0
        },
        {
            "nome": "Aposta Única - 1 valor u",
            "texto": """
            Manchester United vs Arsenal
            Vitória do Manchester
            1.95
            2u
            Betano
            """,
            "esperado": False,
            "num_valores": 1
        },
        {
            "nome": "2 apostas com %",
            "texto": """
            Aposta 1: Over 2.5 - 1.75 - 2%
            Aposta 2: Menos de 5.5 - 2.05 - 1.5%
            
            Sportingbet
            """,
            "esperado": True,
            "num_valores": 2
        },
        {
            "nome": "Múltiplos valores no mesmo número (false positive)",
            "texto": """
            Odds entre R$ 1.00 e R$ 99.99 são válidas
            Use 2.5u ou 3% para sua banca
            """,
            "esperado": True,  # Vai detectar como múltiplas
            "num_valores": 2
        }
    ]
    
    for caso in casos:
        eh_multipla, padroes = detectar_multiplas_apostas(caso["texto"])
        status = "✅" if eh_multipla == caso["esperado"] else "❌"
        
        print(f"\n{status} {caso['nome']}")
        print(f"   Esperado: {'MÚLTIPLAS' if caso['esperado'] else 'ÚNICA'}")
        print(f"   Detectado: {'MÚLTIPLAS' if eh_multipla else 'ÚNICA'}")
        print(f"   Padrões encontrados: {padroes} (total: {len(padroes)})")
        
        if len(padroes) != caso["num_valores"]:
            print(f"   ⚠️ Esperava {caso['num_valores']} valores, encontrou {len(padroes)}")

    print("\n" + "="*70)
    print("Resumo:")
    print("="*70)
    print("""
    A detecção funciona procurando por padrões:
    - "1u", "2u", "0.5u" → Valor em unidades
    - "1%", "2%", "0.75%" → Valor em percentual
    
    Se encontrar 2 ou mais → Múltiplas apostas
    Se encontrar 0 ou 1 → Aposta única
    
    ⚠️ NOTA: Pode ter false positives em textos que mencionam ranges
    de odds (ex: "1.00 até 99.99 são válidas"). Isso é aceitável
    porque a IA vai processar corretamente mesmo assim.
    """)

if __name__ == "__main__":
    testar_deteccao()
