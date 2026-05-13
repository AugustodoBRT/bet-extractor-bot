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
# Agora usa apenas um bot para o grupo.
TOKEN = os.getenv("TOKEN_GERAL") or os.getenv("TOKEN_FUTEBOL")
if not TOKEN:
    print("❌ Token não configurado. Defina TOKEN_GERAL no arquivo .env!")
    exit(1)

os.makedirs(config.PASTA_IMAGENS, exist_ok=True)

# ===============================
# HANDLER DINÂMICO
# ===============================
ALBUM_BUFFER = {}
ALBUM_TASKS = {}

def get_msg(update):
    return update.message or update.edited_message or getattr(update, 'channel_post', None) or getattr(update, 'edited_channel_post', None)

def criar_handler(nome_esporte):
    async def processer_mensagens(updates, context):
        try:
            import re
            partes = []
            tipsters_encontrados = []
            message_ids = []
            
            # 1. Extrair informações de texto, caption e tipster de todas as mensagens
            for update in updates:
                msg = get_msg(update)
                if not msg:
                    continue
                    
                message_ids.append(msg.message_id)
                # O tipster agora é o remetente da mensagem no grupo ou assinatura do canal
                if getattr(msg, 'author_signature', None):
                    tipster = msg.author_signature
                elif msg.from_user:
                    tipster = msg.from_user.full_name
                elif getattr(msg, 'sender_chat', None):
                    tipster = msg.sender_chat.title
                else:
                    tipster = ""
                    
                # Simplificação de nomes
                if tipster:
                    if "Emanuel Oliv" in tipster or "Emanuel Oliveira" in tipster:
                        tipster = "Emanuel"
                    elif "Lucas Meckler" in tipster:
                        tipster = "Meckler"
                
                if tipster and tipster not in tipsters_encontrados:
                    tipsters_encontrados.append(tipster)

                # caption da mensagem original
                if msg.caption:
                    partes.append(msg.caption.strip())

                # texto (caso não tenha foto)
                if msg.text:
                    partes.append(msg.text.strip())
            
            # Filtro Estrito: Verifica se tem a estrutura de aposta no texto
            texto_completo = "\n".join(partes).lower()
            if not ("@" in texto_completo or "odd" in texto_completo):
                return # Ignora silenciosamente se não tiver o símbolo da odd



            # Filtro Estrito: Verifica se tem foto (aposta sempre tem OCR da tip)
            tem_foto = any(get_msg(m).photo for m in updates if get_msg(m))
            if not tem_foto:
                return # Ignora silenciosamente
                
            # 2. Extrair imagens sequencialmente (espera as tarefas)
            for update in updates:
                msg = get_msg(update)
                if msg and msg.photo:
                    # await msg.reply_text("⏳ Lendo imagem...")
                    
                    foto_alta_resolucao = msg.photo[-1]
                    try:
                        file = await foto_alta_resolucao.get_file()
                        caminho = f"{config.PASTA_IMAGENS}/{file.file_id}.jpg"
                        await file.download_to_drive(caminho)
                        
                        ocr = extrair_texto(caminho)
                        if ocr:
                            partes.append(f"[IMAGEM]:\n{ocr}")
                            print("✅ OCR da imagem concluído")
                            
                        # Apaga a imagem logo após o OCR para não lotar o disco
                        if os.path.exists(caminho):
                            os.remove(caminho)
                            
                    except Exception as e:
                        print(f"⚠️ Erro ao processar imagem: {e}")

            if not partes:
                primeiro_msg = get_msg(updates[0])
                # if primeiro_msg:
                #     await primeiro_msg.reply_text("⚠️ Sem texto.")
                return

            texto_final = "\n\n-----\n\n".join(partes)
            tipster_final = tipsters_encontrados[0] if tipsters_encontrados else ""

            print("\n" + "="*50)
            print(f"📩 TEXTO FINAL COMBINADO:\n")
            print(texto_final)
            print("="*50 + "\n")

            primary_message_id = message_ids[0] if message_ids else None
            # Passamos esporte=None porque ele será extraído pela IA
            processar_aposta(texto_final, None, tipster_final, primary_message_id)

            # primeiro_msg = updates[0].message or updates[0].edited_message
            # if primeiro_msg:
            #     await primeiro_msg.reply_text(f"✅ Aposta processada!")

        except Exception as e:
            print(f"❌ Erro:", e)
            # primeiro_msg = updates[0].message or updates[0].edited_message
            # if primeiro_msg:
            #     await primeiro_msg.reply_text("❌ Erro interno.")

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Agrupamento por media_group_id (Albums do Telegram)
        msg = get_msg(update)
        if not msg:
            return
            
        media_group_id = msg.media_group_id
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
        await asyncio.sleep(2.0) # Dar uma descansada entre as mensagens normais

    return handle_message

# ===============================
# MAIN
# ===============================
async def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(60)
        .pool_timeout(60)
        .build()
    )

    handler = criar_handler("Geral")
    app.add_handler(MessageHandler(filters.ALL & ~filters.UpdateType.EDITED_MESSAGE, handler))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handler))

    print("🚀 Bot rodando no modo grupo estrito...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # mantém rodando
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())