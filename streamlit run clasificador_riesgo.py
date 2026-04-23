import streamlit as st

st.set_page_config(page_title="Clasificador de Riesgo", layout="centered")

st.title("Clasificador de Riesgo Académico")

# -----------------------------
# ENTRADAS
# -----------------------------
papa = st.number_input("P.A.P.A.", 0.0, 5.0, step=0.1)

bolsa = st.number_input("Bolsa de créditos", 0, 100)

puntaje = st.number_input("Puntaje de admisión", 0, 1000)

avance = st.number_input("Porcentaje de avance", 0.0, 100.0)

matriculas = st.number_input("Número de matrículas", 1, 30)

traslado = st.selectbox("¿Es traslado?", ["No", "Sí"])

movilidad = st.selectbox("¿Está en movilidad?", ["No", "Sí"])

diversidad = st.selectbox("¿Tiene diversidad funcional?", ["No", "Sí"])

cred_matriculados = st.number_input("Créditos matriculados", 0, 30)

# -----------------------------
# CALCULO AVANCE / MATRICULA
# -----------------------------
ratio = avance / matriculas

st.metric("Avance / Matrícula", round(ratio, 2))

# -----------------------------
# ALERTAS
# -----------------------------
st.subheader("Alertas por criterio")

riesgos = []

# PAPA
if 3.0 <= papa <= 3.3:
    st.error("P.A.P.A.: Riesgo Alto")
    riesgos.append(3)
elif 3.3 < papa <= 4:
    st.warning("P.A.P.A.: Riesgo Medio")
    riesgos.append(2)
elif papa > 4:
    st.success("P.A.P.A.: Riesgo Bajo")
    riesgos.append(1)

# Bolsa
if bolsa <= 10:
    st.error("Bolsa de créditos: Riesgo Alto")
    riesgos.append(3)
elif bolsa <= 20:
    st.warning("Bolsa de créditos: Riesgo Medio")
    riesgos.append(2)
else:
    st.success("Bolsa de créditos: Riesgo Bajo")
    riesgos.append(1)

# Reingreso
if papa < 2.7:
    st.error("Reingreso por Consejo Superior")
    riesgos.append(3)
elif papa < 3:
    st.warning("Reingreso por Consejo de Facultad")
    riesgos.append(2)

# Puntaje
if puntaje < 450:
    st.error("Puntaje admisión: Riesgo Alto")
    riesgos.append(3)
elif puntaje <= 550:
    st.warning("Puntaje admisión: Riesgo Medio")
    riesgos.append(2)
else:
    st.success("Puntaje admisión: Riesgo Bajo")
    riesgos.append(1)

# Avance/Matrícula
if ratio < 4.16:
    st.error("Avance/Matrícula: Riesgo Alto")
    riesgos.append(3)
elif ratio < 6.25:
    st.warning("Avance/Matrícula: Riesgo Medio")
    riesgos.append(2)
else:
    st.success("Avance/Matrícula: Riesgo Bajo")
    riesgos.append(1)

# Traslado
if traslado == "Sí":
    st.warning("Traslado: Riesgo Medio")
    riesgos.append(2)

# Movilidad
if movilidad == "Sí":
    st.error("Movilidad: Riesgo Alto")
    riesgos.append(3)

# Diversidad
if diversidad == "Sí":
    st.error("Diversidad funcional: Riesgo Alto")
    riesgos.append(3)

# Créditos matriculados
if cred_matriculados > 15:
    st.error("Carga alta de créditos")
    riesgos.append(3)
elif cred_matriculados >= 10:
    st.warning("Carga media de créditos")
    riesgos.append(2)
else:
    st.success("Carga baja de créditos")
    riesgos.append(1)

# -----------------------------
# RIESGO GLOBAL
# -----------------------------
promedio_riesgo = sum(riesgos) / len(riesgos)

st.subheader("Resultado Global")

if promedio_riesgo >= 2.5:
    st.error("Riesgo Global Alto")
elif promedio_riesgo >= 1.7:
    st.warning("Riesgo Global Medio")
else:
    st.success("Riesgo Global Bajo")
