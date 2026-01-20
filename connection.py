connection.py - Connexion PostgreSQL (Streamlit Cloud compatible)
Utilise st.secrets["postgres"] pour les identifiants.
"""

import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd


class SimpleConnection:
    """Gestion simple de connexion PostgreSQL."""

    @staticmethod
    def get_connection():
        """Crée et retourne une nouvelle connexion PostgreSQL."""
        try:
            cfg = st.secrets["postgres"]
            return psycopg2.connect(
                host=cfg["host"],
                dbname=cfg["dbname"],
                user=cfg["user"],
                password=cfg["password"],
                port=int(cfg.get("port", 5432)),
                sslmode=cfg.get("sslmode", "require"),  # utile pour Neon/Supabase
            )
        except Exception as e:
            # Affiche l'erreur dans l'app Streamlit
            st.error(f"⚠️ Connexion DB impossible : {e}")
            return None


def execute_query(query: str, params=None, fetch=True):
    """Exécute une requête SQL et retourne les résultats (liste de dict) ou le nombre de lignes affectées."""
    conn = None
    cur = None

    try:
        conn = SimpleConnection.get_connection()
        if conn is None:
            return [] if fetch else 0

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params or ())

        if fetch:
            results = cur.fetchall()
            conn.commit()
            return results
        else:
            row_count = cur.rowcount
            conn.commit()
            return row_count

    except psycopg2.Error as e:
        st.error(f"⚠️ Erreur SQL : {e}")
        if conn:
            conn.rollback()
        return [] if fetch else 0

    except Exception as e:
        st.error(f"⚠️ Erreur lors de l'exécution : {e}")
        if conn:
            conn.rollback()
        return [] if fetch else 0

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def load_dataframe(query: str, params=None) -> pd.DataFrame:
    """Retourne un DataFrame pandas à partir d'une requête SQL."""
    results = execute_query(query, params=params, fetch=True)
    return pd.DataFrame(results) if results else pd.DataFrame()


# Test local seulement (pas nécessaire sur Streamlit Cloud)
if _name_ == "_main_":
    print("🔍 Test de connexion DB...")
    c = SimpleConnection.get_connection()
    if c:
        print("✅ Connexion OK")
        c.close()
    else:
        print("❌ Connexion échouée")
