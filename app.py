import streamlit as st
import pandas as pd
from pathlib import Path

from metrics import (
    calcular_headcount,
    calcular_salario_medio,
    calcular_salario_mediano,
    headcount_por_departamento,
    headcount_por_estado,
    headcount_por_unidade,
    salario_medio_por_nivel,
    salario_medio_matriz_filial,
    salario_por_departamento,
    evolucao_headcount,
    calcular_turnover_anual,
    admissoes_desligamentos_mensais,
    indicadores_movimentacao_anual,
    motivos_desligamento,
    desligamentos_por_departamento,
    desempenho_por_fonte_recrutamento,
    gerar_insights_executivos,
)

from charts import (
    grafico_headcount_departamento,
    grafico_evolucao_headcount,
    grafico_turnover,
    grafico_salario_nivel,
    grafico_matriz_filial,
    grafico_salario_departamento,
    grafico_distribuicao_salarial,
    grafico_headcount_estado,
    grafico_headcount_unidade,
    grafico_admissoes_desligamentos,
    grafico_motivos_desligamento,
    grafico_desligamentos_departamento,
    grafico_desempenho_recrutamento,
)


# ============================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="People Analytics Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("People Analytics Dashboard")
st.caption(
    "Visão interativa de headcount, turnover, movimentações, remuneração, "
    "recrutamento e desligamentos."
)


# ============================================================
# 2. LEITURA DA BASE
# ============================================================

BASE_DIR = Path(__file__).parent
arquivo = BASE_DIR / "data" / "Base_People_Analytics.xlsx"
LOGO_PATH = BASE_DIR / "assets" / "logo.png"



@st.cache_data(show_spinner="Carregando base de People Analytics...")
def carregar_dados(caminho):
    return pd.read_excel(caminho, sheet_name="BaseRH")


df = carregar_dados(arquivo)


# ============================================================
# 3. TRATAMENTO BÁSICO
# ============================================================

for coluna in ["Data_Referencia", "Data_Desligamento", "Data_Admissao"]:
    df[coluna] = pd.to_datetime(df[coluna], errors="coerce")

df["Salario"] = pd.to_numeric(df["Salario"], errors="coerce")
df["Fim_Mes"] = df["Data_Referencia"] + pd.offsets.MonthEnd(0)

# Regra histórica: estava ativo no fechamento daquele mês?
df["Ativo_Fim_Mes"] = (
    (df["Data_Admissao"] <= df["Fim_Mes"])
    & (
        df["Data_Desligamento"].isna()
        | (df["Data_Desligamento"] > df["Fim_Mes"])
    )
)


# ============================================================
# 4. FILTROS
# ============================================================

# LOGO
st.sidebar.image(
    LOGO_PATH,
    use_container_width=True
)



st.sidebar.header("Filtros")

anos = sorted(df["Data_Referencia"].dt.year.dropna().unique())
ano_selecionado = st.sidebar.selectbox(
    "Ano de referência",
    anos,
    index=len(anos) - 1,
)

foto_ano = df[df["Data_Referencia"].dt.year == ano_selecionado].copy()

meses_dict = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}
meses = sorted(foto_ano["Data_Referencia"].dt.month.dropna().unique())
mes_selecionado = st.sidebar.selectbox(
    "Mês de referência",
    meses,
    index=len(meses) - 1,
    format_func=lambda x: meses_dict[x],
)

departamentos = sorted(df["Departamento"].dropna().unique())
departamentos_sel = st.sidebar.multiselect(
    "Departamento",
    departamentos,
    default=departamentos,
)

estados = sorted(df["Estado"].dropna().unique())
estados_sel = st.sidebar.multiselect(
    "Estado",
    estados,
    default=estados,
)

niveis = sorted(df["Nivel"].dropna().unique())
niveis_sel = st.sidebar.multiselect(
    "Nível hierárquico",
    niveis,
    default=niveis,
)

unidades = sorted(df["Tipo_Unidade"].dropna().unique())
unidades_sel = st.sidebar.multiselect(
    "Tipo de unidade",
    unidades,
    default=unidades,
)


# ============================================================
# 5. BASES FILTRADAS
# ============================================================

