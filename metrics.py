"""
metrics.py
==========
Regras de negócio e agregações do dashboard People Analytics.

Regra de organização usada no projeto:
- app.py: interface, leitura, tratamento básico, filtros e montagem das páginas.
- metrics.py: cálculos, groupbys, merges e indicadores.
- charts.py: apenas criação e formatação dos gráficos Plotly.

Este arquivo não usa comandos Streamlit nem cria gráficos.
"""

import pandas as pd
import numpy as np


PERFORMANCE_SCORE = {
    "Plano de melhoria": 1,
    "Precisa melhorar": 2,
    "Atende plenamente": 3,
    "Acima do esperado": 4,
}


# ============================================================
# 1. MÉTRICAS DE FOTOGRAFIA MENSAL
# ============================================================

def calcular_headcount(foto_ativa: pd.DataFrame) -> int:
    """Quantidade de colaboradores distintos ativos na fotografia mensal."""
    return int(foto_ativa["ID_Funcionario"].nunique())


def calcular_salario_medio(foto_ativa: pd.DataFrame) -> float:
    """Salário médio dos colaboradores ativos na fotografia mensal."""
    return float(foto_ativa["Salario"].mean()) if not foto_ativa.empty else 0.0


def calcular_salario_mediano(foto_ativa: pd.DataFrame) -> float:
    """Salário mediano dos colaboradores ativos na fotografia mensal."""
    return float(foto_ativa["Salario"].median()) if not foto_ativa.empty else 0.0


def headcount_por_departamento(foto_ativa: pd.DataFrame) -> pd.DataFrame:
    return (
        foto_ativa.groupby("Departamento", as_index=False)
        .agg(Headcount=("ID_Funcionario", "nunique"))
        .sort_values("Headcount", ascending=True)
    )


def headcount_por_estado(foto_ativa: pd.DataFrame) -> pd.DataFrame:
    return (
        foto_ativa.groupby("Estado", as_index=False)
        .agg(Headcount=("ID_Funcionario", "nunique"))
        .sort_values("Headcount", ascending=False)
    )


def headcount_por_unidade(foto_ativa: pd.DataFrame) -> pd.DataFrame:
    return (
        foto_ativa.groupby("Tipo_Unidade", as_index=False)
        .agg(Headcount=("ID_Funcionario", "nunique"))
        .sort_values("Headcount", ascending=False)
    )


def salario_medio_por_nivel(foto_ativa: pd.DataFrame) -> pd.DataFrame:
    return (
        foto_ativa.groupby("Nivel", as_index=False)
        .agg(
            Salario_Medio=("Salario", "mean"),
            Headcount=("ID_Funcionario", "nunique"),
        )
        .sort_values("Salario_Medio", ascending=False)
    )


def salario_medio_matriz_filial(foto_ativa: pd.DataFrame) -> pd.DataFrame:
    return (
        foto_ativa.groupby("Tipo_Unidade", as_index=False)
        .agg(
            Salario_Medio=("Salario", "mean"),
            Headcount=("ID_Funcionario", "nunique"),
        )
        .sort_values("Salario_Medio", ascending=False)
    )


def salario_por_departamento(foto_ativa: pd.DataFrame) -> pd.DataFrame:
    """Base resumida para comparação salarial por departamento."""
    return (
        foto_ativa.groupby("Departamento", as_index=False)
        .agg(
            Salario_Medio=("Salario", "mean"),
            Salario_Mediano=("Salario", "median"),
            Headcount=("ID_Funcionario", "nunique"),
        )
        .sort_values("Salario_Medio", ascending=False)
    )


# ============================================================
# 2. MÉTRICAS HISTÓRICAS
# ============================================================

def evolucao_headcount(df: pd.DataFrame) -> pd.DataFrame:
    """Headcount ativo no fechamento de cada mês."""
    return (
        df[df["Ativo_Fim_Mes"]]
        .groupby("Data_Referencia", as_index=False)
        .agg(Headcount=("ID_Funcionario", "nunique"))
        .sort_values("Data_Referencia")
    )


