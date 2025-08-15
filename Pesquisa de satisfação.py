# app.py
# Dashboard de Avaliações - BeSmart (Versão visual aprimorada e gamificada, sem aba Ranking)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# CONFIG & ESTILO
# =========================
st.set_page_config(
    page_title="BeSmart | Avaliações de Reuniões",
    page_icon="📈",
    layout="wide"
)

# CSS aprimorado
st.markdown("""
<style>
* { font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
h1, h2, h3 { font-weight: 700; letter-spacing: -0.3px; }

.kpi-card {
  border: 1px solid #ececec;
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 1px 14px rgba(0,0,0,0.06);
  background: white;
  transition: all 0.3s ease-in-out;
}
.kpi-card:hover {
  transform: scale(1.03);
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.kpi-title { font-size: 0.85rem; color: #666; margin-bottom: 6px; }
.kpi-value { font-size: 1.8rem; font-weight: 800; line-height: 1.1; }

.comment-card {
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  padding: 12px 14px;
  background-color: #fafafa;
  margin-bottom: 10px;
  font-size: 0.9rem;
}
.comment-author {
  font-weight: 600;
  margin-bottom: 4px;
  color: #444;
}
.comment-text { color: #333; }

.badge-ok {
  background: #10b98122; color: #065f46; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 700;
}
.badge-nok {
  background: #ef444422; color: #7f1d1d; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CARREGAMENTO & LIMPEZA
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTSb09AJoTWy7rivoymiFsvRTpNxm3XKgvQ4lghKLTCBKWEVKbGvdl4FpuUueFP-WFu_1NeSf5nheNS/pub?output=csv"

@st.cache_data(ttl=3600, show_spinner=False)
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    rename_map = {
        "Especialista Responsável": "Especialista",
        "Data da Pesquisa": "Data",
        "3.1. O advisor estava bem planejado e organizado": "Q3_1_Planejamento",
        "3.2. A comunicação foi clara e objetiva": "Q3_2_Comunicacao",
        "3.3. Demonstrou domínio técnico sobre o tema": "Q3_3_Dominio",
        "3.4. Teve foco no fechamento do negócio e sugeriu nova data para conclusão": "Q3_4_Fechamento",
        "3.5. Transmitiu confiança e postura profissional": "Q3_5_Confianca",
        "4. Qual a probabilidade de recomendar o advisor da BeSmart para um colega?": "Q4_NPS",
        "5. Gostaria de deixar algum comentário adicional?": "Comentario"
    }
    for k, v in rename_map.items():
        if k in df.columns:
            df.rename(columns={k: v}, inplace=True)

    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")

    nota_cols = [c for c in ["Q3_1_Planejamento","Q3_2_Comunicacao","Q3_3_Dominio","Q3_4_Fechamento","Q3_5_Confianca","Q4_NPS"] if c in df.columns]
    for c in nota_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    q3_cols = [c for c in ["Q3_1_Planejamento","Q3_2_Comunicacao","Q3_3_Dominio","Q3_4_Fechamento","Q3_5_Confianca"] if c in df.columns]
    if q3_cols:
        df["Nota_Media_3x"] = df[q3_cols].mean(axis=1)

    if "Etapa" in df.columns:
        df["Etapa"] = df["Etapa"].astype(str).str.strip().str.title()
        df["Etapa"] = df["Etapa"].replace({"Respondida":"Respondido","Recebida":"Respondido"})
    else:
        df["Etapa"] = "Respondido"

    if "Especialista" in df.columns:
        df["Especialista"] = df["Especialista"].fillna("— Sem especialista —").astype(str).str.strip()
    else:
        df["Especialista"] = "— Sem especialista —"

    if "Comentario" not in df.columns:
        df["Comentario"] = ""

    return df

df = load_data(CSV_URL)

# =========================
# FILTROS
# =========================
st.sidebar.header("⚙️ Filtros")
min_date = pd.to_datetime(df["Data"].min()) if "Data" in df.columns else None
max_date = pd.to_datetime(df["Data"].max()) if "Data" in df.columns else None

if min_date is not None and max_date is not None and not pd.isna(min_date) and not pd.isna(max_date):
    date_range = st.sidebar.date_input(
        "Período",
        value=(min_date.date(), max_date.date())
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df = df[(df["Data"] >= start_date) & (df["Data"] <= end_date)]

especialistas = sorted(df["Especialista"].dropna().unique().tolist())
sel_especialistas = st.sidebar.multiselect("Especialista", options=especialistas, default=especialistas)
df = df[df["Especialista"].isin(sel_especialistas)]

# =========================
# KPIs
# =========================
total_reunioes = len(df)
total_recebidas = int(df[df["Etapa"].str.contains("Respond|Recebid", case=False, na=False)].shape[0]) if total_reunioes > 0 else 0
taxa_resposta_global = (total_recebidas / total_reunioes * 100) if total_reunioes > 0 else 0.0
media_global = float(df["Nota_Media_3x"].mean()) if "Nota_Media_3x" in df.columns and not df.empty else np.nan

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total de Reuniões</div><div class="kpi-value">📅 {total_reunioes}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Recebidas/Avaliadas</div><div class="kpi-value">📥 {total_recebidas}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Taxa de Avaliação</div><div class="kpi-value">🎯 {taxa_resposta_global:.1f}%</div></div>', unsafe_allow_html=True)
with col4:
    if not np.isnan(media_global):
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Média 3.x (Geral)</div><div class="kpi-value">⭐ {media_global:.2f}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Média 3.x (Geral)</div><div class="kpi-value">⭐ —</div></div>', unsafe_allow_html=True)

# =========================
# POR ESPECIALISTA (resumo)
# =========================
resumo = pd.DataFrame(columns=["Especialista","Reuniões_Realizadas","Avaliadas","Média_3x"])  # fallback
if not df.empty:
    resumo = df.groupby("Especialista").agg(
        Reuniões_Realizadas=("Especialista", "count"),
        Avaliadas=("Etapa", lambda x: (x.str.contains("Respond|Recebid", case=False, na=False)).sum()),
        Média_3x=("Nota_Media_3x", "mean")
    ).reset_index()

    resumo["% Avaliada"] = np.where(
        resumo["Reuniões_Realizadas"] > 0,
        (resumo["Avaliadas"] / resumo["Reuniões_Realizadas"]) * 100,
        0.0
    )
    resumo["Meta_OK"] = np.where(
        (resumo["% Avaliada"] >= 50) & (resumo["Reuniões_Realizadas"] >= 10),
        True, False
    )

# =========================
# DASHBOARD
# =========================
st.title("BeSmart • Dashboard de Avaliações")

tab1, tab3, tab4 = st.tabs(["📊 Visão Geral", "🧑‍💼 Por Especialista", "💬 Comentários"])

with tab1:
    st.subheader("% Avaliada por Especialista")
    if not resumo.empty:
        sorted_resumo = resumo.sort_values("% Avaliada", ascending=False)
        fig1 = px.bar(
            sorted_resumo,
            x="Especialista", y="% Avaliada",
            text=sorted_resumo["% Avaliada"].round(1).astype(str) + "%",
            title=None
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(yaxis_title="% Avaliada", xaxis_title="Especialista", margin=dict(t=10))
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Sem dados para exibir no período/seleção atual.")

with tab3:
    st.subheader("Resumo por Especialista")
    if not resumo.empty:
        resumo_show = resumo.copy()
        resumo_show["% Avaliada"] = resumo_show["% Avaliada"].map(lambda v: f"{v:.1f}%")
        resumo_show["Meta"] = resumo_show["Meta_OK"].map(lambda x: "✅ Atingida" if x else "❌ Não atingida")
        st.dataframe(resumo_show, use_container_width=True)
    else:
        st.info("Sem dados para exibir no período/seleção atual.")

with tab4:
    st.subheader("Feedbacks e Comentários")
    if "Comentario" in df.columns and not df.empty:
        comentarios = df.dropna(subset=["Comentario"])
        comentarios = comentarios[comentarios["Comentario"].astype(str).str.strip() != ""]
    else:
        comentarios = pd.DataFrame(columns=["Especialista","Comentario","Data"])

    if comentarios.empty:
        st.info("Nenhum comentário registrado no período selecionado.")
    else:
        for especialista in comentarios["Especialista"].unique():
            st.markdown(f"### 👤 {especialista}")
            subset = comentarios[comentarios["Especialista"] == especialista]
            for _, row in subset.iterrows():
                data_fmt = row["Data"].strftime('%d/%m/%Y') if pd.notnull(row["Data"]) else "Data não informada"
                comentario_txt = str(row["Comentario"]).strip()
                st.markdown(f"""
                <div class="comment-card">
                    <div class="comment-author">{data_fmt}</div>
                    <div class="comment-text">{comentario_txt}</div>
                </div>
                """, unsafe_allow_html=True)