# Filtros de dimensões aplicados ao histórico completo.
df_dimensoes = df[
    df["Departamento"].isin(departamentos_sel)
    & df["Estado"].isin(estados_sel)
    & df["Nivel"].isin(niveis_sel)
    & df["Tipo_Unidade"].isin(unidades_sel)
].copy()

# Recorte anual para análises de movimentação, recrutamento e desligamento.
df_ano_filtrado = df_dimensoes[
    df_dimensoes["Data_Referencia"].dt.year == ano_selecionado
].copy()

# Fotografia mensal para KPIs e remuneração.
foto_mes = df_ano_filtrado[
    df_ano_filtrado["Data_Referencia"].dt.month == mes_selecionado
].copy()
foto_ativa = foto_mes[foto_mes["Ativo_Fim_Mes"]].copy()


# ============================================================
# 6. CÁLCULO DAS MÉTRICAS
# ============================================================

headcount = calcular_headcount(foto_ativa)
salario_medio = calcular_salario_medio(foto_ativa)
salario_mediano = calcular_salario_mediano(foto_ativa)

dados_headcount = headcount_por_departamento(foto_ativa)
dados_estado = headcount_por_estado(foto_ativa)
dados_unidade = headcount_por_unidade(foto_ativa)
dados_salario_nivel = salario_medio_por_nivel(foto_ativa)
dados_matriz_filial = salario_medio_matriz_filial(foto_ativa)
dados_salario_dept = salario_por_departamento(foto_ativa)
dados_evolucao = evolucao_headcount(df_dimensoes)
dados_turnover = calcular_turnover_anual(df_dimensoes)
dados_movimentacao = admissoes_desligamentos_mensais(df_ano_filtrado, ano_selecionado)
movimentacao_kpi = indicadores_movimentacao_anual(df_ano_filtrado, ano_selecionado)
dados_motivos = motivos_desligamento(df_ano_filtrado, ano_selecionado)
dados_deslig_dept = desligamentos_por_departamento(df_ano_filtrado, ano_selecionado)
dados_recrutamento = desempenho_por_fonte_recrutamento(df_ano_filtrado)

linha_turnover = dados_turnover[dados_turnover["Ano"] == ano_selecionado]
taxa_turnover = float(linha_turnover.iloc[0]["Taxa_Turnover"]) if not linha_turnover.empty else 0.0


# ============================================================
# 7. KPIs
# ============================================================

with st.container():

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Colaboradores ativos", f"{headcount:,}".replace(",", "."))

    with k2:
        st.metric(
            "Salário médio",
            f"R$ {salario_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )

    with k3:
        st.metric(
            "Salário mediano",
            f"R$ {salario_mediano:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )

    with k4:
        st.metric("Turnover anual", f"{taxa_turnover:.2f}%".replace(".", ","))


# ============================================================
# 8. ABAS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Visão Executiva",
        "Headcount & Movimentações",
        "Remuneração",
        "Recrutamento & Desligamentos",
        "Dados & Metodologia",
    ]
)


# ============================================================
# TAB 1 - VISÃO EXECUTIVA
# ============================================================

with tab1:

    with st.container():

        st.subheader(f"Resumo executivo - {meses_dict[mes_selecionado]}/{ano_selecionado}")

        insights = gerar_insights_executivos(foto_ativa, dados_turnover, ano_selecionado)
        if insights:
            for texto in insights:
                st.info(texto)

    with st.container():

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                grafico_headcount_departamento(dados_headcount),
                use_container_width=True,
                key="exec_headcount",
            )
        with c2:
            st.plotly_chart(
                grafico_evolucao_headcount(dados_evolucao),
                use_container_width=True,
                key="exec_evolucao",
            )

    with st.container():

        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(
                grafico_turnover(dados_turnover),
                use_container_width=True,
                key="exec_turnover",
            )
        with c4:
            st.plotly_chart(
                grafico_salario_nivel(dados_salario_nivel),
                use_container_width=True,
                key="exec_salario_nivel",
            )


# ============================================================
# TAB 2 - HEADCOUNT & MOVIMENTAÇÕES
# ============================================================

