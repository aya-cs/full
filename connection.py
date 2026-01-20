"""
connection.py - Connexion PostgreSQL (Streamlit Cloud compatible)
Utilise st.secrets["postgres"] pour les identifiants.
"""

import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd


class SimpleConnection:
    @staticmethod
    def get_connection():
        try:
            cfg = st.secrets["postgres"]
            return psycopg2.connect(
                host=cfg["host"],
                dbname=cfg["dbname"],
                user=cfg["user"],
                password=cfg["password"],
                port=int(cfg.get("port", 5432)),
                sslmode=cfg.get("sslmode", "require"),
            )
        except Exception as e:
            st.error(f"⚠️ Connexion DB impossible : {e}")
            return None


def execute_query(query: str, params=None, fetch=True):
    conn = None
    cur = None
    try:
        conn = SimpleConnection.get_connection()
        if conn is None:
            return [] if fetch else 0

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params or ())

        if fetch:
            rows = cur.fetchall()
            conn.commit()
            return rows
        else:
            count = cur.rowcount
            conn.commit()
            return count

    except psycopg2.Error as e:
        st.error(f"⚠️ Erreur SQL : {e}")
        if conn:
            conn.rollback()
        return [] if fetch else 0

    except Exception as e:
        st.error(f"⚠️ Erreur : {e}")
        if conn:
            conn.rollback()
        return [] if fetch else 0

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def load_dataframe(query: str, params=None) -> pd.DataFrame:
    rows = execute_query(query, params=params, fetch=True)
    return pd.DataFrame(rows) if rows else pd.DataFrame()