def calcular_turnover_anual(df: pd.DataFrame) -> pd.DataFrame:
    """
    Turnover anual = desligados distintos no ano / headcount médio mensal * 100.
    """
    hc_mensal = evolucao_headcount(df).copy()

    if hc_mensal.empty:
        return pd.DataFrame(columns=["Ano", "Headcount_Medio", "Desligados", "Taxa_Turnover"])

    hc_mensal["Ano"] = hc_mensal["Data_Referencia"].dt.year
    hc_medio = (
        hc_mensal.groupby("Ano", as_index=False)
        .agg(Headcount_Medio=("Headcount", "mean"))
    )

    desligados = (
        df[df["Data_Desligamento"].notna()]
        .sort_values("Data_Referencia")
        .drop_duplicates("ID_Funcionario", keep="last")
        .copy()
    )

    if desligados.empty:
        desligados_ano = pd.DataFrame(columns=["Ano", "Desligados"])
    else:
        desligados["Ano"] = desligados["Data_Desligamento"].dt.year
        desligados_ano = (
            desligados.groupby("Ano", as_index=False)
            .agg(Desligados=("ID_Funcionario", "nunique"))
        )

    turnover = hc_medio.merge(desligados_ano, on="Ano", how="left")
    turnover["Desligados"] = turnover["Desligados"].fillna(0).astype(int)
    turnover["Taxa_Turnover"] = np.where(
        turnover["Headcount_Medio"] > 0,
        turnover["Desligados"] / turnover["Headcount_Medio"] * 100,
        0,
    )
    turnover["Taxa_Turnover"] = turnover["Taxa_Turnover"].round(2)
    return turnover.sort_values("Ano")


