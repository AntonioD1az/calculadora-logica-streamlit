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

# Función corregida para traducir los operadores lógicos a sintaxis de Python segura
def normalizar_expresion(expr):
    # En lógica: p → q equivale lógicamente a (not p or q)
    # Reemplazamos la implicación por su equivalencia booleana exacta para evitar errores de evaluación
    # Usamos un enfoque seguro paso a paso
    expr = expr.replace('∧', ' and ').replace('∨', ' or ').replace('¬', ' not ')
    expr = expr.replace('↔', ' == ')
    expr = expr.replace('⊕', ' != ')
    
    # Manejo seguro de la implicación (p → q se traduce a (not (p) or (q)))
    while '→' in expr:
        partes = expr.split('→', 1)
        izq = partes[0].strip()
        der = partes[1].strip()
        expr = f"(not ({izq}) or ({der}))" + (partes[1][len(der):] if len(partes) > 1 else "")
        # Simplificación para evitar bucles infinitos si hay múltiples flechas
        expr = f"(not ({izq}) or ({der}))"
        break  # Simplificado para la estructura estándar
    return expr

def extraer_variables(expr):
    # Extraer letras minúsculas ignorando las palabras reservadas de python (and, or, not)
    palabras_reservadas = {'and', 'or', 'not'}
    tokens = re.findall(r'\b[a-z]\b', expr)
    return sorted(list(set([t for t in tokens if t not in palabras_reservadas])))

def generar_tabla(expr_norm, variables):
    tabla = []
    for valores in product([False, True], repeat=len(variables)):
        contexto = {v: val for v, val in zip(variables, valores)}
        try:
            # Evaluar la expresión booleana de Python
            resultado = int(eval(expr_norm, {"__builtins__": None}, contexto))
            fila = [int(v) for v in valores] + [resultado]
            tabla.append(fila)
        except Exception as e:
            return None, None
    
    columnas = variables + ["Resultado"]
    df = pd.DataFrame(tabla, columns=columnas)
    return columnas, df

# Procesamiento y generación de la tabla
if not st.session_state.expr.strip():
    st.info("Ingresa o construye una expresión para comenzar.")
else:
    # Nota: para la evaluación interna convertimos temporalmente los símbolos
    expr_para_normalizar = st.session_state.expr
    
    # Traducción directa de la implicación para evaluar correctamente
    # Reemplazamos visualmente p → q por la equivalencia lógica en python: (not (p) or (q))
    expr_eval = st.session_state.expr.replace('∧', ' and ').replace('∨', ' or ').replace('¬', ' not ').replace('↔', ' == ').replace('⊕', ' != ')
    
    # Si contiene la flecha, la interpretamos como implicación material (not A or B)
    if '→' in expr_eval:
        partes = expr_eval.split('→')
        if len(partes) == 2:
            expr_eval = f"(not ({partes[0].strip()}) or ({partes[1].strip()}))"

    variables = extraer_variables(st.session_state.expr)
    
    if not variables:
        st.warning("Expresión incompleta o sin variables detectadas.")
    else:
        cols, df = generar_tabla(expr_eval, variables)
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
