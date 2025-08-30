from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from database import get_user, save_user, get_topic_name, save_topic
from config import GRUPO_AUTORIZADO


async def auto_register_user_and_topic(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    mensaje = update.message
    if not mensaje:
        return  # No hay mensaje, salir

    # Solo se procesa si es el chat autorizado
    if mensaje.chat_id != GRUPO_AUTORIZADO:
        return

    # --- Registrar usuario si no existe ---
    usuario = mensaje.from_user
    if usuario and not get_user(usuario.id):
        save_user(
            usuario.id,
            usuario.username,
            usuario.first_name,
            usuario.last_name,
            datetime.utcnow(),
        )
        # Log esencial
        print(f"👤 Usuario registrado: {usuario.id} | @{usuario.username}")

    # --- Registrar topic si no existe ---
    thread_id = getattr(mensaje, "message_thread_id", None)
    if thread_id:
        topic_name = get_topic_name(mensaje.chat_id, thread_id)
        if not topic_name:
            # Intentamos obtener el nombre real del topic desde Telegram
            try:
                topic_info = await context.bot.get_forum_topic(
                    chat_id=mensaje.chat_id, message_thread_id=thread_id
                )
                topic_name = topic_info.name if topic_info else f"Tema {thread_id}"
            except Exception:
                topic_name = f"Tema {thread_id}"

            save_topic(mensaje.chat_id, thread_id, topic_name)
            # Log esencial
            print(f"🆕 Topic registrado: {topic_name} (ID: {thread_id})")
