PASTA_IMAGENS = "imagens"
CSV_PATH = "apostas.csv"

# ===============================
# BANCA - CONFIGURAÇÃO DE VALOR
# ===============================
# Valor em reais de 1% da sua banca.
# Exemplo: se sua banca é R$ 200, 1% = R$ 2,00
# Se subir para R$ 1000, mude para 10.0 (1% de 1000 = 10)
VALOR_UNIDADE = 100.0  # R$ por 1%

# ===============================
# CASAS DE APOSTAS - NOMES EXATOS
# ===============================
# Mapeamento de variações comuns para o nome EXATO da planilha.
# A chave (esquerda) é em minúsculo para comparação.
# O valor (direita) é o nome EXATO como aparece na planilha.
# Para adicionar uma nova casa, basta adicionar uma linha aqui.
CASAS_APOSTAS = {
    # BetPix365
    "betpix365": "BetPix365",
    "betpix": "BetPix365",
    "bet pix 365": "BetPix365",
    "bet pix": "BetPix365",
    # Lottu
    "lottu": "Lottu",
    # BETesporte
    "betesporte": "Betesporte",
    "bet esporte": "Betsporte",
    # Bet365
    "bet365": "Bet365",
    "bet 365": "Bet365",
    # Esporte da Sorte
    "esporte da sorte": "Esporte da Sorte",
    "esportes da sorte": "Esporte da Sorte",
    "esporteda sorte": "Esporte da Sorte",
    "esportedasorte": "Esporte da Sorte",
    # Aposta1
    "aposta1": "Aposta1",
    "aposta 1": "Aposta1",
    # AviaoBet
    "aviaobet": "AviaoBet",
    "aviao bet": "AviaoBet",
    "avião bet": "AviaoBet",
    # Casebre
    "casebre": "Casebre",
    "casebre vip": "Casebre",
    # Vaidebet
    "vaidebet": "Vai de bet",
    "vai de bet": "Vai de bet",
    "vdb": "Vai de bet",
    # multibet
    "Multi": "Multi",
    "multi": "Multi",
    # segurobet
    "segurobet": "segurobet",
    "seguro bet": "segurobet",
    # Betano
    "betano": "Betano",
    # OLEYBET
    "oleybet": "OLEYBET",
    "oley bet": "OLEYBET",
    # Esporte da sorte (variação)
    "esporte da sorte": "Esporte da Sorte",
    "eds": "Esporte da Sorte",
    # Betou
    "betou": "Betou",
    # Jogo de Ouro
    "jogo de ouro": "Jogo de Ouro",
    "jogodeouro": "Jogo de Ouro",
    "jdo": "Jogo de Ouro",
    # Rei do Pitaco
    "rei do pitaco": "Rei do Pitaco",
    "reidopitaco": "Rei do Pitaco",
    # Sortenabet
    "sortenabet": "Sortenabet",
    "sortena bet": "Sortenabet",
    # Esportiva
    "esportiva": "Esportiva",
    # Novibet
    "novibet": "Novibet",
    "novi bet": "Novibet",
    # Casa de Aposta
    "casa de aposta": "Casa de Aposta",
    "casadeaposta": "Casa de Aposta",
    # Aposta Ganha
    "aposta ganha": "Aposta Ganha",
    "apostaganha": "Aposta Ganha",
    # Sportingbet
    "sportingbet": "SportingBet",
    "sporting bet": "SportingBet",
    # LiderBet
    "liderbet": "LiderBet",
    "lider bet": "LiderBet",
    # DonaldBet
    "donaldbet": "DonaldBet",
    "donald bet": "DonaldBet",
    # BetssoniBet
    "betssonibet": "BetssoniBet",
    # McGamess
    "mcgamess": "McGamess",
    "mc gamess": "McGamess",
    # Betfair
    "betfair": "Betfair",
    "bet fair": "Betfair",
    # Pixbet
    "pixbet": "Pixbet",
    "pix bet": "Pixbet",
    # Stake
    "stake": "Stake",
    # KTO
    "kto": "KTO",
    # BetBoo
    "betboo": "BetBoo",
    "bet boo": "BetBoo",
    # Betcional
    "betcional": "Betcional",
    "betnacional": "Betnacional",
    "bet nacional": "Betnacional",
    # Betânia
    "betânia": "Betânia",
    # Parimatch
    "parimatch": "Parimatch",
    "pari match": "Parimatch",
    # Rivalbet
    "rivalbet": "Rivalbet",
    "rival bet": "Rivalbet",
    #versus
    "Versus": "versus",
    "versus": "versus",
    #multibet
    "Multibet": "multi",
    "multi bet": "multi",
    # 4play
    "4play": "4play",
    # 4win
    "4win": "4win",
    # 7Games
    "7games": "7Games",
    "7 games": "7Games",
    # 7K Bet
    "7k bet": "7K Bet",
    "7kbet": "7K Bet",
    # Aposta Tudo
    "aposta tudo": "Aposta Tudo",
    "apostatudo": "Aposta Tudo",
    # Apostou
    "apostou": "Apostou",
    # B2X
    "b2x": "B2X",
    # Band
    "band": "Band",
    # Bateu
    "bateu": "Bateu",
    # Bet MGM
    "bet mgm": "Bet MGM",
    "betmgm": "Bet MGM",
    # Betaki
    "betaki": "Betaki",
    # BetBoom
    "betboom": "BetBoom",
    "bet boom": "BetBoom",
    # BetBra
    "betbra": "BetBra",
    "bet bra": "BetBra",
    # Betfast
    "betfast": "Betfast",
    "bet fast": "Betfast",
    # BetPonto
    "betponto": "BetPonto",
    "bet ponto": "BetPonto",
    # Betsson
    "betsson": "Betsson",
    # Betsul
    "betsul": "Betsul",
    "bet sul": "Betsul",
    # Betvip
    "betvip": "Betvip",
    "bet vip": "Betvip",
    # Bolsa de Aposta
    "bolsa de aposta": "Bolsa de Aposta",
    "bolsadeaposta": "Bolsa de Aposta",
    # Br4
    "br4": "Br4",
    # Brasil Bet
    "brasil bet": "Brasil Bet",
    "brasilbet": "Brasil Bet",
    # Brasil da Sorte
    "brasil da sorte": "Brasil da Sorte",
    "brasildasorte": "Brasil da Sorte",
    # Bravo
    "bravo": "Bravo",
    # BrBet
    "brbet": "BrBet",
    "br bet": "BrBet",
    # Brx
    "brx": "Brx",
    # Bulls
    "bulls": "Bulls",
    # Casa de Apostas
    "casa de apostas": "Casa de Apostas",
    "casadeapostas": "Casa de Apostas",
    # Cassino
    "cassino": "Cassino",
    # CBEsporte
    "cbesporte": "CBEsporte",
    "cb esporte": "CBEsporte",
    # Donos
    "donos": "Donos",
    # Estrela
    "estrela": "Estrela",
    "estrelabet": "Estrela",
    "estrela bet": "Estrela",
    # EVip
    "evip": "EVip",
    "e vip": "EVip",
    # F12
    "f12": "F12",
    "f12bet": "F12",
    "f12 bet": "F12",
    # Falcons
    "falcons": "Falcons",
    # Faz1
    "faz1": "Faz1",
    "faz 1": "Faz1",
    # Fla / Ganhei
    "fla": "Fla / Ganhei",
    "fla ganhei": "Fla / Ganhei",
    "fla / ganhei": "Fla / Ganhei",
    "flaganhei": "Fla / Ganhei",
    # Fullt
    "fullt": "Fullt",
    # Galera
    "galera": "Galera",
    "galerabet": "Galera",
    "galera bet": "Galera",
    # Ginga
    "ginga": "Ginga",
    "gingabet": "Ginga",
    "ginga bet": "Ginga",
    # Gol de Bet
    "gol de bet": "Gol de Bet",
    "goldebet": "Gol de Bet",
    # Gorillas
    "gorillas": "Gorillas",
    # Hiper
    "hiper": "Hiper",
    "hiperbet": "Hiper",
    "hiper bet": "Hiper",
    # King Panda
    "king panda": "King Panda",
    "kingpanda": "King Panda",
    # Lance de Sorte
    "lance de sorte": "Lance de Sorte",
    "lancedesorte": "Lance de Sorte",
    # Loto
    "loto": "Loto",
    # Match
    "match": "Match",
    # Maxima
    "maxima": "Maxima",
    # Meridian
    "meridian": "Meridian",
    # Milhao
    "milhao": "Milhao",
    "milhão": "Milhao",
    # Nossa
    "nossa": "Nossa",
    "nossabet": "Nossa",
    "nossa bet": "Nossa",
    # Ona
    "ona": "Ona",
    "onabet": "Ona",
    "ona bet": "Ona",
    # Pagol
    "pagol": "Pagol",
    "Pagol": "Pagol",
    # Pinnacle
    "pinnacle": "Pinnacle",
    # R7
    "r7": "R7",
    # Seu Bet
    "seu bet": "Seu Bet",
    "seubet": "Seu Bet",
    # Superbet
    "superbet": "Superbet",
    "super bet": "Superbet",
    # Suprema
    "suprema": "Suprema",
    # Tivo
    "tivo": "Tivo",
    # Ultra
    "ultra": "Ultra",
    # Vbet
    "vbet": "Vbet",
    "v bet": "Vbet",
    # Vera
    "vera": "Vera",
    # Viva
    "viva": "Viva",
    # Warrior
    "warrior": "Warrior",
    # ZeroUm
    "zeroum": "ZeroUm",
    "zero um": "ZeroUm",
}