with tab2:

    with st.container():

        st.subheader("Estrutura do quadro e movimentações")

        m1, m2, m3 = st.columns(3)
        m1.metric("Admissões no ano", movimentacao_kpi["Admissoes"])
        m2.metric("Desligamentos no ano", movimentacao_kpi["Desligamentos"])
        m3.metric("Saldo anual", movimentacao_kpi["Saldo"])


    with st.container():

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                grafico_headcount_estado(dados_estado),
                use_container_width=True,
                key="hc_estado",
            )
        with c2:
            st.plotly_chart(
                grafico_headcount_unidade(dados_unidade),
                use_container_width=True,
                key="hc_unidade",
            )

    with st.container():

        st.plotly_chart(
            grafico_admissoes_desligamentos(dados_movimentacao),
            use_container_width=True,
            key="movimentacoes",
        )

        st.subheader("Evolução mensal")
        tabela_evolucao = dados_evolucao.copy()
        tabela_evolucao["Mês"] = tabela_evolucao["Data_Referencia"].dt.strftime("%m/%Y")
        st.dataframe(
            tabela_evolucao[["Mês", "Headcount"]].sort_values("Mês", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# TAB 3 - REMUNERAÇÃO
# ============================================================

with tab3:

    with st.container():

        st.subheader("Análise de remuneração")
        st.caption(
            "As análises salariais usam somente os colaboradores ativos na fotografia mensal selecionada."
        )


    with st.container():

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                grafico_salario_nivel(dados_salario_nivel),
                use_container_width=True,
                key="rem_salario_nivel",
            )
        with c2:
            st.plotly_chart(
                grafico_matriz_filial(dados_matriz_filial),
                use_container_width=True,
                key="rem_matriz_filial",
            )


    with st.container():

        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(
                grafico_salario_departamento(dados_salario_dept),
                use_container_width=True,
                key="rem_salario_dept",
            )
        with c4:
            st.plotly_chart(
                grafico_distribuicao_salarial(foto_ativa),
                use_container_width=True,
                key="rem_boxplot",
            )

    with st.container():

        with st.expander("Ver detalhe dos colaboradores da fotografia"):
            colunas = [
                "ID_Funcionario", "Nome_Funcionario", "Departamento", "Cargo",
                "Nivel", "Estado", "Tipo_Unidade", "Salario",
            ]
            st.dataframe(
                foto_ativa[colunas].sort_values("Salario", ascending=False),
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# TAB 4 - RECRUTAMENTO & DESLIGAMENTOS
# ============================================================

with tab4:
    st.subheader(f"Recrutamento e desligamentos - {ano_selecionado}")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            grafico_motivos_desligamento(dados_motivos),
            use_container_width=True,
            key="deslig_motivos",
        )
    with c2:
        st.plotly_chart(
            grafico_desligamentos_departamento(dados_deslig_dept),
            use_container_width=True,
            key="deslig_dept",
        )

    st.plotly_chart(
        grafico_desempenho_recrutamento(dados_recrutamento),
        use_container_width=True,
        key="recrutamento_score",
    )

    st.caption(
        "Para a comparação de desempenho, as categorias foram convertidas em escala ordinal: "
        "Plano de melhoria=1, Precisa melhorar=2, Atende plenamente=3 e Acima do esperado=4."
    )


# ============================================================
# TAB 5 - DADOS & METODOLOGIA
# ============================================================

with tab5:
    st.subheader("Metodologia e qualidade dos dados")

    st.markdown(
        """
        **Granularidade da base:** cada linha representa a fotografia de um funcionário em um mês.

        **Headcount ativo:** funcionário admitido até o último dia do mês e sem desligamento até esse fechamento.

        **Turnover anual:** desligados distintos no ano dividido pelo headcount médio mensal do ano.

        **Salário:** as médias e distribuições usam apenas colaboradores ativos na fotografia mensal selecionada.

        **Filtros:** Departamento, Estado, Nível e Tipo de Unidade afetam tanto a fotografia atual quanto as análises históricas.
        """
    )

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Linhas na base", f"{len(df):,}".replace(",", "."))
    q2.metric("Funcionários distintos", df["ID_Funcionario"].nunique())
    q3.metric("Chaves mês+func. duplicadas", int(df.duplicated(["Data_Referencia", "ID_Funcionario"]).sum()))
    q4.metric("Salários nulos", int(df["Salario"].isna().sum()))

    st.subheader("Prévia da base tratada")
    st.dataframe(df.head(100), use_container_width=True, hide_index=True)
