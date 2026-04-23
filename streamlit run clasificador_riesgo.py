import streamlit as st

# -----------------------------------
# CONFIGURACIÓN
# -----------------------------------
st.set_page_config(page_title="Clasificador de Riesgo Académico", layout="centered")

st.markdown("""
<h1 style='text-align: center;'>Clasificador de Riesgo Académico</h1>
<p style='text-align: center;'>Sistema de alerta temprana y recomendaciones académicas</p>
""", unsafe_allow_html=True)

# -----------------------------------
# ENTRADAS
# -----------------------------------
st.subheader("Información del Estudiante")

papa = st.number_input("P.A.P.A.", min_value=0.0, max_value=5.0, step=0.1)

bolsa = st.number_input("Bolsa de créditos", min_value=0, max_value=100)

puntaje = st.number_input("Puntaje de admisión", min_value=0, max_value=1000)

avance = st.number_input("Porcentaje de avance", min_value=0.0, max_value=100.0)

matriculas = st.number_input("Número de matrículas", min_value=1, max_value=27)

traslado = st.selectbox("¿Es traslado de programa?", ["No", "Sí"])

movilidad = st.selectbox("¿Está en movilidad académica?", ["No", "Sí"])

diversidad = st.selectbox("¿Tiene diversidad funcional?", ["No", "Sí"])

cred_matriculados = st.number_input("Créditos matriculados", min_value=0, max_value=30)

trabaja = st.selectbox("¿Actualmente trabaja?", ["No", "Sí"])

# -----------------------------------
# CÁLCULOS
# -----------------------------------
ratio = avance / matriculas if matriculas > 0 else 0

st.metric("Avance / Matrícula", round(ratio, 2))

horas_academicas = cred_matriculados * 3
st.metric("Horas académicas estimadas/semana", horas_academicas)

# -----------------------------------
# ALERTAS
# -----------------------------------
st.subheader("Alertas por criterio")

riesgos = []
recomendaciones = []

# PAPA
if 3.0 <= papa <= 3.3:
    st.error("P.A.P.A.: Riesgo Alto")
    riesgos.append(3)
    recomendaciones.append("Fortalecer hábitos de estudio y priorizar asignaturas con mayor número de créditos.")
elif 3.3 < papa <= 4:
    st.warning("P.A.P.A.: Riesgo Medio")
    riesgos.append(2)
    recomendaciones.append("Mantener seguimiento académico para evitar descenso del promedio.")
elif papa > 4:
    st.success("P.A.P.A.: Riesgo Bajo")
    riesgos.append(1)

# Bolsa de créditos
if bolsa <= 10:
    st.error("Bolsa de créditos: Riesgo Alto")
    riesgos.append(3)
    recomendaciones.append("Revisar proyección curricular y solicitar orientación para optimizar matrícula.")
elif bolsa <= 20:
    st.warning("Bolsa de créditos: Riesgo Medio")
    riesgos.append(2)
    recomendaciones.append("Monitorear uso de créditos disponibles.")
else:
    st.success("Bolsa de créditos: Riesgo Bajo")
    riesgos.append(1)

# Reingreso
if papa < 2.7:
    st.error("Debe hacer reingreso por Consejo Superior Universitario.")
    riesgos.append(3)
    recomendaciones.append("Iniciar trámite de reingreso por Consejo Superior Universitario.")
elif papa < 3:
    st.warning("Debe hacer reingreso por Consejo de Facultad.")
    riesgos.append(2)
    recomendaciones.append("Iniciar trámite de reingreso por Consejo de Facultad.")

# Puntaje admisión
if puntaje < 450:
    st.error("Puntaje de admisión: Riesgo Alto")
    riesgos.append(3)
    recomendaciones.append("Asignar acompañamiento intensivo y tutorías académicas.")
elif puntaje <= 550:
    st.warning("Puntaje de admisión: Riesgo Medio")
    riesgos.append(2)
    recomendaciones.append("Seguimiento preventivo.")
