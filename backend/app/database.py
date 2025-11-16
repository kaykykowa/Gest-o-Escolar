import psycopg2
from psycopg2.extras import RealDictCursor

# ⚠️ Aqui eu NÃO uso .env, é o host direto do Supabase só pra garantir
def get_conn():
    return psycopg2.connect(
        host="db.yvkglnnmklwkvabjjqqn.supabase.co",
        port=5432,
        user="postgres",
        password="352861091Kkk@",
        dbname="postgres",
        cursor_factory=RealDictCursor,
        connect_timeout=10,
    )
