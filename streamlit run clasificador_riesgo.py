import streamlit as st

# -----------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------
st.set_page_config(page_title="Clasificador de Riesgo Académico", layout="centered")

# -----------------------------------
# TÍTULO
# -----------------------------------
st.markdown("""
<h1 style='text-align: center;'>Clasificador de Riesgo Académico</h1>
<p style='text-align: center; font-size:18px;'>
Modelo de clasificación basado en criterios institucionales
</p>
""", unsafe_allow_html=True)

# -----------------------------------
# VARIABLES DE ENTRADA
# -----------------------------------
st.subheader("Caracterización del Estudiante")

semestre = st.number_input("Semestre actual", min_value=1, max_value=20)

reingreso = st.selectbox("¿Es estudiante de reingreso?", ["No", "Sí"])

papa = st.number_input("P.A.P.A.", min_value=0.0, max_value=5.0, step=0.1)

avance = st.number_input("Porcentaje de avance (%)", min_value=0, max_value=100)

matriculas = st.number_input("Número de matrículas acumuladas", min_value=1, max_value=50)

traslado = st.selectbox("¿Es traslado de programa?", ["No", "Sí"])

# -----------------------------------
# PUNTAJE DE ADMISIÓN
# -----------------------------------
st.subheader("Puntaje de Admisión")

puntaje = st.number_input("Puntaje de admisión", min_value=0, max_value=1000)

# -----------------------------------
# CARGA ACADÉMICA Y CONTEXTO
# -----------------------------------
st.subheader("Carga Académica y Contexto")

creditos_semestre = st.number_input("Número de créditos matriculados este semestre", min_value=1, max_value=30)

trabaja = st.selectbox("¿Actualmente trabaja?", ["No", "Sí"])

cuida = st.selectbox("¿Tiene responsabilidades de cuidado?", ["No", "Sí"])

horas_academicas = creditos_semestre * 3

st.metric("Horas académicas estimadas por semana", horas_academicas)

# -----------------------------------
# CLASIFICACIÓN POR PERFIL
# -----------------------------------
riesgo_perfil = "Bajo"

if semestre <= 2:
    riesgo_perfil = "Alto"

elif reingreso == "Sí":
    riesgo_perfil = "Alto"

elif 3.0 <= papa <= 3.3:
    riesgo_perfil = "Alto"

elif avance >= 90:
    riesgo_perfil = "Medio"

elif matriculas > 13 and avance < 50:
    riesgo_perfil = "Medio"

elif traslado == "Sí":
    riesgo_perfil = "Medio"

elif papa > 4.0:
    riesgo_perfil = "Bajo"

# -----------------------------------
# CLASIFICACIÓN POR PUNTAJE
# -----------------------------------
if puntaje >= 650:
    riesgo_puntaje = "Muy bajo"
elif puntaje >= 550:
    riesgo_puntaje = "Bajo"
elif puntaje >= 450:
    riesgo_puntaje = "Medio"
elif puntaje >= 350:
    riesgo_puntaje = "Alto"
else:
    riesgo_puntaje = "Crítico"

# -----------------------------------
# CONSOLIDACIÓN DEL RIESGO
# -----------------------------------
niveles = {
    "Muy bajo": 1,
    "Bajo": 2,
    "Medio": 3,
    "Alto": 4,
    "Crítico": 5
}

map_perfil = {
    "Bajo": 2,
    "Medio": 3,
    "Alto": 4
}

valor_final = max(map_perfil[riesgo_perfil], niveles[riesgo_puntaje])

riesgo_final = [k for k, v in niveles.items() if v == valor_final][0]

# -----------------------------------
# AJUSTE POR SOBRECARGA
# -----------------------------------
if trabaja == "Sí" and horas_academicas >= 50:
    riesgo_final = "Alto"

if cuida == "Sí" and horas_academicas >= 50:
    riesgo_final = "Alto"

# -----------------------------------
# RESULTADOS
# -----------------------------------
st.subheader("Resultado de Clasificación")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Riesgo por Perfil", riesgo_perfil)

with col2:
    st.metric("Riesgo por Puntaje", riesgo_puntaje)

with col3:
    st.metric("Riesgo Consolidado", riesgo_final)

# -----------------------------------
# ALERTAS POR CARGA
# -----------------------------------
st.subheader("Alertas de Sobrecarga")

if trabaja == "Sí" and horas_academicas >= 50:
    st.warning("La carga académica y laboral podría afectar descanso y rendimiento.")

if cuida == "Sí" and horas_academicas >= 50:
    st.warning("La carga académica y de cuidado podría generar sobrecarga.")

if horas_academicas >= 60:
    st.error("La carga académica semanal estimada es muy alta.")

# -----------------------------------
# INTERPRETACIÓN
# -----------------------------------
st.subheader("Interpretación")

if riesgo_final in ["Crítico", "Alto"]:
    st.error("Se recomienda intervención prioritaria y acompañamiento intensivo.")

elif riesgo_final == "Medio":
    st.warning("Seguimiento periódico sugerido para evitar deterioro académico.")

else:
    st.success("Condiciones académicas estables.")

# -----------------------------------
# EXPLICACIÓN
# -----------------------------------
st.markdown("""
<hr>
<div style='text-align:center;'>

<b>Clasificación por Perfil:</b><br>
Evalúa características académicas y administrativas.<br><br>

<b>Clasificación por Puntaje:</b><br>
Evalúa el riesgo con base en antecedentes de ingreso.<br><br>

<b>Carga Académica:</b><br>
Cada crédito equivale a 3 horas de trabajo semanal.<br><br>

<b>Riesgo Consolidado:</b><br>
Se toma el criterio más restrictivo para priorizar acompañamiento.

</div>
""", unsafe_allow_html=True)
