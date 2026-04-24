import streamlit as st

st.set_page_config(page_title="Simulador de Riesgo Estudiantil", layout="centered")

st.title("📊 Simulador de Riesgo Estudiantil")
st.write("Este simulador clasifica el nivel de riesgo académico de un estudiante.")

# -----------------------------
# 1. PAPA
# -----------------------------
st.subheader("1. Promedio Académico (PAPA)")
papa = st.number_input("Ingrese el PAPA", min_value=0.0, max_value=5.0, step=0.1)

if papa < 3.0:
    puntaje_papa = 4
elif papa <= 3.3:
    puntaje_papa = 3
elif papa <= 4.0:
    puntaje_papa = 2
else:
    puntaje_papa = 1

# -----------------------------
# 2. Porcentaje de avance
# -----------------------------
st.subheader("2. Porcentaje de avance")
avance = st.slider("Seleccione el porcentaje de avance", 0, 100, 50)

if avance < 25:
    puntaje_avance = 4
elif avance < 50:
    puntaje_avance = 3
elif avance < 80:
    puntaje_avance = 2
else:
    puntaje_avance = 1

# -----------------------------
# 3. Materias perdidas / repitencia
# -----------------------------
st.subheader("3. Materias perdidas / repitencia")
materias_perdidas = st.number_input("Número de materias perdidas", min_value=0, step=1)

if materias_perdidas == 0:
    puntaje_materias = 1
elif materias_perdidas <= 2:
    puntaje_materias = 2
elif materias_perdidas <= 4:
    puntaje_materias = 3
else:
    puntaje_materias = 4

# -----------------------------
# 4. Condición del estudiante
# -----------------------------
st.subheader("4. Condición del estudiante")

preguntas = [
    "¿Es estudiante de reingreso?",
    "¿Se trasladó de programa?",
    "¿Actualmente trabaja?"
]

respuestas = {}

for pregunta in preguntas:
    col1, col2 = st.columns([4, 2])

    with col1:
        st.write(pregunta)

    with col2:
        respuestas[pregunta] = st.radio(
            "",
            ["No", "Sí"],
            horizontal=True,
            key=pregunta
        )

puntaje_condicion = 0

if respuestas["¿Es estudiante de reingreso?"] == "Sí":
    puntaje_condicion += 2

if respuestas["¿Se trasladó de programa?"] == "Sí":
    puntaje_condicion += 1

if respuestas["¿Actualmente trabaja?"] == "Sí":
    puntaje_condicion += 3

# -----------------------------
# 5. Alertas adicionales
# -----------------------------
st.subheader("5. Alertas adicionales")

salud_mental = st.checkbox("Problemas de salud mental")
economico = st.checkbox("Problemas económicos")
convivencia = st.checkbox("Problemas de convivencia / disciplina")
familiar = st.checkbox("Problemas familiares")

puntaje_alertas = 0

if salud_mental:
    puntaje_alertas += 1
if economico:
    puntaje_alertas += 1
if convivencia:
    puntaje_alertas += 1
if familiar:
    puntaje_alertas += 1

# -----------------------------
# NORMALIZACIÓN
# -----------------------------
condicion_norm = (puntaje_condicion / 6) * 4
alertas_norm = (puntaje_alertas / 4) * 4

# -----------------------------
# Cálculo final ponderado
# -----------------------------
st.subheader("Resultado Final")

riesgo_total = (
    puntaje_papa * 0.35 +
    puntaje_avance * 0.20 +
    puntaje_materias * 0.20 +
    condicion_norm * 0.10 +
    alertas_norm * 0.15
)

if riesgo_total <= 1.9:
    clasificacion = "🟢 Bajo"
elif riesgo_total <= 2.4:
    clasificacion = "🟡 Medio"
elif riesgo_total <= 3.2:
    clasificacion = "🟠 Alto"
else:
    clasificacion = "🔴 Crítico"

st.metric("Puntaje Total", round(riesgo_total, 2))
st.success(f"Clasificación del riesgo: {clasificacion}")

# -----------------------------
# SUGERENCIAS GLOBALES
# -----------------------------
st.subheader("Sugerencias Globales")

if clasificacion == "🔴 Crítico":
    st.error(
        "Se recomienda intervención inmediata, revisión de carga académica y acompañamiento psicosocial."
    )
elif clasificacion == "🟠 Alto":
    st.warning(
        "Se recomienda seguimiento académico prioritario, tutorías y orientación personalizada."
    )
elif clasificacion == "🟡 Medio":
    st.info(
        "Se recomienda monitoreo preventivo y fortalecimiento de hábitos de estudio."
    )
else:
    st.success(
        "Condición académica estable. Mantener estrategias actuales."
    )