def admissoes_desligamentos_mensais(df_ano: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Admissões e desligamentos distintos, mês a mês, no ano selecionado."""
    funcionarios = (
        df_ano.sort_values("Data_Referencia")
        .drop_duplicates("ID_Funcionario", keep="last")
        .copy()
    )

    adm = funcionarios[funcionarios["Data_Admissao"].dt.year == ano].copy()
    adm["Mes"] = adm["Data_Admissao"].dt.month
    admissoes = (
        adm.groupby("Mes", as_index=False)
        .agg(Admissoes=("ID_Funcionario", "nunique"))
    )

    des = funcionarios[
        funcionarios["Data_Desligamento"].notna()
        & (funcionarios["Data_Desligamento"].dt.year == ano)
    ].copy()
    des["Mes"] = des["Data_Desligamento"].dt.month
    desligamentos = (
        des.groupby("Mes", as_index=False)
        .agg(Desligamentos=("ID_Funcionario", "nunique"))
    )

    meses = pd.DataFrame({"Mes": range(1, 13)})
    resultado = meses.merge(admissoes, on="Mes", how="left").merge(
        desligamentos, on="Mes", how="left"
    )
    resultado[["Admissoes", "Desligamentos"]] = resultado[
        ["Admissoes", "Desligamentos"]
    ].fillna(0).astype(int)

    nomes = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
    }
    resultado["Mes_Nome"] = resultado["Mes"].map(nomes)
    return resultado


def indicadores_movimentacao_anual(df_ano: pd.DataFrame, ano: int) -> dict:
    """Total de admissões e desligamentos distintos ocorridos no ano."""
    funcionarios = (
        df_ano.sort_values("Data_Referencia")
        .drop_duplicates("ID_Funcionario", keep="last")
        .copy()
    )
    admissoes = funcionarios[funcionarios["Data_Admissao"].dt.year == ano]["ID_Funcionario"].nunique()
    desligamentos = funcionarios[
        funcionarios["Data_Desligamento"].notna()
        & (funcionarios["Data_Desligamento"].dt.year == ano)
    ]["ID_Funcionario"].nunique()
    return {
        "Admissoes": int(admissoes),
        "Desligamentos": int(desligamentos),
        "Saldo": int(admissoes - desligamentos),
    }


# ============================================================
# 3. DESLIGAMENTOS E RECRUTAMENTO
# ============================================================

def motivos_desligamento(df_ano: pd.DataFrame, ano: int) -> pd.DataFrame:
    desligados = (
        df_ano[
            df_ano["Data_Desligamento"].notna()
            & (df_ano["Data_Desligamento"].dt.year == ano)
            & (df_ano["Motivo_Desligamento"] != "N/A - Ainda empregado")
        ]
        .sort_values("Data_Referencia")
        .drop_duplicates("ID_Funcionario", keep="last")
        .copy()
    )

    return (
        desligados.groupby("Motivo_Desligamento", as_index=False)
        .agg(Desligados=("ID_Funcionario", "nunique"))
        .sort_values("Desligados", ascending=True)
    )


def desligamentos_por_departamento(df_ano: pd.DataFrame, ano: int) -> pd.DataFrame:
    desligados = (
        df_ano[
            df_ano["Data_Desligamento"].notna()
            & (df_ano["Data_Desligamento"].dt.year == ano)
        ]
        .sort_values("Data_Referencia")
        .drop_duplicates("ID_Funcionario", keep="last")
        .copy()
    )

    return (
        desligados.groupby("Departamento", as_index=False)
        .agg(Desligados=("ID_Funcionario", "nunique"))
        .sort_values("Desligados", ascending=True)
    )


def desempenho_por_fonte_recrutamento(df_ano: pd.DataFrame) -> pd.DataFrame:
    latest = (
        df_ano.sort_values("Data_Referencia")
        .drop_duplicates("ID_Funcionario", keep="last")
        .copy()
    )
    latest["Score_Desempenho"] = latest["Pontuacao_Desempenho"].map(PERFORMANCE_SCORE)

    resultado = (
        latest.groupby("Fonte_Recrutamento", as_index=False)
        .agg(
            Score_Medio=("Score_Desempenho", "mean"),
            Funcionarios=("ID_Funcionario", "nunique"),
        )
        .dropna(subset=["Score_Medio"])
        .sort_values(["Score_Medio", "Funcionarios"], ascending=[False, False])
    )
    resultado["Score_Medio"] = resultado["Score_Medio"].round(2)
    return resultado


# ============================================================
# 4. INSIGHTS TEXTUAIS SIMPLES
# ============================================================

def gerar_insights_executivos(
    foto_ativa: pd.DataFrame,
    turnover: pd.DataFrame,
    ano: int,
) -> list[str]:
    """Gera frases simples com base nos números já calculados."""
    insights = []

    hc_dept = headcount_por_departamento(foto_ativa)
    if not hc_dept.empty:
        maior = hc_dept.sort_values("Headcount", ascending=False).iloc[0]
        total = hc_dept["Headcount"].sum()
        participacao = (maior["Headcount"] / total * 100) if total else 0
        insights.append(
            f"{maior['Departamento']} concentra {int(maior['Headcount'])} colaboradores "
            f"({participacao:.1f}% do headcount filtrado)."
        )

    sal_nivel = salario_medio_por_nivel(foto_ativa)
    if not sal_nivel.empty:
        topo = sal_nivel.iloc[0]
        insights.append(
            f"O maior salário médio por nível está em {topo['Nivel']}: "
            f"R$ {topo['Salario_Medio']:,.2f}."
        )

    linha_turnover = turnover[turnover["Ano"] == ano]
    if not linha_turnover.empty:
        taxa = float(linha_turnover.iloc[0]["Taxa_Turnover"])
        insights.append(f"A taxa de turnover de {ano} é {taxa:.2f}% para os filtros selecionados.")

    return insights
