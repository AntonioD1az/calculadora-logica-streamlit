import streamlit as st
import re
from itertools import product
import pandas as pd

st.set_page_config(
    page_title="Calculadora Tabla de la Verdad", layout="centered"
)
st.title("🧮 Calculadora de Tabla de la Verdad")
st.write(
    "Construye tu expresión haciendo clic. El resultado se muestra en 0 y 1."
)

if "expr" not in st.session_state:
    st.session_state.expr = ""

st.subheader("🛠️ Constructor de Expresión")

variables = ["p", "q", "r", "s", "t", "w"]
st.write("Variables:")
cols_vars = st.columns(len(variables))
for i, var in enumerate(variables):
    with cols_vars[i]:
        if st.button(var, key=f"var_{var}", use_container_width=True):
            st.session_state.expr += var

operadores = [
    ("∧", " and "),
    ("∨", " or "),
    ("¬", " not "),
    ("⊕", " ^ "),
    ("→", " <= "),
    ("↔", " == "),
]
st.write("Operadores:")
cols_ops = st.columns(len(operadores))
for i, (simbolo, op) in enumerate(operadores):
    with cols_ops[i]:
        if st.button(simbolo, key=f"op_{i}", use_container_width=True):
            st.session_state.expr += op

col_clear, col_preview, col_del = st.columns(3)
with col_clear:
    if st.button(
        "🧹 Limpiar Todo", type="secondary", use_container_width=True
    ):
        st.session_state.expr = ""
with col_del:
    if st.button(
        "⌫ Borrar Último", type="secondary", use_container_width=True
    ):
        st.session_state.expr = st.session_state.expr.strip()[:-1]

st.code(st.session_state.expr or "Vacío", language="text")


def normalizar_expresion(expr):
    return expr


def extraer_variables(expr):
    return sorted(list(set(re.findall(r"\b[p-t,w]\b", expr))))


def generar_tabla(expr_str):
    vars_ = extraer_variables(expr_str)
    if not vars_:
        return None, None
    tabla = []
    for valores in product([True, False], repeat=len(vars_)):
        entorno = {v: val for v, val in zip(vars_, valores)}
        try:
            resultado = eval(expr_str, {}, entorno)
            fila = [int(v) for v in valores] + [int(resultado)]
            tabla.append(fila)
        except Exception:
            return None, None
    return vars_, tabla


if not st.session_state.expr.strip():
    st.info("Ingresa o construye una expresión arriba.")
else:
    expr_norm = normalizar_expresion(st.session_state.expr)
    vars_, tabla = generar_tabla(expr_norm)
    if not vars_:
        st.error(
            "Expresión inválida o sin variables detectadas.", icon="⚠️"
        )
    else:
        cols_df = vars_ + ["Resultado"]
        df = pd.DataFrame(tabla, columns=cols_df)
        st.success(f"¡Tabla generada para {len(vars_)} variable(s)!")
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Descargar Tabla de Verdad (.csv)",
            csv,
            "tabla_verdad.csv",
            "text/csv",
        )