else:
    st.success("Puntaje de admisión: Riesgo Bajo")
    riesgos.append(1)

# Avance / Matrícula
if ratio < 4.16:
    st.error("Avance/Matrícula: Riesgo Alto")
    riesgos.append(3)
    recomendaciones.append("Evaluar causas de rezago y diseñar plan de nivelación.")
elif ratio < 6.25:
    st.warning("Avance/Matrícula: Riesgo Medio")
    riesgos.append(2)
    recomendaciones.append("Monitorear progreso curricular.")
else:
    st.success("Avance/Matrícula: Riesgo Bajo")
    riesgos.append(1)

# Traslado
if traslado == "Sí":
    st.warning("Traslado de programa: Riesgo Medio")
    riesgos.append(2)
    recomendaciones.append("Brindar orientación curricular para adaptación.")
else:
    riesgos.append(1)

# Movilidad
if movilidad == "Sí":
    st.error("Movilidad académica: Riesgo Alto")
    riesgos.append(3)
    recomendaciones.append("Realizar seguimiento por adaptación académica y administrativa.")
else:
    riesgos.append(1)

# Diversidad funcional
if diversidad == "Sí":
    st.error("Diversidad funcional: Requiere acompañamiento prioritario")
    riesgos.append(3)
    recomendaciones.append("Activar rutas de apoyo y ajustes razonables.")
else:
    riesgos.append(1)

# Créditos matriculados ajustado por trabajo
if trabaja == "Sí":
    if cred_matriculados > 12:
        st.error("Carga alta de créditos para estudiante que trabaja")
        riesgos.append(3)
        recomendaciones.append("Reducir carga académica o reorganizar tiempos por compatibilidad con jornada laboral.")
    elif cred_matriculados >= 8:
        st.warning("Carga media de créditos para estudiante que trabaja")
        riesgos.append(2)
        recomendaciones.append("Monitorear equilibrio entre trabajo y estudio.")
    else:
        st.success("Carga manejable para estudiante que trabaja")
        riesgos.append(1)
else:
    if cred_matriculados > 15:
        st.error("Carga alta de créditos")
        riesgos.append(3)
        recomendaciones.append("Revisar carga académica para evitar sobrecarga.")
    elif cred_matriculados >= 10:
        st.warning("Carga media de créditos")
        riesgos.append(2)
        recomendaciones.append("Mantener equilibrio entre carga y rendimiento.")
    else:
        st.success("Carga baja de créditos")
        riesgos.append(1)

# -----------------------------------
# RESULTADO GLOBAL
# -----------------------------------
promedio_riesgo = sum(riesgos) / len(riesgos)

st.subheader("Resultado Global")

if promedio_riesgo >= 2.5:
    st.error("Riesgo Global Alto")
    riesgo_global = "Alto"
elif promedio_riesgo >= 1.7:
    st.warning("Riesgo Global Medio")
    riesgo_global = "Medio"
else:
    st.success("Riesgo Global Bajo")
    riesgo_global = "Bajo"

# -----------------------------------
# RECOMENDACIONES ESPECÍFICAS
# -----------------------------------
st.subheader("Recomendaciones Específicas")

for r in set(recomendaciones):
    st.write(f"• {r}")

# -----------------------------------
# RECOMENDACIÓN GLOBAL
# -----------------------------------
st.subheader("Recomendación Global")

if riesgo_global == "Alto":
    st.error("Se recomienda intervención prioritaria, seguimiento continuo y articulación con bienestar universitario.")
elif riesgo_global == "Medio":
    st.warning("Se recomienda seguimiento periódico y acompañamiento preventivo.")
else:
    st.success("Se recomienda mantener estrategias actuales y monitoreo básico.")

# -----------------------------------
# PIE DE PÁGINA
# -----------------------------------
st.markdown("""
<hr>
<div style='text-align:center;'>
Sistema de clasificación académica.
</div>
""", unsafe_allow_html=True)
