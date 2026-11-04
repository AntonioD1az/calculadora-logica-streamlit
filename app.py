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

st.subheader("🛠️ Constructor de Expresión")

# Variables disponibles
st.markdown("**Variables:**")
cols_vars = st.columns(6)
variables_disponibles = ['p', 'q', 'r', 's', 't', 'u']
for i, var in enumerate(variables_disponibles):
    with cols_vars[i]:
        if st.button(var, use_container_width=True):
            st.session_state.expr += var

# Operadores lógicos en español
st.markdown("**Operadores:**")
cols_ops = st.columns(6)
operadores = [
    ("∧ (Y)", "∧"),
    ("∨ (O)", "∨"),
    ("→ (IMPLICA)", "→"),
    ("↔ (EQUIV.)", "↔"),
    ("¬ (NO)", "¬"),
    ("( )", "()")
]

for i, (label, symbol) in enumerate(operadores):
    with cols_ops[i]:
        if st.button(label, use_container_width=True):
            if symbol == "()":
                st.session_state.expr += "()"
            else:
                st.session_state.expr += f" {symbol} "

# Botones de control de edición
col_c1, col_c2 = st.columns(2)
with col_c1:
    if st.button("🗑️ Limpiar Todo", type="secondary", use_container_width=True):
        st.session_state.expr = ""
with col_c2:
    if st.button("⬅️ Borrar Último", use_container_width=True):
        st.session_state.expr = st.session_state.expr.strip()[:-1]

# Mostrar expresión actual
st.markdown("**Expresión actual:**")
st.code(st.session_state.expr if st.session_state.expr else "Vacío", language="text")

# Funciones de lógica para la tabla de verdad
def normalizar_expresion(expr):
    expr = expr.replace('→', '>>').replace('↔', '==').replace('∧', '&').replace('∨', '|').replace('¬', '~')
    return expr

def extraer_variables(expr):
    return sorted(list(set(re.findall(r'\b[a-z]\b', expr))))

def generar_tabla(expr_norm, variables):
    tabla = []
    for valores in product([False, True], repeat=len(variables)):
        contexto = {v: val for v, val in zip(variables, valores)}
        try:
            resultado = int(eval(expr_norm, {"__builtins__": None}, contexto))
            fila = [int(v) for v in valores] + [resultado]
            tabla.append(fila)
        except Exception:
            return None, None
    
    columnas = variables + ["Resultado"]
    df = pd.DataFrame(tabla, columns=columnas)
    return columnas, df

# Procesamiento y generación de la tabla
if not st.session_state.expr.strip():
    st.info("Ingresa o construye una expresión para comenzar.")
else:
    expr_norm = normalizar_expresion(st.session_state.expr)
    variables = extraer_variables(expr_norm)
    
    if not variables:
        st.warning("Expresión incompleta o sin variables detectadas.")
    else:
        cols, df = generar_tabla(expr_norm, variables)
        if df is not None:
            st.success(f"¡Tabla generada para {len(variables)} variable(s)!")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Botón de descarga CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar tabla de verdad (.csv)",
                data=csv,
                file_name="tabla_verdad.csv",
                mime="text/csv",
            )
        else:
            st.error("Error al evaluar la expresión. Revisa que los operadores y paréntesis estén balanceados.")
