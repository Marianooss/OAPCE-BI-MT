import streamlit as st
import sys
sys.path.append('.')
from page_forms import show_data_forms

st.set_page_config(page_title="Gestión de Datos", layout="wide")

# Llama a la función que construye la página de Gestión de Datos
show_data_forms()
