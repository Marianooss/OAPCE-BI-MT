import streamlit as st
import sys
sys.path.append('.')
from page_direccion import show_management_dashboard

st.set_page_config(page_title="Dirección General", layout="wide")

# Llama a la función que construye el dashboard de Dirección
show_management_dashboard()
