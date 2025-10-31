import streamlit as st
import sys
sys.path.append('.')
from page_comercial import show_commercial_dashboard

st.set_page_config(page_title="Comercial", layout="wide")

# Llama a la función que construye el dashboard Comercial
show_commercial_dashboard()
