"""
connection.py - Connexion PostgreSQL CORRIGÉE
Version finale testée et fonctionnelle
"""
import psycopg2
import psycopg2.extras
import pandas as pd
import streamlit as st

class SimpleConnection:
    """Classe pour gérer la connexion à PostgreSQL"""
    
    mport streamlit as st
import psycopg2

conn = psycopg2.connect(
    host=st.secrets["postgres"]["host"],
    dbname=st.secrets["postgres"]["dbname"],
    user=st.secrets["postgres"]["user"],
    password=st.secrets["postgres"]["password"],
    port=st.secrets["postgres"]["port"]
)


def execute_query(query: str, params=None, fetch=True):
    """Exécute une requête SQL et retourne les résultats"""
    conn = None
    cursor = None
    try:
        conn = SimpleConnection.get_connection()
        if not conn:
            return [] if fetch else 0
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, params or ())
        
        if fetch:
            results = cursor.fetchall()
            conn.commit()
            return results
        else:
            row_count = cursor.rowcount
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def load_dataframe(query: str, params=None):
    """Retourne un DataFrame pandas à partir d'une requête"""
    results = execute_query(query, params, fetch=True)
    if results:
        return pd.DataFrame(results)
    return pd.DataFrame()

# Test de connexion au lancement
if __name__ == "__main__":
    print("🔍 Test de connexion à la base de données...")
    conn = SimpleConnection.get_connection()
    if conn:
        print("✅ Connexion réussie à exam_platform !")
        test_results = execute_query("SELECT COUNT(*) AS nb FROM etudiants")
        if test_results:
            print(f"   → Nombre d'étudiants : {test_results[0]['nb']}")
        conn.close()
    else:

        print("❌ La connexion a échoué.")
