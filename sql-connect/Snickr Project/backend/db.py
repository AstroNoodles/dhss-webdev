import os
from dotenv import load_dotenv
from psycopg2 import pool

load_dotenv()

_pool = None

def init_pool(minconn=1, maxconn=5):
    global _pool
    if _pool is not None:
        return _pool

    dbname = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')

    if not (dbname and user and password):
        raise RuntimeError('Database credentials not set in environment (DB_NAME/DB_USER/DB_PASSWORD)')

    _pool = pool.ThreadedConnectionPool(minconn, maxconn,
                                        dbname=dbname,
                                        user=user,
                                        password=password,
                                        host=host,
                                        port=port)
    return _pool

def get_conn():
    if _pool is None:
        init_pool()
    return _pool.getconn()

def put_conn(conn, close=False):
    if _pool is None:
        return
    _pool.putconn(conn, close=close)

def query_one(sql, params=None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        row = cur.fetchone()
        if row is None:
            cur.close()
            return None
        cols = [desc[0] for desc in cur.description]
        result = dict(zip(cols, row))
        cur.close()
        return result
    finally:
        put_conn(conn)


def query_all(sql, params=None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        if not rows:
            cur.close()
            return []
        cols = [desc[0] for desc in cur.description]
        result = [dict(zip(cols, r)) for r in rows]
        cur.close()
        return result
    finally:
        put_conn(conn)


def execute(sql, params=None, returning=False):
    """Execute a write query and commit. If returning is True, return cursor.fetchone() as dict."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        ret = None
        if returning:
            row = cur.fetchone()
            if row and cur.description:
                cols = [desc[0] for desc in cur.description]
                ret = dict(zip(cols, row))
        conn.commit()
        cur.close()
        return ret
    finally:
        put_conn(conn)
