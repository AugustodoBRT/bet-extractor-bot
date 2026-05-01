import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

import config
from ocr import extrair_texto
from processar_apostas import processar_aposta

# ===============================
# CONFIG DOS BOTS
# ===============================
BOTS = [
    {"token": os.getenv("TOKEN_FUTEBOL", ""), "esporte": "Futebol"},
    {"token": os.getenv("TOKEN_NBA", ""), "esporte": "NBA"},
    {"token": os.getenv("TOKEN_NHL", ""), "esporte": "NHL"},
    {"token": os.getenv("TOKEN_OUTROS", ""), "esporte": "Outros"},
]

os.makedirs(config.PASTA_IMAGENS, exist_ok=True)

# ===============================
# HANDLER DINÂMICO
# ===============================
ALBUM_BUFFER = {}
ALBUM_TASKS = {}

def criar_handler(nome_esporte):
    async def processer_mensagens(updates, context):
        try:
            import re
            partes = []
            tipsters_encontrados = []
            
            # 1. Extrair informações de texto, caption e tipster de todas as mensagens
            for update in updates:
                msg = update.message
                tipster = ""
                
                if msg.forward_origin:
                    origem = msg.forward_origin
                    nome_bruto = ""
                    if origem.type == "user":
                        nome_bruto = origem.sender_user.full_name
                    elif origem.type == "hidden_user":
                        nome_bruto = origem.sender_user_name
                    elif origem.type in ["chat", "channel"]:
                        nome_bruto = origem.chat.title
                        assinatura = getattr(origem, 'author_signature', None)
                        if assinatura:
                            nome_bruto = f"{nome_bruto} ({assinatura})"
                        
                    if nome_bruto and "(" in nome_bruto and ")" in nome_bruto:
                        match = re.search(r'\(([^)]+)\)', nome_bruto)
                        if match:
                            tipster = match.group(1).strip()
                        else:
                            tipster = nome_bruto
                    elif nome_bruto:
                        tipster = nome_bruto
                        
                elif getattr(msg, 'forward_from_chat', None):
                    nome_bruto = msg.forward_from_chat.title
                    if nome_bruto and "(" in nome_bruto and ")" in nome_bruto:
                        match = re.search(r'\(([^)]+)\)', nome_bruto)
                        if match:
                            tipster = match.group(1).strip()
                        else:
                            tipster = nome_bruto
                    else:
                        tipster = nome_bruto
                elif getattr(msg, 'forward_from', None):
                    tipster = msg.forward_from.full_name
                elif getattr(msg, 'forward_sender_name', None):
                    tipster = msg.forward_sender_name

                # Normalizar nome do tipster
                if tipster:
                    t_lower = tipster.lower()
                    if "meckler" in t_lower or "lucas meckler" in t_lower:
                        tipster = "Meckler"
                    elif "emanuel" in t_lower or "oliveira" in t_lower:
                        tipster = "Emanuel"
                
                if tipster and tipster not in tipsters_encontrados:
                    tipsters_encontrados.append(tipster)

                # caption da mensagem original
                if msg.caption:
                    partes.append(msg.caption.strip())

                # texto (caso não tenha foto)
                if msg.text:
                    partes.append(msg.text.strip())

            # 2. Extrair imagens sequencialmente (espera as tarefas)
            for update in updates:
                if update.message.photo:
                    await update.message.reply_text("⏳ Lendo imagem...")
                    
                    foto_alta_resolucao = update.message.photo[-1]
                    try:
                        file = await foto_alta_resolucao.get_file()
                        caminho = f"{config.PASTA_IMAGENS}/{file.file_id}.jpg"
                        await file.download_to_drive(caminho)
                        
                        ocr = extrair_texto(caminho)
                        if ocr:
                            partes.append(f"[IMAGEM]:\n{ocr}")
                            print("✅ OCR da imagem concluído")
                    except Exception as e:
                        print(f"⚠️ Erro ao processar imagem: {e}")

            if not partes:
                await updates[0].message.reply_text("⚠️ Sem texto.")
                return

            texto_final = "\n\n-----\n\n".join(partes)
            tipster_final = tipsters_encontrados[0] if tipsters_encontrados else ""

            print("\n" + "="*50)
            print(f"📩 [{nome_esporte}] TEXTO FINAL COMBINADO:\n")
            print(texto_final)
            print("="*50 + "\n")

            processar_aposta(texto_final, nome_esporte, tipster_final)

            await updates[0].message.reply_text(f"✅ Aposta(s) de {nome_esporte} processada(s)!")

        except Exception as e:
            print(f"❌ Erro ({nome_esporte}):", e)
            await updates[0].message.reply_text("❌ Erro interno.")

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Agrupamento por media_group_id (Albums do Telegram)
        media_group_id = update.message.media_group_id
        if media_group_id:
            if media_group_id not in ALBUM_BUFFER:
                ALBUM_BUFFER[media_group_id] = []
            ALBUM_BUFFER[media_group_id].append(update)

            if media_group_id not in ALBUM_TASKS:
                async def process_album():
                    await asyncio.sleep(4.0) # Espera 4 segundos para coletar todas do album
                    updates_to_process = ALBUM_BUFFER.pop(media_group_id, [])
                    ALBUM_TASKS.pop(media_group_id, None)
                    if updates_to_process:
                        await processer_mensagens(updates_to_process, context)
                
                ALBUM_TASKS[media_group_id] = asyncio.create_task(process_album())
            return
            
        # Mensagens normais sem album
        await processer_mensagens([update], context)

    return handle_message

# ===============================
# MAIN MULTI-BOT
# ===============================
async def main():
    apps = []

    for bot in BOTS:
        if not bot["token"]:
            print(f"⚠️ Token não configurado para {bot['esporte']}. Verifique o arquivo .env!")
            continue

        app = ApplicationBuilder().token(bot["token"]).build()

        handler = criar_handler(bot["esporte"])
        app.add_handler(MessageHandler(filters.ALL, handler))

        apps.append(app)

    if not apps:
        print("❌ Nenhum bot inicializado. Configure os tokens no arquivo .env!")
        return

    print("🚀 Todos os bots rodando...")

    # inicia todos
    await asyncio.gather(*(app.initialize() for app in apps))
    await asyncio.gather(*(app.start() for app in apps))
    await asyncio.gather(*(app.updater.start_polling() for app in apps))

    # mantém rodando
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())