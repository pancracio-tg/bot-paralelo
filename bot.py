from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TOKEN
from handlers import (
    commands_handler,
    forum_handler,
    media_handler,
    user_handler,
)
from handlers.auto_register_user_and_topic import (
    auto_register_user_and_topic,
)  # Asegúrate de que la importación esté correcta

app = ApplicationBuilder().token(TOKEN).build()

# -------------------------
# Handler global de auto-registro (usuarios + topics)
# Se ejecuta antes que cualquier otro handler
# group=0 asegura la prioridad
# -------------------------
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, auto_register_user_and_topic),
    group=0,
)

# -------------------------
# Handlers de media
# Captura fotos, videos, audios y mensajes de voz
# -------------------------
filtro_media = filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE
app.add_handler(MessageHandler(filtro_media, media_handler.manejar_media), group=1)

# -------------------------
# Handler para nuevos usuarios que se unen al grupo
# -------------------------
app.add_handler(
    MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, user_handler.manejar_nuevo_usuario
    )
)

# -------------------------
# Comandos del bot
# -------------------------
app.add_handler(CommandHandler("start", commands_handler.start))
app.add_handler(CommandHandler("help", commands_handler.help_command))
app.add_handler(CommandHandler("stats", commands_handler.stats))
app.add_handler(CommandHandler("noActivos", commands_handler.no_activos))
app.add_handler(CommandHandler("masActivo", commands_handler.usuarios_mas_activos))

# Handler para comandos desconocidos
app.add_handler(MessageHandler(filters.COMMAND, commands_handler.comando_desconocido))

# -------------------------
# Handler de creación de topics/foros
# -------------------------
app.add_handler(
    MessageHandler(
        filters.StatusUpdate.FORUM_TOPIC_CREATED, forum_handler.manejar_nuevo_tema
    )
)

# -------------------------
# Iniciar bot
# -------------------------
print("🤖 VolafileBot iniciado...")
app.run_polling()
print("🤖 VolafileBot detenido.")
