from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from database import get_user, save_user
from config import GRUPO_AUTORIZADO


async def auto_register_user_and_topic(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # Asegurémonos de que haya un mensaje
    mensaje = update.message
    if not mensaje:
        print("❌ No se encontró mensaje.")
        return  # No hay mensaje, salir

    # Solo se procesa si es el chat autorizado
    if mensaje.chat_id != GRUPO_AUTORIZADO:
        print(f"❌ Mensaje no proviene del chat autorizado: {mensaje.chat_id}")
        return

    # --- Registrar usuario si no existe ---
    usuario = mensaje.from_user
    if usuario:
        user_in_db = get_user(usuario.id)
        if not user_in_db:
            save_user(
                usuario.id,
                usuario.username,
                usuario.first_name,
                usuario.last_name,
                datetime.utcnow(),
            )
            print(f"👤 Usuario registrado: {usuario.id} | @{usuario.username}")
        else:
            print(f"✔️ Usuario ya existe: {usuario.id} | @{usuario.username}")
