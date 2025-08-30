import os

TOKEN = os.getenv("TOKEN")
GRUPO_AUTORIZADO = int(os.getenv("GRUPO_AUTORIZADO", "-1003046379594"))

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql-db")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "botuser")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "botpass")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "botdb")
