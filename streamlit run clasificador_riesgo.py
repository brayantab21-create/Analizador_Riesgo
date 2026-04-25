import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ─── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard de Riesgo Estudiantil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Estilos personalizados ───────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #1e2d40; }
    [data-testid="stSidebar"] * { color: #e8edf3 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { color: #a8bbd0 !important; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.1rem 1.4rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
        border-left: 4px solid #3b82f6;
    }
    .metric-card.verde { border-left-color: #22c55e; }
    .metric-card.amarillo { border-left-color: #f59e0b; }
    .metric-card.naranja { border-left-color: #f97316; }
    .metric-card.rojo { border-left-color: #ef4444; }
    .metric-val { font-size: 2rem; font-weight: 700; color: #1e2d40; line-height: 1.1; }
    .metric-lbl { font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }
    .section-title { font-size: 0.75rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin: 1.5rem 0 0.6rem; }
    .badge-bajo { background:#dcfce7; color:#166534; border-radius:6px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
    .badge-medio { background:#fef9c3; color:#854d0e; border-radius:6px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
    .badge-alto  { background:#ffedd5; color:#9a3412; border-radius:6px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
    .badge-critico { background:#fee2e2; color:#991b1b; border-radius:6px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
    .upload-area { background: white; border-radius: 16px; padding: 3rem 2rem; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.07); }
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    .stPlotlyChart { border-radius: 12px; overflow: hidden; background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.07); }
</style>
""", unsafe_allow_html=True)

# ─── Columnas de riesgo del archivo ──────────────────────────────────────────
RISK_FLAGS = {
    "1 y 2 semestre": "1°/2° semestre",
    "Reingreso":      "Reingreso",
    "P.A.P.A":        "PAPA bajo",
    "Traslado":       "Traslado",
    "PAPA +4":        "PAPA ≥ 4",
    "Admisión":       "Admisión especial",
    4:                "Alerta col.4",
    5:                "Alerta col.5",
}

COLOR_RIESGO = {
    "Bajo":    "#22c55e",
    "Medio":   "#f59e0b",
    "Alto":    "#f97316",
    "Crítico": "#ef4444",
}

# ─── Función: calcular nivel de riesgo ───────────────────────────────────────
def calcular_riesgo(row):
    papa  = row.get("PAPA", np.nan)
    avance = row.get("AVANCE", np.nan)
    matriculas = row.get("MATRICULAS", 1) or 1

    # PAPA
    if pd.isna(papa):
        p_papa = 2           # sin dato → riesgo medio
    elif papa < 3.0:
        p_papa = 4
    elif papa <= 3.3:
        p_papa = 3
    elif papa <= 4.0:
        p_papa = 2
    else:
        p_papa = 1

    # Avance
    if pd.isna(avance):
        p_avance = 2
    elif matriculas > 13 and avance < 50:
        p_avance = 4
    elif avance < 25:
        p_avance = 4
    elif avance < 50:
        p_avance = 3
    elif avance < 80:
        p_avance = 2
    else:
        p_avance = 1

    # Flags de riesgo → puntaje extra
    n_flags = sum(
        1 for col in RISK_FLAGS
        if str(row.get(col, "")).strip().upper() == "SI"
    )
    # Excluir "PAPA +4" como factor negativo de riesgo
    papa4_ok = str(row.get("PAPA +4", "")).strip().upper() == "SI"
    if papa4_ok:
        n_flags = max(0, n_flags - 1)

    flags_norm = (n_flags / 5) * 4

    total = p_papa * 0.45 + p_avance * 0.30 + flags_norm * 0.25

    if total <= 1.8:
        return "Bajo",    round(total, 2)
    elif total <= 2.4:
        return "Medio",   round(total, 2)
    elif total <= 3.2:
        return "Alto",    round(total, 2)
    else:
        return "Crítico", round(total, 2)


# ─── Función: cargar y procesar datos ────────────────────────────────────────
@st.cache_data(show_spinner=False)
def procesar(raw_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(BytesIO(raw_bytes))

    # Renombrar columnas numéricas para que sobrevivan al procesamiento
    df = df.rename(columns={4: "alerta_4", 5: "alerta_5"})

    # Calcular riesgo
    df[["NIVEL_RIESGO", "PUNTAJE_RIESGO"]] = df.apply(
        lambda r: pd.Series(calcular_riesgo(r)), axis=1
    )

    # Conteo de flags activos
    flag_cols_renamed = {
        "1 y 2 semestre": "1 y 2 semestre",
        "Reingreso": "Reingreso",
        "P.A.P.A": "P.A.P.A",
        "Traslado": "Traslado",
        "PAPA +4": "PAPA +4",
        "Admisión": "Admisión",
        "alerta_4": "alerta_4",
        "alerta_5": "alerta_5",
    }
    def contar_flags(row):
        return sum(
            1 for c in flag_cols_renamed
            if str(row.get(c, "")).strip().upper() == "SI"
        )
    df["N_FLAGS"] = df.apply(contar_flags, axis=1)

    # PAPA limpio
    df["PAPA_DISP"] = df["PAPA"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")

    return df


# ─── Sidebar: carga de archivo ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📂 Cargar datos")
    st.markdown(
        "<small style='color:#7a9bbf'>Los datos <b>no se guardan</b> en ningún servidor. "
        "Al actualizar la página todo se borra.</small>",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Subir archivo Excel (.xlsx)",
        type=["xlsx"],
        help="Solo se procesa en memoria. No se almacena nada.",
    )
    st.divider()

    if uploaded:
        st.markdown("### 🔍 Filtros")

# ─── Estado de sesión (volátil, no persistente) ───────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None

if uploaded is not None:
    raw = uploaded.read()
    st.session_state.df = procesar(raw)

df = st.session_state.df

# ─── Sin datos: pantalla de bienvenida ───────────────────────────────────────
if df is None:
    st.markdown("""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:70vh;'>
      <div style='font-size:4rem;'>📊</div>
      <h1 style='color:#1e2d40;font-weight:700;margin:0.5rem 0;'>Dashboard de Riesgo Estudiantil</h1>
      <p style='color:#64748b;font-size:1.1rem;max-width:520px;text-align:center;'>
        Sube un archivo Excel con el formato estándar de análisis de riesgo usando el panel izquierdo.
        Los datos se procesan <b>solo en memoria</b> y desaparecen al actualizar la página.
      </p>
      <div style='margin-top:1.5rem;background:#f1f5f9;border-radius:10px;padding:1rem 2rem;font-size:0.85rem;color:#475569;'>
        🔒 &nbsp;<b>Privacidad garantizada</b> — cero persistencia de datos
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Filtros laterales (en cascada) ──────────────────────────────────────────
with st.sidebar:
    # 1. Facultad
    facultades = sorted(df["FACULTAD"].dropna().unique())
    sel_fac = st.multiselect("Facultad", facultades, default=facultades)

    # 2. Departamento — solo los que pertenecen a las facultades seleccionadas
    df_fac = df[df["FACULTAD"].isin(sel_fac)]
    departamentos = sorted(df_fac["DEPARTAMENTO"].dropna().unique())
    sel_dep = st.multiselect("Departamento", departamentos, default=departamentos)

    # 3. Programa — solo los que pertenecen a los departamentos seleccionados
    df_dep = df_fac[df_fac["DEPARTAMENTO"].isin(sel_dep)]
    programas = sorted(df_dep["PROGRAMA_CURRICULAR"].dropna().unique())
    sel_prog = st.multiselect("Programa curricular", programas, default=programas)

    st.divider()

    niveles = ["Bajo", "Medio", "Alto", "Crítico"]
    sel_nivel = st.multiselect("Nivel de riesgo", niveles, default=niveles)

    profesionales = sorted(df["PROFESIONAL REPORTE"].dropna().unique())
    sel_prof = st.multiselect("Profesional de reporte", profesionales, default=profesionales)

    st.divider()
    st.markdown(
        "<small style='color:#7a9bbf;font-size:0.7rem'>"
        "🔒 Datos solo en sesión. Al recargar la página se eliminan automáticamente."
        "</small>",
        unsafe_allow_html=True,
    )

# ─── Aplicar filtros ──────────────────────────────────────────────────────────
dff = df[
    df["FACULTAD"].isin(sel_fac) &
    df["DEPARTAMENTO"].isin(sel_dep) &
    df["PROGRAMA_CURRICULAR"].isin(sel_prog) &
    df["NIVEL_RIESGO"].isin(sel_nivel) &
    df["PROFESIONAL REPORTE"].isin(sel_prof)
].copy()

# ─── Encabezado ───────────────────────────────────────────────────────────────
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("## 📊 Dashboard de Riesgo Estudiantil")
    st.caption(f"Periodo: **{df['PERIODO'].iloc[0]}** · Sede: **{df['SEDE'].iloc[0]}** · Mostrando **{len(dff):,}** de **{len(df):,}** estudiantes")
with c2:
    periodo = df["PERIODO"].iloc[0]
    st.markdown(f"""
    <div style='background:#1e2d40;border-radius:10px;padding:0.8rem 1.2rem;text-align:center;'>
      <div style='color:#7a9bbf;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'>Periodo activo</div>
      <div style='color:white;font-size:1.2rem;font-weight:700;'>{periodo}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ─── Métricas de resumen ──────────────────────────────────────────────────────
conteos = dff["NIVEL_RIESGO"].value_counts()
total = len(dff)

col_t, col_b, col_m, col_a, col_c = st.columns(5)

def metric_card(col, valor, label, clase=""):
    col.markdown(
        f"""<div class="metric-card {clase}">
              <div class="metric-val">{valor}</div>
              <div class="metric-lbl">{label}</div>
            </div>""",
        unsafe_allow_html=True,
    )

metric_card(col_t, total, "Total estudiantes")
metric_card(col_b, conteos.get("Bajo",    0), "Riesgo bajo",    "verde")
metric_card(col_m, conteos.get("Medio",   0), "Riesgo medio",   "amarillo")
metric_card(col_a, conteos.get("Alto",    0), "Riesgo alto",    "naranja")
metric_card(col_c, conteos.get("Crítico", 0), "Riesgo crítico", "rojo")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Fila de gráficas principales ────────────────────────────────────────────
g1, g2, g3 = st.columns([1.2, 1.4, 1.4])

with g1:
    st.markdown('<p class="section-title">Distribución de riesgo</p>', unsafe_allow_html=True)
    dist_df = (
        dff["NIVEL_RIESGO"]
        .value_counts()
        .reindex(["Bajo", "Medio", "Alto", "Crítico"], fill_value=0)
        .reset_index()
    )
    dist_df.columns = ["Nivel", "Estudiantes"]
    fig_pie = px.pie(
        dist_df,
        names="Nivel",
        values="Estudiantes",
        color="Nivel",
        color_discrete_map=COLOR_RIESGO,
        hole=0.52,
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        textfont_size=12,
        marker=dict(line=dict(color="white", width=2)),
    )
    fig_pie.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=270,
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

with g2:
    st.markdown('<p class="section-title">Distribución PAPA</p>', unsafe_allow_html=True)
    papa_data = dff["PAPA"].dropna()
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=papa_data,
        nbinsx=20,
        marker_color="#3b82f6",
        opacity=0.85,
        name="PAPA",
    ))
    for val, color, label in [(3.0, "#ef4444", "< 3.0"), (4.0, "#f59e0b", "= 4.0")]:
        fig_hist.add_vline(x=val, line_dash="dash", line_color=color, line_width=1.5,
                           annotation_text=label, annotation_position="top right",
                           annotation_font_size=10)
    fig_hist.update_layout(
        margin=dict(t=10, b=30, l=10, r=10),
        height=270,
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        xaxis_title="PAPA",
        yaxis_title="Estudiantes",
        font=dict(size=11),
        bargap=0.05,
    )
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

with g3:
    st.markdown('<p class="section-title">Avance académico (%)</p>', unsafe_allow_html=True)
    bins = [0, 25, 50, 80, 100]
    labels = ["0–25%", "25–50%", "50–80%", "80–100%"]
    dff["RANGO_AVANCE"] = pd.cut(dff["AVANCE"], bins=bins, labels=labels, right=True)
    avance_df = dff["RANGO_AVANCE"].value_counts().reindex(labels, fill_value=0).reset_index()
    avance_df.columns = ["Rango", "Estudiantes"]
    colores_avance = ["#ef4444", "#f97316", "#f59e0b", "#22c55e"]
    fig_bar = px.bar(
        avance_df,
        x="Rango",
        y="Estudiantes",
        color="Rango",
        color_discrete_sequence=colores_avance,
        text="Estudiantes",
    )
    fig_bar.update_traces(textposition="outside", textfont_size=11, marker_line_width=0)
    fig_bar.update_layout(
        showlegend=False,
        margin=dict(t=10, b=30, l=10, r=10),
        height=270,
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        xaxis_title=None,
        yaxis_title="Estudiantes",
        font=dict(size=11),
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

# ─── Fila secundaria ─────────────────────────────────────────────────────────
g4, g5 = st.columns([1.5, 1.5])

with g4:
    st.markdown('<p class="section-title">Riesgo por programa</p>', unsafe_allow_html=True)
    prog_risk = (
        dff.groupby(["PROGRAMA_CURRICULAR", "NIVEL_RIESGO"])
        .size()
        .reset_index(name="n")
    )
    fig_prog = px.bar(
        prog_risk,
        x="n",
        y="PROGRAMA_CURRICULAR",
        color="NIVEL_RIESGO",
        color_discrete_map=COLOR_RIESGO,
        orientation="h",
        category_orders={"NIVEL_RIESGO": ["Crítico", "Alto", "Medio", "Bajo"]},
        labels={"n": "Estudiantes", "PROGRAMA_CURRICULAR": ""},
    )
    fig_prog.update_layout(
        margin=dict(t=5, b=5, l=5, r=10),
        height=280,
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(size=11),
        barmode="stack",
    )
    st.plotly_chart(fig_prog, use_container_width=True, config={"displayModeBar": False})

with g5:
    st.markdown('<p class="section-title">Frecuencia de alertas activas</p>', unsafe_allow_html=True)
    flag_rename = {
        "1 y 2 semestre": "1°/2° semestre",
        "Reingreso": "Reingreso",
        "P.A.P.A": "PAPA bajo",
        "Traslado": "Traslado",
        "PAPA +4": "PAPA ≥ 4",
        "Admisión": "Admisión especial",
        "alerta_4": "Alerta 4",
        "alerta_5": "Alerta 5",
    }
    flag_counts = {}
    for col, lbl in flag_rename.items():
        if col in dff.columns:
            flag_counts[lbl] = (dff[col].str.strip().str.upper() == "SI").sum()
    fc_df = (
        pd.Series(flag_counts)
        .sort_values(ascending=True)
        .reset_index()
    )
    fc_df.columns = ["Alerta", "Estudiantes"]
    fig_flags = px.bar(
        fc_df,
        x="Estudiantes",
        y="Alerta",
        orientation="h",
        text="Estudiantes",
        color="Estudiantes",
        color_continuous_scale=["#bfdbfe", "#1e40af"],
    )
    fig_flags.update_traces(textposition="outside", textfont_size=11)
    fig_flags.update_layout(
        margin=dict(t=5, b=5, l=5, r=10),
        height=280,
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        coloraxis_showscale=False,
        font=dict(size=11),
        xaxis_title="Estudiantes",
        yaxis_title=None,
    )
    st.plotly_chart(fig_flags, use_container_width=True, config={"displayModeBar": False})

st.divider()

# ─── Tabla detallada ─────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Listado detallado de estudiantes</p>', unsafe_allow_html=True)

col_search, col_sort, col_export = st.columns([2, 1.5, 0.8])
with col_search:
    busqueda = st.text_input("🔎 Buscar por nombre o documento", placeholder="Ej: García, 1006...")
with col_sort:
    orden = st.selectbox(
        "Ordenar por",
        ["NIVEL_RIESGO", "PAPA", "AVANCE", "MATRICULAS", "PUNTAJE_RIESGO"],
        format_func=lambda x: {
            "NIVEL_RIESGO": "Nivel de riesgo",
            "PAPA": "PAPA",
            "AVANCE": "Avance %",
            "MATRICULAS": "N° matrículas",
            "PUNTAJE_RIESGO": "Puntaje riesgo",
        }.get(x, x),
    )

# Filtrar por búsqueda
tabla = dff.copy()
if busqueda.strip():
    mask = (
        tabla["NOMBRE COMPLETO"].str.contains(busqueda, case=False, na=False) |
        tabla["DOCUMENTO"].astype(str).str.contains(busqueda, na=False)
    )
    tabla = tabla[mask]

# Ordenar
orden_cat = {"Bajo": 1, "Medio": 2, "Alto": 3, "Crítico": 4}
if orden == "NIVEL_RIESGO":
    tabla["_sort"] = tabla["NIVEL_RIESGO"].map(orden_cat)
    tabla = tabla.sort_values("_sort", ascending=False).drop(columns=["_sort"])
elif orden in ["PAPA", "AVANCE"]:
    tabla = tabla.sort_values(orden, ascending=True)
else:
    tabla = tabla.sort_values(orden, ascending=False)

# Columnas a mostrar
FLAG_COLS_SHOW = ["1 y 2 semestre", "Reingreso", "P.A.P.A", "Traslado", "PAPA +4", "Admisión"]
existing_flags = [c for c in FLAG_COLS_SHOW if c in tabla.columns]

cols_show = ["NOMBRE COMPLETO", "PROGRAMA_CURRICULAR", "MATRICULAS",
             "PAPA_DISP", "AVANCE", "NIVEL_RIESGO", "PUNTAJE_RIESGO",
             "PROFESIONAL REPORTE"] + existing_flags

tabla_display = tabla[cols_show].rename(columns={
    "NOMBRE COMPLETO": "Nombre",
    "PROGRAMA_CURRICULAR": "Programa",
    "MATRICULAS": "Matrículas",
    "PAPA_DISP": "PAPA",
    "AVANCE": "Avance %",
    "NIVEL_RIESGO": "Riesgo",
    "PUNTAJE_RIESGO": "Puntaje",
    "PROFESIONAL REPORTE": "Profesional",
    "P.A.P.A": "PAPA bajo",
    "PAPA +4": "PAPA≥4",
    "Admisión": "Adm. esp.",
    "1 y 2 semestre": "1°/2° sem",
})

# Formatear avance
tabla_display["Avance %"] = tabla_display["Avance %"].apply(
    lambda x: f"{x:.1f}%" if pd.notna(x) else "—"
)

st.dataframe(
    tabla_display,
    use_container_width=True,
    height=420,
    column_config={
        "Riesgo": st.column_config.TextColumn("Riesgo", width="small"),
        "Puntaje": st.column_config.NumberColumn("Puntaje", format="%.2f"),
        "Matrículas": st.column_config.NumberColumn("Matrículas", format="%d"),
    },
    hide_index=True,
)

st.caption(f"Mostrando {len(tabla_display):,} registros · Tabla generada en memoria — no se guarda ningún dato.")

# ─── Exportar (solo la vista filtrada, como CSV en memoria) ───────────────────
with col_export:
    st.markdown("<br>", unsafe_allow_html=True)
    csv_bytes = tabla_display.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇ Exportar CSV",
        data=csv_bytes,
        file_name=f"riesgo_{periodo}.csv",
        mime="text/csv",
        use_container_width=True,
    )
