from telegram import Update
from telegram.ext import ContextTypes
from database import save_topic, get_topic_name


async def manejar_nuevo_tema(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message
    if not mensaje or not mensaje.message_thread_id:
        return  # No hay thread_id, no se registra topic

    thread_id = mensaje.message_thread_id

    # Verificar si ya está guardado en la DB
    topic_name = get_topic_name(mensaje.chat_id, thread_id)
    if topic_name:
        return  # Ya existe, no hacer nada

    # Tomar el nombre del topic directamente del mensaje o usar ID como fallback
    topic_name = getattr(mensaje, "message_thread_name", None) or f"Tema {thread_id}"

    # Guardar en la DB
    save_topic(mensaje.chat_id, thread_id, topic_name)

    # Log esencial
    print(f"🆕 Topic registrado: {topic_name} (ID: {thread_id})")
