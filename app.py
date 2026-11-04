import streamlit as st
import re
from itertools import product
import pandas as pd

st.set_page_config(
    page_title="Calculadora de Tabla de la Verdad",
    layout="centered"
)

st.title("Calculadora de Tabla de la Verdad")
st.markdown("Construye tu expresión haciendo clic. El resultado se muestra en 0 y 1.")

# Inicializar estado para la expresión
if 'expr' not in st.session_state:
    st.session_state.expr = ""

# Componentes y lógica de la aplicación...