from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from config import GRUPO_AUTORIZADO
from database import get_user, save_user


async def manejar_nuevo_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Registra usuarios que se unan al grupo.
    """
    mensaje = update.message
    if not mensaje or mensaje.chat_id != GRUPO_AUTORIZADO:
        return

    if not mensaje.new_chat_members:
        return

    for usuario in mensaje.new_chat_members:
        save_user(
            usuario.id,
            usuario.username,
            usuario.first_name,
            usuario.last_name,
            datetime.utcnow().isoformat(),  # fecha de registro
        )
        # Solo log de información relevante
        print(f"👤 Nuevo usuario guardado: {usuario.id} | @{usuario.username}")


async def registrar_usuario_si_no_existe(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Registra usuarios que ya estaban en el grupo cuando escriben un mensaje por primera vez.
    """
    mensaje = update.message
    if not mensaje or mensaje.chat_id != GRUPO_AUTORIZADO:
        return

    usuario = mensaje.from_user
    if not get_user(usuario.id):
        save_user(
            usuario.id,
            usuario.username,
            usuario.first_name,
            usuario.last_name,
            datetime.utcnow().isoformat(),
        )
        # Solo log de información relevante
        print(
            f"👤 Usuario registrado automáticamente: {usuario.id} | @{usuario.username}"
        )
