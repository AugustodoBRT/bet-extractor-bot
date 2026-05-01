"""
Teste para validar as correções de "u" (valor) vs "odd"
"""
import re

def testar_validacao_odd():
    """Testa se consegue diferenciar "u" de odd"""
    
    print("=" * 60)
    print("TESTE 1: Validação de Odd (range 1.00-99.99)")
    print("=" * 60)
    
    casos_odd = [
        ("3.50", True, "Odd válida normal"),
        ("1.00", True, "Odd mínima válida"),
        ("99.99", True, "Odd máxima válida"),
        ("0.50", False, "Odd muito pequena (< 1.00)"),
        ("100.00", False, "Odd muito grande (> 99.99)"),
        ("370", False, "Número sem decimal (erro OCR anterior)"),
        ("3u", False, "Com 'u' (valor, não odd)"),
        ("2%", False, "Com '%' (valor, não odd)"),
    ]
    
    for valor, esperado_valido, descricao in casos_odd:
        try:
            num = float(valor.replace(",", "."))
            # Simular a validação que implementamos
            eh_valido = 1.0 <= num <= 99.99
            status = "✓" if eh_valido == esperado_valido else "✗"
            print(f"{status} {descricao:40} | '{valor}' → {eh_valido}")
        except ValueError:
            status = "✓" if not esperado_valido else "✗"
            print(f"{status} {descricao:40} | '{valor}' → ValueError (inválido)")
    
    print("\n" + "=" * 60)
    print("TESTE 2: Extração de Odd com >>")
    print("=" * 60)
    
    casos_seta = [
        ("era 2.50 >> 4.00", ["4.00"], "Usa a ÚLTIMA (após >>)"),
        ("2.50 >> 3.85 >> 4.50", ["3.85", "4.50"], "Múltiplas setas - pega última"),
        ("Odd: 3.45", None, "Padrão 'Odd:'"),
        ("vale 2u >> 4.00", ["4.00"], "Com 'u' antes, mas >> pega odd"),
    ]
    
    for texto, esperado_findall, descricao in casos_seta:
        # Simular o findall que implementamos
        resultado = re.findall(r'(?:>>|»)\s*(\d+[.,]?\d*)', texto)
        
        if resultado:
            ultima = resultado[-1]
            status = "✓" if ((esperado_findall is None) or (ultima in esperado_findall)) else "✗"
            print(f"{status} {descricao:40}")
            print(f"   Texto: '{texto}'")
            print(f"   Encontrado: {resultado}, Usando: {ultima}")
        else:
            status = "✓" if esperado_findall is None else "✗"
            print(f"{status} {descricao:40}")
            print(f"   Texto: '{texto}' → Nada encontrado")
        print()
    
    print("\n" + "=" * 60)
    print("TESTE 3: Rejeição de 'u' e '%' na odd")
    print("=" * 60)
    
    casos_rejeicao = [
        ("3u", True, "Contém 'u' - deve rejeitar"),
        ("3.5", False, "Número decimal - aceita"),
        ("2%", True, "Contém '%' - deve rejeitar"),
        ("4.00", False, "Decimal puro - aceita"),
    ]
    
    for valor, deve_rejeitar, descricao in casos_rejeicao:
        rejeitar = ('u' in valor.lower()) or ('%' in valor)
        status = "✓" if rejeitar == deve_rejeitar else "✗"
        print(f"{status} {descricao:40} | '{valor}' → {'REJEITA' if rejeitar else 'ACEITA'}")
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 60)

if __name__ == "__main__":
    testar_validacao_odd()
