import difflib
from telegram import Update
from telegram.ext import ContextTypes
from database import usuarios_no_activos, usuario_mas_activo

# -------------------------
# Funciones de ayuda
# -------------------------


def sugerir_periodo(periodo: str) -> str | None:
    """Sugiere un periodo válido cercano a la entrada del usuario."""
    opciones = ["semana", "mes", "año"]
    coincidencias = difflib.get_close_matches(periodo, opciones, n=1, cutoff=0.6)
    return coincidencias[0] if coincidencias else None


def sugerir_comando(comando: str) -> str | None:
    """Sugiere un comando válido cercano al escrito por el usuario."""
    comandos = ["/start", "/help", "/stats", "/no_activos", "/masActivo"]
    coincidencias = difflib.get_close_matches(comando, comandos, n=1, cutoff=0.5)
    return coincidencias[0] if coincidencias else None


# -------------------------
# Verificación de administrador
# -------------------------


async def es_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Comprueba si el usuario es administrador o creador del chat."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        miembro = await context.bot.get_chat_member(chat_id, user_id)
        return miembro.status in ("administrator", "creator")
    except Exception:
        return False


async def puede_usarlo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Verifica permisos y notifica al usuario si no es admin."""
    if not await es_admin(update, context):
        await update.message.reply_text(
            "❌ Solo los administradores pueden usar este comando."
        )
        return False
    return True


# -------------------------
# Comandos
# -------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await puede_usarlo(update, context):
        return
    await update.message.reply_text(
        "👋 ¡Hola! Bot listo para gestionar archivos y usuarios."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await puede_usarlo(update, context):
        return
    await update.message.reply_text(
        "📖 Comandos disponibles:\n"
        "/start - Iniciar el bot\n"
        "/help - Mostrar este mensaje\n"
        "/stats - Ver estadísticas (opcional)\n"
        "/no_activos - Lista de usuarios con menos de 6 archivos\n"
        "/masActivo <semana|mes|año> - Usuario más activo en ese periodo"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await puede_usarlo(update, context):
        return
    await update.message.reply_text("📊 Estadísticas no implementadas todavía.")


async def no_activos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await puede_usarlo(update, context):
        return

    usuarios = usuarios_no_activos(min_archivos=6)
    if not usuarios:
        await update.message.reply_text(
            "✅ Todos los usuarios han enviado 6 o más archivos."
        )
        return

    mensaje = "⚠️ Usuarios poco activos (menos de 6 archivos enviados):\n\n"
    for id_user, username, first_name, last_name, total_archivos in usuarios:
        mensaje += f"👤 {first_name} {last_name or ''} (@{username or 'N/A'}) - {total_archivos} archivos\n"

    await update.message.reply_text(mensaje)


async def usuarios_mas_activos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await puede_usarlo(update, context):
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Debes indicar un periodo: semana, mes o año.\nEjemplo: /masActivo semana"
        )
        return

    periodo = context.args[0].lower()
    if periodo not in ["semana", "mes", "año"]:
        sugerencia = sugerir_periodo(periodo)
        mensaje = f"❌ Periodo inválido: '{periodo}'. Debe ser: semana, mes o año."
        if sugerencia:
            mensaje += f"\n💡 Quizá quisiste decir: '{sugerencia}'"
        await update.message.reply_text(mensaje)
        return

    usuario = usuario_mas_activo(periodo)
    if not usuario:
        await update.message.reply_text(
            f"⚠️ No se encontró ningún usuario activo en el último {periodo}."
        )
        return

    id_user, username, first_name, last_name, total_archivos = usuario
    mensaje = (
        f"🏆 Usuario más activo en el último {periodo}:\n\n"
        f"👤 {first_name} {last_name or ''} (@{username or 'N/A'}) - {total_archivos} archivos\n"
        "Felicidades y gracias por tu apoyo! 🎉"
    )
    await update.message.reply_text(mensaje)


# -------------------------
# Handler para comandos desconocidos
# -------------------------


async def comando_desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await puede_usarlo(update, context):
        return

    texto = update.message.text
    sugerencia = sugerir_comando(texto)
    mensaje = f"❌ Comando no reconocido: {texto}"
    if sugerencia:
        mensaje += f"\n💡 Quizá quisiste decir: {sugerencia}"
    await update.message.reply_text(mensaje)
