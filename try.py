import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("PG_HOST", "127.0.0.1").strip()
port = int(os.getenv("PG_PORT", "5432").strip())
user = os.getenv("PG_USER", "postgres").strip()
db   = os.getenv("PG_DB", "try").strip()
pwd  = (os.getenv("PG_PASSWORD") or "").strip()

print("HOST:", repr(host))
print("PORT:", port)
print("USER:", repr(user))
print("DB:", repr(db))
print("PWD length:", len(pwd))   # NO mostramos la contraseña, solo la longitud

try:
    conn = psycopg.connect(host=host, port=port, user=user, password=pwd, dbname=db)
    with conn.cursor() as cur:
        cur.execute("SELECT current_user, inet_server_addr(), inet_server_port();")
        print("✓ Conexión OK:", cur.fetchone())
    conn.close()
except Exception as e:
    print("❌ Falló conexión directa:", e)
