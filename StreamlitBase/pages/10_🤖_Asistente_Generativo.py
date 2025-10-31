import streamlit as st

st.set_page_config(page_title="Asistente Generativo", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F0F15; color: #E0E0FF; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Asistente de Datos Generativo (GDA)")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Pregúntame sobre ventas, clientes o métricas."}
    ]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        if "ventas" in msg["content"].lower():
            st.line_chart([10, 20, 30, 25, 40])

prompt = st.chat_input("Ej: ¿Ventas por región en Q3?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = f"He analizado tus datos. Las ventas en Q3 fueron: Norte $500K, Sur $300K. ¿Quieres ver el gráfico?"
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
    st.bar_chart({"Norte": 500, "Sur": 300})
