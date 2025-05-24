from fastapi_pg_websocket.database import get_raw_db_connection


def test_raw_connection():
    conn = get_raw_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
    finally:
        conn.close()
