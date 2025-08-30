# VolafileBot

Bot de Telegram para gestión de archivos, duplicados y estadísticas de actividad de usuarios en un grupo.

## Características

* Registro automático de usuarios que envían mensajes o se unen al grupo.
* Registro de “topics” (temas) en el chat de grupo.
* Detección de archivos duplicados mediante hash SHA-256.
* Alerta y eliminación de mensajes duplicados.
* Comandos de administración para consultar usuarios poco activos y más activos.
* Compatible con MySQL para persistencia de datos.
* Desplegable mediante Docker Compose.

## Requisitos

* Docker y Docker Compose
* Python 3.11
* MySQL 8+

## Configuración

1. Crear un archivo `.env` basado en `.env.example` con tus credenciales:

```bash
cp .env.example .env
```

2. Rellenar los valores de tu bot de Telegram y MySQL.

## Docker

Construir y levantar los servicios:

```bash
docker-compose up --build -d
```

### Servicios

* `telegram-bot` – Bot de Telegram.
* `mysql-db` – Base de datos MySQL.

## Comandos del Bot

Solo accesibles para administradores:

* `/start` – Inicia el bot.
* `/help` – Muestra la ayuda y comandos disponibles.
* `/stats` – Estadísticas generales (en desarrollo).
* `/no_activos` – Lista usuarios con menos de 6 archivos enviados.
* `/masActivo <semana|mes|año>` – Usuario más activo en ese periodo.

> Si se escribe un comando desconocido, el bot sugerirá una alternativa cercana.

## Buenas prácticas

* Mantener `.env` fuera de GitHub.
* Usar `.env.example` como referencia para nuevos desarrolladores.
* Los archivos temporales se borran tras calcular hash.
* Los mensajes duplicados se eliminan automáticamente.

## Base de datos

Tablas principales:

* `users` – Información de usuarios.
* `hashes` – Hashes de archivos enviados.
* `topics` – Temas (threads) de los mensajes.

## Licencia

Este proyecto es open-source bajo la licencia MIT.
