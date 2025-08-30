import os
from datetime import datetime, timedelta
import mysql.connector

# -------------------------
# Configuración de MySQL
# -------------------------
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql-db")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "telegram_bot")


# -------------------------
# Conexión a MySQL con reintentos
# -------------------------
def get_connection():
    import time

    while True:
        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Esperando MySQL... ({err})")
            time.sleep(3)


conn = get_connection()
c = conn.cursor(dictionary=True)

# -------------------------
# Creación de tablas si no existen
# -------------------------
TABLES = {
    "hashes": (
        "CREATE TABLE IF NOT EXISTS hashes ("
        "hash VARCHAR(255),"
        "id_user BIGINT,"
        "username VARCHAR(255),"
        "id_topic BIGINT,"
        "tipo VARCHAR(50),"
        "id_chat BIGINT,"
        "fecha_creacion DATETIME,"
        "PRIMARY KEY (hash, id_chat)"
        ") ENGINE=InnoDB"
    ),
    "topics": (
        "CREATE TABLE IF NOT EXISTS topics ("
        "id_chat BIGINT,"
        "thread_id BIGINT,"
        "name VARCHAR(255),"
        "PRIMARY KEY (id_chat, thread_id)"
        ") ENGINE=InnoDB"
    ),
    "users": (
        "CREATE TABLE IF NOT EXISTS users ("
        "id_user BIGINT PRIMARY KEY,"
        "username VARCHAR(255),"
        "first_name VARCHAR(255),"
        "last_name VARCHAR(255),"
        "fecha_registro DATETIME"
        ") ENGINE=InnoDB"
    ),
}

for table_sql in TABLES.values():
    c.execute(table_sql)

conn.commit()

# -------------------------
# Funciones de acceso a la base de datos
# -------------------------


# Topics
def save_topic(id_chat, thread_id, name):
    """Inserta o reemplaza un topic en la DB."""
    c.execute(
        "REPLACE INTO topics (id_chat, thread_id, name) VALUES (%s,%s,%s)",
        (id_chat, thread_id, name),
    )
    conn.commit()


def get_topic_name(id_chat, thread_id):
    """Obtiene el nombre de un topic por su chat y thread_id."""
    c.execute(
        "SELECT name FROM topics WHERE id_chat=%s AND thread_id=%s",
        (id_chat, thread_id),
    )
    row = c.fetchone()
    return row["name"] if row else None


# Hashes
def check_duplicate(hash_archivo, id_chat):
    """Verifica si un hash ya existe en la DB."""
    c.execute(
        "SELECT hash FROM hashes WHERE hash=%s AND id_chat=%s", (hash_archivo, id_chat)
    )
    return c.fetchone() is not None


def get_duplicate(hash_archivo, id_chat):
    """Obtiene información completa de un hash duplicado."""
    c.execute(
        "SELECT id_user, username, id_topic, tipo, fecha_creacion "
        "FROM hashes WHERE hash=%s AND id_chat=%s",
        (hash_archivo, id_chat),
    )
    return c.fetchone()


def save_hash(
    hash_archivo, id_user, username, id_topic, tipo, id_chat, fecha_creacion=None
):
    """Guarda un nuevo hash en la DB."""
    if fecha_creacion is None:
        fecha_creacion = datetime.utcnow()
    c.execute(
        "INSERT INTO hashes (hash,id_user,username,id_topic,tipo,id_chat,fecha_creacion) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (hash_archivo, id_user, username, id_topic, tipo, id_chat, fecha_creacion),
    )
    conn.commit()


# Users
def save_user(id_user, username, first_name, last_name, fecha_registro=None):
    """Inserta o reemplaza un usuario en la DB."""
    if fecha_registro is None:
        fecha_registro = datetime.utcnow()
    c.execute(
        "REPLACE INTO users (id_user,username,first_name,last_name,fecha_registro) "
        "VALUES (%s,%s,%s,%s,%s)",
        (id_user, username, first_name, last_name, fecha_registro),
    )
    conn.commit()


def get_user(id_user):
    """Obtiene información de un usuario por su ID."""
    c.execute(
        "SELECT id_user,username,first_name,last_name FROM users WHERE id_user=%s",
        (id_user,),
    )
    return c.fetchone()


def usuarios_no_activos(min_archivos=6):
    """Lista usuarios con menos de 'min_archivos' enviados."""
    c.execute(
        "SELECT u.id_user,u.username,u.first_name,u.last_name,COUNT(h.hash) AS total_archivos "
        "FROM users u LEFT JOIN hashes h ON u.id_user=h.id_user "
        "GROUP BY u.id_user HAVING total_archivos < %s",
        (min_archivos,),
    )
    return c.fetchall()


def usuario_mas_activo(periodo: str):
    """Devuelve el usuario más activo en el periodo indicado (semana, mes, año)."""
    ahora = datetime.utcnow()
    if periodo == "semana":
        limite = ahora - timedelta(days=7)
    elif periodo == "mes":
        limite = ahora - timedelta(days=30)
    elif periodo == "año":
        limite = ahora - timedelta(days=365)
    else:
        limite = datetime.min

    c.execute(
        "SELECT u.id_user,u.username,u.first_name,u.last_name,COUNT(h.hash) AS total_archivos "
        "FROM users u JOIN hashes h ON u.id_user=h.id_user "
        "WHERE h.fecha_creacion >= %s "
        "GROUP BY u.id_user ORDER BY total_archivos DESC LIMIT 1",
        (limite,),
    )
    return c.fetchone()
