# Extrator de Apostas

Bot do Telegram para extração de apostas e envio para o Google Sheets.

## Configuração

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Crie um arquivo `.env` baseado no `.env.example` e preencha suas chaves:
   ```bash
   cp .env.example .env
   ```

3. Adicione suas credenciais do Google Sheets no arquivo `credenciais.json` (você pode usar o `credenciais_TEMPLATE.json` como base).

4. Execute os bots:
   ```bash
   python multi_bot.py
   ```
