import streamlit as st
import sys
sys.path.append('.')
from page_finanzas import show_finance_dashboard

st.set_page_config(page_title="Finanzas", layout="wide")

# Llama a la función que construye el dashboard de Finanzas
show_finance_dashboard()
