import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime


# Configuração da página
st.set_page_config(page_title="Dashboard de Vistorias", layout="wide")

st.title("🏢 Dashboard de Vistorias")

# Upload
arquivo = st.sidebar.file_uploader("Envie o CSV", type=["csv"])

if arquivo is not None:
    # =========================
    # 📥 LEITURA E LIMPEZA
    # =========================
    df = pd.read_csv(arquivo, sep=None, engine="python")

    # Limpar nomes das colunas (evita KeyError)
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    # Ver colunas (debug opcional)
    # st.write(df.columns)

    # =========================
    # 🔍 VALIDAÇÃO
    # =========================
    colunas_necessarias = [
        "Data_Vistoria",
        "Tipo_Imovel",
        "Permissao",
        "Vistoriador",
        "Proxima_Vistoria"
    ]

    for col in colunas_necessarias:
        if col not in df.columns:
            st.error(f"❌ Coluna obrigatória não encontrada: {col}")
            st.stop()

    # =========================
    # 📅 TRATAMENTO DE DATAS
    # =========================
    df["Data_Vistoria"] = pd.to_datetime(df["Data_Vistoria"], errors="coerce")
    df["Proxima_Vistoria"] = pd.to_datetime(df["Proxima_Vistoria"], errors="coerce")

    # =========================
    # ⚠️ STATUS (VENCIMENTO)
    # =========================
    hoje = pd.Timestamp.today()

    df["Status"] = df["Proxima_Vistoria"].apply(
        lambda x: "Vencida" if pd.notnull(x) and x < hoje else "Em dia"
    )

    # =========================
    # 📊 KPIs
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de Vistorias", len(df))

    with col2:
        vencidas = df[df["Status"] == "Vencida"]
        st.metric("Vistorias Vencidas", len(vencidas))

    with col3:
        st.metric("Total de Vistoriadores", df["Vistoriador"].nunique())

    # Lista de vistoriadores
    st.caption("👷 " + ", ".join(df["Vistoriador"].dropna().unique()))

    # =========================
    # 🎛️ FILTROS
    # =========================
    st.sidebar.subheader("🔍 Filtros")

    tipo_imovel = st.sidebar.multiselect(
        "Tipo de Imóvel",
        df["Tipo_Imovel"].dropna().unique(),
        default=df["Tipo_Imovel"].dropna().unique()
    )

    vistoriador = st.sidebar.multiselect(
        "Vistoriador",
        df["Vistoriador"].dropna().unique(),
        default=df["Vistoriador"].dropna().unique()
    )

    data_inicio = st.sidebar.date_input(
        "Data inicial",
        df["Data_Vistoria"].min()
    )

    data_fim = st.sidebar.date_input(
        "Data final",
        df["Data_Vistoria"].max()
    )

    # Aplicar filtros
    df_filtrado = df[
        (df["Tipo_Imovel"].isin(tipo_imovel)) &
        (df["Vistoriador"].isin(vistoriador)) &
        (df["Data_Vistoria"] >= pd.to_datetime(data_inicio)) &
        (df["Data_Vistoria"] <= pd.to_datetime(data_fim))
    ]

    # =========================
    # 📊 GRÁFICOS
    # =========================

    # Status (cores)
    fig_status = px.bar(
        df_filtrado,
        x="Tipo_Imovel",
        color="Status",
        title="📊 Status das Vistorias",
        color_discrete_map={
            "Em dia": "green",
            "Vencida": "red"
        }
    )

    st.plotly_chart(fig_status, use_container_width=True)

    # Vistorias por vistoriador
    fig_vistoriador = px.bar(
        df_filtrado,
        x="Vistoriador",
        color="Vistoriador",
        title="👷 Vistorias por Vistoriador"
    )

    st.plotly_chart(fig_vistoriador, use_container_width=True)

    # Pizza de permissão
    fig_perm = px.pie(
        df_filtrado,
        names="Permissao",
        title="📜 Tipos de Permissão"
    )

    st.plotly_chart(fig_perm, use_container_width=True)

    # =========================
    # ⚠️ GRÁFICO VENCIDAS
    # =========================
    df_vencidas = df_filtrado[df_filtrado["Status"] == "Vencida"]

    if not df_vencidas.empty:
        fig_vencidas = px.bar(
            df_vencidas,
            x="Vistoriador",
            title="⚠️ Vistorias Vencidas",
            color="Vistoriador"
        )

        st.plotly_chart(fig_vencidas, use_container_width=True)
    else:
        st.success("✅ Nenhuma vistoria vencida")

    # =========================
    # 📥 DOWNLOAD
    # =========================
    csv = df_filtrado.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Baixar relatório",
        data=csv,
        file_name="relatorio_vistorias.csv",
        mime="text/csv"
    )

    # =========================
    # 📄 TABELA
    # =========================
    st.subheader("📋 Dados")
    st.dataframe(df_filtrado)

else:
    st.info("👈 Envie um arquivo CSV para começar")