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
    riesgo_papa = "Crítico"
elif papa <= 3.3:
    puntaje_papa = 3
    riesgo_papa = "Alto"
elif papa <= 4.0:
    puntaje_papa = 2
    riesgo_papa = "Medio"
else:
    puntaje_papa = 1
    riesgo_papa = "Bajo"

st.write(f"Riesgo por PAPA: {riesgo_papa}")

# -----------------------------
# 2. Porcentaje de avance
# -----------------------------
st.subheader("2. Porcentaje de avance")
avance = st.slider("Seleccione el porcentaje de avance", 0, 100, 50)

if avance < 25:
    puntaje_avance = 4
    riesgo_avance = "Crítico"
elif avance < 50:
    puntaje_avance = 3
    riesgo_avance = "Alto"
elif avance < 80:
    puntaje_avance = 2
    riesgo_avance = "Medio"
else:
    puntaje_avance = 1
    riesgo_avance = "Bajo"

st.write(f"Riesgo por avance: {riesgo_avance}")

# -----------------------------
# 3. Materias perdidas / repitencia
# -----------------------------
st.subheader("3. Materias perdidas / repitencia")
materias_perdidas = st.number_input("Número de materias perdidas", min_value=0, step=1)

if materias_perdidas == 0:
    puntaje_materias = 1
    riesgo_materias = "Bajo"
elif materias_perdidas <= 2:
    puntaje_materias = 2
    riesgo_materias = "Medio"
elif materias_perdidas <= 4:
    puntaje_materias = 3
    riesgo_materias = "Alto"
else:
    puntaje_materias = 4
    riesgo_materias = "Crítico"

st.write(f"Riesgo por repitencia: {riesgo_materias}")

# -----------------------------
# 4. Condición del estudiante
# -----------------------------
st.subheader("4. Condición del estudiante")

reingreso = st.radio("¿Es estudiante de reingreso?", ["No", "Sí"])
traslado = st.radio("¿Se trasladó de programa?", ["No", "Sí"])
trabaja = st.radio("¿Actualmente trabaja?", ["No", "Sí"])

puntaje_condicion = 0

if reingreso == "Sí":
    puntaje_condicion += 2

if traslado == "Sí":
    puntaje_condicion += 1

if trabaja == "Sí":
    puntaje_condicion += 3

if puntaje_condicion == 0:
    riesgo_condicion = "Bajo"
elif puntaje_condicion <= 2:
    riesgo_condicion = "Medio"
elif puntaje_condicion <= 4:
    riesgo_condicion = "Alto"
else:
    riesgo_condicion = "Crítico"

st.write(f"Puntaje condición: {puntaje_condicion}")
st.write(f"Riesgo por condición: {riesgo_condicion}")

# -----------------------------
# 5. Alertas psicosociales / económicas / disciplinarias
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

if puntaje_alertas == 0:
    riesgo_alertas = "Bajo"
elif puntaje_alertas == 1:
    riesgo_alertas = "Medio"
elif puntaje_alertas == 2:
    riesgo_alertas = "Alto"
else:
    riesgo_alertas = "Crítico"

st.write(f"Riesgo por alertas: {riesgo_alertas}")

# -----------------------------
# Cálculo final ponderado
# -----------------------------
st.subheader("Resultado Final")

riesgo_total = (
    puntaje_papa * 0.35 +
    puntaje_avance * 0.20 +
    puntaje_materias * 0.20 +
    puntaje_condicion * 0.10 +
    puntaje_alertas * 0.15
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
