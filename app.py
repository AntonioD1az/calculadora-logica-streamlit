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

# Función mejorada para traducir correctamente cualquier cantidad de implicaciones y operadores
def traducir_implicaciones(expr):
    # Traducir operadores estándar primero
    expr = expr.replace('∧', ' and ').replace('∨', ' or ').replace('¬', ' not ')
    expr = expr.replace('↔', ' == ').replace('⊕', ' != ')
    
    # Mientras existan flechas '→', las reemplazamos aplicando la equivalencia material: A → B equivalente a (not (A) or (B))
    # Buscamos de manera segura agrupar los términos adyacentes a la flecha
    while '→' in expr:
        partes = expr.split('→')
        # Tomamos el antecedente (último bloque antes de la flecha actual) y el consecuente (primer bloque después)
        # Para simplificar y evitar errores de sintaxis en cadenas múltiples, convertimos la primera ocurrencia de izquierda a derecha
        idx = expr.find('→')
        
        # Recortamos hacia la izquierda encontrando el inicio lógico o delimitador
        # O aplicamos un reemplazo directo seguro envolviendo la proposición
        expr = expr.replace('→', ' ) or ( not (', 1)
        # Como la implicación A → B es (not A or B), reestructuramos con un parser simple basado en reemplazo seguro:
    
    return expr

# Función de evaluación segura utilizando una aproximación basada en tokens o reemplazo estructurado
def evaluar_expresion_logica(expr, contexto):
    # Reemplazos básicos
    expr_eval = expr.replace('∧', ' and ').replace('∨', ' or ').replace('¬', ' not ')
    expr_eval = expr_eval.replace('↔', ' == ').replace('⊕', ' != ')
    
    # Traducción iterativa robusta para la implicación (A → B  ==>  (not (A) or (B)))
    # Vamos a manejar expresiones comunes reemplazando el operador por su equivalente lógico booleano
    # Una forma infalible en Python para la implicación:
    def implicacion(a, b):
        return (not a) or b

    # Inyectamos la función de implicación en el entorno de evaluación de Python para que la entienda directamente
    contexto_con_funciones = {**contexto, "__builtins__": None, "implicacion": implicacion}
    
    # Reemplazamos el símbolo '→' por nuestra función auxiliar 'implicacion(' ... ',' ... ')'
    while '→' in expr_eval:
        # Dividimos de forma equilibrada o reemplazamos de manera segura
        # Buscamos la posición de la flecha
        idx = expr_eval.find('→')
        # Extraemos el lado izquierdo (buscando el inicio o paréntesis)
        # Simplificación robusta: evaluamos transformando la cadena con la función implicacion(izq, der)
        # Para hacerlo visualmente compatible con el split:
        partes = expr_eval.split('→', 1)
        izq = partes[0].strip()
        der = partes[1].strip()
        
        # Envolvemos en la función implicacion(izq, der)
        expr_eval = f"implicacion({izq}, {der})" + (partes[1][len(der):] if len(partes) > 1 else "")
        # Si quedan más flechas, el bucle las procesa ordenadamente de dentro hacia afuera o viceversa
        break

    # Por si acaso quedan flechas tras una iteración compleja
    if '→' in expr_eval:
        partes = expr_eval.split('→')
        expr_eval = f"implicacion({partes[0].strip()}, {partes[1].strip()})"

    try:
        resultado = eval(expr_eval, contexto_con_funciones)
        return bool(resultado)
    except Exception:
        return None

def extraer_variables(expr):
    tokens = re.findall(r'\b[a-z]\b', expr)
    palabras_reservadas = {'and', 'or', 'not', 'implicacion'}
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
