import streamlit as st
from utils import authenticate_user

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    
    return st.session_state.authenticated

def login_page():
    st.title("🔐 OAPCE Multitrans")
    st.subheader("Sistema de Control y Gestión")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Iniciar Sesión")
        
        email = st.text_input("Email", placeholder="usuario@grupoom.com")
        password = st.text_input("Password", type="password", placeholder="Ingrese su contraseña")
        
        if st.button("Ingresar", use_container_width=True):
            if email and password:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "id": user.id,
                        "nombre": user.nombre,
                        "email": user.email,
                        "rol": user.rol.value
                    }
                    st.success(f"Bienvenido, {user.nombre}!")
                    st.rerun()
                else:
                    st.error("Email o contraseña incorrectos")
            else:
                st.warning("Por favor ingrese email y contraseña")
        
        st.markdown("---")
        st.info("""
        **Credenciales de prueba:**
        - Admin: admin@grupoom.com / admin123
        - Operador: operador@grupoom.com / operador123
        - Cliente: cliente@example.com / cliente123
        """)

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

def require_auth(func):
    def wrapper(*args, **kwargs):
        if not check_authentication():
            login_page()
            return None
        return func(*args, **kwargs)
    return wrapper

def get_current_user():
    return st.session_state.get("user", None)
