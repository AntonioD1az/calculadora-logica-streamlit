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

# Operadores lógicos
st.markdown("**Operadores:**")
cols_ops = st.columns(6)
operadores = [
    ("∧ (Y)", "∧"),
    ("∨ (O)", "∨"),
    ("¬ (NO)", "¬"),
    ("⊕ (XOR)", "⊕"),
    ("→ (IMPLICA)", "→"),
    ("↔ (EQUIV.)", "↔")
]

for i, (label, symbol) in enumerate(operadores):
    with cols_ops[i]:
        if st.button(label, use_container_width=True):
            st.session_state.expr += f" {symbol} "

# Fila para paréntesis y controles
cols_extras = st.columns(4)
with cols_extras[0]:
    if st.button("(", use_container_width=True):
        st.session_state.expr += "("
with cols_extras[1]:
    if st.button(")", use_container_width=True):
        st.session_state.expr += ")"
with cols_extras[2]:
    if st.button("🗑️ Limpiar Todo", type="secondary", use_container_width=True):
        st.session_state.expr = ""
with cols_extras[3]:
    if st.button("⬅️ Borrar Último", use_container_width=True):
        st.session_state.expr = st.session_state.expr.strip()[:-1]

# Mostrar expresión actual
st.markdown("**Expresión actual:**")
st.code(st.session_state.expr if st.session_state.expr else "Vacío", language="text")

# Función robusta de evaluación lógica basada en la ley de la implicación material
def evaluar_expresion_logica(expr, contexto):
    # Reemplazamos símbolos visuales por operadores booleanos exactos de Python
    expr_eval = expr.replace('∧', ' and ').replace('∨', ' or ').replace('¬', ' not ')
    expr_eval = expr_eval.replace('↔', ' == ').replace('⊕', ' != ')
    
    # Manejo correcto de la implicación (A → B equivale a not A or B)
    while '→' in expr_eval:
        partes = expr_eval.split('→', 1)
        izq = partes[0].strip()
        der = partes[1].strip()
        expr_eval = f"(not ({izq}) or ({der}))" + (partes[1][len(der):] if len(partes) > 1 else "")
        break
        
    try:
        if '→' in expr_eval:
            p_parts = expr_eval.split('→')
            expr_eval = f"(not ({p_parts[0].strip()}) or ({p_parts[1].strip()}))"
            
        return bool(eval(expr_eval, {"__builtins__": None}, contexto))
    except Exception:
        return None

def extraer_variables(expr):
    tokens = re.findall(r'\b[a-z]\b', expr)
    palabras_reservadas = {'and', 'or', 'not'}
    return sorted(list(set([t for t in tokens if t not in palabras_reservadas])))

def generar_tabla(expr_original, variables):
    tabla = []
    for valores in product([False, True], repeat=len(variables)):
        contexto = {v: val for v, val in zip(variables, valores)}
        resultado_bool = evaluar_expresion_logica(expr_original, contexto)
        if resultado_bool is None:
            return None, None
        
        fila = [int(v) for v in valores] + [int(resultado_bool)]
        tabla.append(fila)
    
    columnas = variables + ["Resultado"]
    df = pd.DataFrame(tabla, columns=columnas)
    return columnas, df

# Procesamiento y generación de la tabla
if not st.session_state.expr.strip():
    st.info("Ingresa o construye una expresión para comenzar.")
else:
    variables = extraer_variables(st.session_state.expr)
    
    if not variables:
        st.warning("Expresión incompleta o sin variables detectadas.")
    else:
        cols, df = generar_tabla(st.session_state.expr, variables)
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
