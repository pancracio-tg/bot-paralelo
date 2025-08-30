import os
import tempfile

from telegram import Update
from telegram.ext import ContextTypes

from config import GRUPO_AUTORIZADO
from database import get_duplicate, save_hash
from utils.hashing import calcular_hash


def detectar_archivo(mensaje):
    """Detecta el tipo de archivo en el mensaje y devuelve su file_id y tipo."""
    if mensaje.photo:
        return mensaje.photo[-1].file_id, "photo"
    elif mensaje.video:
        return mensaje.video.file_id, "video"
    elif mensaje.audio:
        return mensaje.audio.file_id, "audio"
    elif mensaje.voice:
        return mensaje.voice.file_id, "voice"
    return None, None


async def descargar_archivo(archivo_id, context):
    """Descarga el archivo de Telegram y devuelve la ruta temporal."""
    archivo_obj = await context.bot.get_file(archivo_id)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        ruta = tmp.name
    try:
        await archivo_obj.download_to_drive(ruta)
    except Exception as e:
        print(f"❌ Error al descargar archivo {archivo_id}: {e}")
        return None
    return ruta


async def procesar_hash(ruta, mensaje, context):
    """Calcula hash, verifica duplicados y guarda el archivo si es nuevo."""
    if not ruta:
        return  # No se pudo descargar el archivo

    hash_archivo = calcular_hash(ruta)
    os.remove(ruta)  # borrar archivo temporal

    dup_info = get_duplicate(hash_archivo, mensaje.chat_id)

    if dup_info:
        id_user_prev, username_prev, id_topic_prev, tipo_archivo_prev, fecha_prev = (
            dup_info
        )
        try:
            await context.bot.send_message(
                chat_id=mensaje.chat_id,
                message_thread_id=mensaje.message_thread_id,
                text=(
                    "❌ Este archivo ya fue enviado anteriormente, se procede a eliminarlo. "
                ),
            )
            await mensaje.delete()  # eliminar mensaje duplicado
        except Exception as e:
            print(f"⚠️ No se pudo procesar el duplicado. Error: {e}")
    else:
        save_hash(
            hash_archivo,
            mensaje.from_user.id,
            mensaje.from_user.username or mensaje.from_user.first_name,
            mensaje.message_thread_id,
            detectar_archivo(mensaje)[1],  # tipo_archivo
            mensaje.chat_id,
        )


async def manejar_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la recepción de archivos y delega la descarga y registro."""
    mensaje = update.message
    if not mensaje or mensaje.chat_id != GRUPO_AUTORIZADO:
        return

    archivo_id, tipo_archivo = detectar_archivo(mensaje)
    if not archivo_id:
        return

    ruta = await descargar_archivo(archivo_id, context)
    await procesar_hash(ruta, mensaje, context)
