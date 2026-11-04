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

# Funciones auxiliares de normalización y lógica
def normalizar_expresion(expr):
    # Reemplazos básicos para operadores lógicos
    expr = expr.replace('→', '>>').replace('↔', '==').replace('∧', '&').replace('∨', '|').replace('¬', '~')
    return expr

def extraer_variables(expr):
    # Extraer variables únicas (letras minúsculas) ordenadas alfabéticamente
    vars_encontradas = sorted(list(set(re.findall(r'\b[a-z]\b', expr))))
    return vars_encontradas

def generar_tabla(expr_norm, variables):
    tabla = []
    for valores in product([False, True], repeat=len(variables)):
        contexto = {v: val for v, val in zip(variables, valores)}
        try:
            # Evaluar la expresión lógica
            resultado = int(eval(expr_norm, {"__builtins__": None}, contexto))
            fila = [int(v) for v in valores] + [resultado]
            tabla.append(fila)
        except Exception:
            return None, None
    
    columnas = variables + ["Resultado"]
    df = pd.DataFrame(tabla, columns=columnas)
    return columnas, df

# Entrada de texto para la expresión
st.session_state.expr = st.text_input("Expresión lógica:", value=st.session_state.expr)

if not st.session_state.expr.strip():
    st.info("Ingresa o construye una expresión para comenzar.")
else:
    expr_norm = normalizar_expresion(st.session_state.expr)
    variables = extraer_variables(expr_norm)
    
    if not variables:
        st.warning("Expresión inválida o sin variables detectadas.")
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
            st.error("Error al evaluar la expresión. Revisa los operadores.")
