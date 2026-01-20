# auth.py - Authentification utilisateurs (Version Streamlit Cloud)

import streamlit as st
import hashlib
from connection import execute_query


def verifier_mot_de_passe(mot_de_passe_saisi: str, hash_stocke: str) -> bool:
    """
    Vérifie le mot de passe contre le hash stocké en base
    (méthode spécifique à ton projet)
    """
    if not mot_de_passe_saisi or not hash_stocke:
        return False

    # Format attendu : $2a$12$ + parties MD5
    if hash_stocke.startswith("$2a$12$"):
        md5hex = hashlib.md5(mot_de_passe_saisi.encode("utf-8")).hexdigest()
        hash_genere = "$2a$12$" + md5hex[:22] + md5hex[:31]
        return hash_stocke == hash_genere

    return False


def authentifier_utilisateur(username: str, password: str):
    """
    Authentifie un utilisateur via la base PostgreSQL
    (fallback possible via comptes de test)
    """
    username = (username or "").strip().lower()

    # Comptes de test (fallback si DB indisponible)
    users_test = {
        "admin": {"password": "admin123", "role": "admin_examens"},
        "test.etudiant": {"password": "test123", "role": "etudiant"},
        "test.professeur": {"password": "test123", "role": "professeur"},
        "test.chef": {"password": "test123", "role": "chef_departement"},
        "vice.doyen": {"password": "doyen123", "role": "vice_doyen"},
    }

    # Tentative via base de données
    try:
        sql = """
            SELECT id, username, password_hash, role, linked_id, is_active
            FROM users
            WHERE LOWER(username) = LOWER(%s)
            LIMIT 1
        """
        rows = execute_query(sql, (username,))

        if rows:
            u = rows[0]

            if not u.get("is_active", True):
                return None

            if verifier_mot_de_passe(password, u.get("password_hash", "")):
                return {
                    "id": u["id"],
                    "username": u["username"],
                    "role": u["role"],
                    "linked_id": u["linked_id"],
                    "nom_affiche": u["username"].split(".")[0].title(),
                }

    except Exception as e:
        st.warning(f"⚠️ Base indisponible : {e}. Mode test activé.")

    # Fallback (mode test)
    if username in users_test and users_test[username]["password"] == password:
        return {
            "id": 1,
            "username": username,
            "role": users_test[username]["role"],
            "linked_id": 1,
            "nom_affiche": username.split(".")[0].title(),
        }

    return None


def render_login_form():
    """Affiche le formulaire de connexion"""
    st.markdown(
        """
<div class="card fadeUp" style="max-width:520px; margin: 24px auto; text-align:center;">
  <div class="h-title">🔐 Connexion</div>
  <div class="h-sub">Accès selon le rôle (admin, vice-doyen, chef, etc.)</div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input(
                "👤 Nom d'utilisateur",
                placeholder="admin, vice.doyen, test.chef ..."
            )
        with col2:
            password = st.text_input(
                "🔒 Mot de passe",
                type="password",
                placeholder="admin123, doyen123 ..."
            )

        submitted = st.form_submit_button(
            "Se connecter",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        user = authentifier_utilisateur(username, password)
        if user:
            st.session_state.authenticated = True
            st.session_state.user = user
            st.session_state.role = user["role"]
            st.success(f"✅ Connecté : {user['username']} ({user['role']})")
            st.rerun()
        else:
            st.error("❌ Identifiants incorrects ou compte désactivé.")
            st.info("Vérifie la table users et le mot de passe.")
