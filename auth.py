import os
from pathlib import Path

import streamlit as st
from utils import authenticate_user


# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_DIR.mkdir(exist_ok=True)


def _get_logo_path():
    # Prefer assets folder, then project root
    candidates = [ASSETS_DIR / "Bioss logo.png", PROJECT_ROOT / "Bioss logo.png"]
    for p in candidates:
        if p.exists():
            return p
    return None


def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    return st.session_state.authenticated


def login_page():
    image_path = _get_logo_path()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if image_path is None:
            st.info("Logo no encontrado. Coloca 'Bioss logo.png' en 'assets/' o en la raíz del proyecto.")
        else:
            if not os.access(str(image_path), os.R_OK):
                st.error(f"No se puede leer el archivo de imagen: {image_path}. Verifica permisos.")
            else:
                st.image(str(image_path), width='stretch')

        email = st.text_input("Email", placeholder="usuario@grupoom.com", autocomplete="username")
        password = st.text_input("Password", type="password", placeholder="Ingrese su contraseña", autocomplete="current-password")

        if st.button("Ingresar"):
            if email and password:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "id": user.id,
                        "nombre": user.nombre,
                        "email": user.email,
                        "rol": user.rol.value,
                    }
                    st.success(f"Bienvenido, {user.nombre}!")
                else:
                    st.error("Email o contraseña incorrectos")
            else:
                st.warning("Por favor ingrese email y contraseña")

        st.markdown("---")
        st.info(
            """
        **Credenciales de prueba:**
        - Admin: admin@grupoom.com / admin123
        - Operador: operador@grupoom.com / operador123
        - Cliente: cliente@example.com / cliente123
        """
        )


def logout():
    st.session_state.authenticated = False
    st.session_state.user = None


def get_current_user():
    return st.session_state.get("user", None)
