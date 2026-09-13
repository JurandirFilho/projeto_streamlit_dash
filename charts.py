"""
charts.py
=========
Funções responsáveis somente pela camada visual do dashboard.
Cada função recebe um DataFrame pronto e devolve uma figura Plotly.
"""

import plotly.express as px

AZUL = "#00247D"
AMARELO = "#EFA903"
CINZA = "#6B7280"


def _layout_padrao(fig, altura=430):
    fig.update_layout(
        template="plotly_white",
        height=altura,
        margin=dict(l=25, r=25, t=65, b=35),
        legend_title_text="",
        hoverlabel=dict(font_size=12),
    )
    return fig


def grafico_headcount_departamento(dados):
    fig = px.bar(
        dados,
        x="Headcount",
        y="Departamento",
        text="Headcount",
        orientation="h",
        title="Headcount ativo por departamento",
        color_discrete_sequence=[AMARELO],
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(title_text="", showgrid=False, visible=False)
    fig.update_yaxes(title_text="")
    return _layout_padrao(fig)


def grafico_evolucao_headcount(dados):
    fig = px.line(
        dados,
        x="Data_Referencia",
        y="Headcount",
        markers=True,
        title="Evolução mensal do headcount",
        color_discrete_sequence=[AZUL],
    )
    fig.update_traces(line_width=3)
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Colaboradores ativos", gridcolor="rgba(0,0,0,0.08)")
    return _layout_padrao(fig)


def grafico_turnover(dados):
    fig = px.bar(
        dados,
        x="Ano",
        y="Taxa_Turnover",
        text="Taxa_Turnover",
        title="Taxa de turnover anual",
        color_discrete_sequence=[AZUL],
    )
    fig.update_traces(texttemplate="%{y:.2f}%", textposition="outside")
    fig.update_xaxes(title_text="", showgrid=False)
    fig.update_yaxes(title_text="Turnover (%)", gridcolor="rgba(0,0,0,0.08)")
    return _layout_padrao(fig)


def grafico_salario_nivel(dados):
    dados = dados.sort_values("Salario_Medio", ascending=True)
    fig = px.bar(
        dados,
        x="Salario_Medio",
        y="Nivel",
        text="Salario_Medio",
        orientation="h",
        title="Salário médio por nível hierárquico",
        color_discrete_sequence=[AZUL],
        hover_data={"Headcount": True},
    )
    fig.update_traces(texttemplate="R$ %{x:,.0f}", textposition="outside")
    fig.update_xaxes(title_text="Salário médio (R$)", gridcolor="rgba(0,0,0,0.08)")
    fig.update_yaxes(title_text="")
    return _layout_padrao(fig)


def grafico_matriz_filial(dados):
    fig = px.bar(
        dados,
        x="Tipo_Unidade",
        y="Salario_Medio",
        text="Salario_Medio",
        title="Média salarial - Matriz x Filiais",
        color_discrete_sequence=[AMARELO],
        hover_data={"Headcount": True},
    )
    fig.update_traces(texttemplate="R$ %{y:,.0f}", textposition="outside")
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Salário médio (R$)", gridcolor="rgba(0,0,0,0.08)")
    return _layout_padrao(fig)


def grafico_salario_departamento(dados):
    fig = px.bar(
        dados.sort_values("Salario_Medio", ascending=True),
        x="Salario_Medio",
        y="Departamento",
        orientation="h",
        text="Salario_Medio",
        title="Salário médio por departamento",
        color_discrete_sequence=[AZUL],
        hover_data={"Salario_Mediano": ":,.2f", "Headcount": True},
    )
    fig.update_traces(texttemplate="R$ %{x:,.0f}", textposition="outside")
    fig.update_xaxes(title_text="Salário médio (R$)")
    fig.update_yaxes(title_text="")
    return _layout_padrao(fig, altura=470)


def grafico_distribuicao_salarial(foto_ativa):
    fig = px.box(
        foto_ativa,
        x="Nivel",
        y="Salario",
        points="outliers",
        title="Distribuição salarial por nível",
        color="Nivel",
        color_discrete_map={
            "Operacional" : "#00247D",
            "Executivo" : "#EFA903",
            "Gerencial" : "#006EC7",
            "Especialista": "#FFBF31"
        }
    )
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Salário (R$)", gridcolor="rgba(0,0,0,0.08)")
    fig.update_layout(showlegend=False)
    return _layout_padrao(fig, altura=470)


def grafico_headcount_estado(dados):
    fig = px.bar(
        dados,
        x="Estado",
        y="Headcount",
        text="Headcount",
        title="Headcount por estado",
        color_discrete_sequence=[AMARELO],
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Colaboradores")
    return _layout_padrao(fig)


def grafico_headcount_unidade(dados):
    fig = px.pie(
        dados,
        names="Tipo_Unidade",
        values="Headcount",
        hole=0.52,
        title="Composição do headcount - Matriz x Filiais",
        color_discrete_sequence=[AZUL, AMARELO],
    )
    fig.update_traces(textinfo="percent+label")
    return _layout_padrao(fig)


def grafico_admissoes_desligamentos(dados):
    long = dados.melt(
        id_vars=["Mes", "Mes_Nome"],
        value_vars=["Admissoes", "Desligamentos"],
        var_name="Movimento",
        value_name="Quantidade",
    )
    fig = px.bar(
        long,
        x="Mes_Nome",
        y="Quantidade",
        color="Movimento",
        barmode="group",
        text="Quantidade",
        title="Admissões x desligamentos por mês",
        category_orders={"Mes_Nome": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]},
        color_discrete_map={"Admissoes": AZUL, "Desligamentos": AMARELO},
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Quantidade")
    return _layout_padrao(fig, altura=470)


def grafico_motivos_desligamento(dados):
    fig = px.bar(
        dados,
        x="Desligados",
        y="Motivo_Desligamento",
        text="Desligados",
        orientation="h",
        title="Principais motivos de desligamento",
        color_discrete_sequence=[AMARELO],
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(title_text="", visible=False)
    fig.update_yaxes(title_text="")
    return _layout_padrao(fig, altura=500)


def grafico_desligamentos_departamento(dados):
    fig = px.bar(
        dados,
        x="Desligados",
        y="Departamento",
        text="Desligados",
        orientation="h",
        title="Desligamentos por departamento",
        color_discrete_sequence=[AZUL],
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(title_text="Quantidade")
    fig.update_yaxes(title_text="")
    return _layout_padrao(fig)


def grafico_desempenho_recrutamento(dados):
    fig = px.scatter(
        dados,
        x="Score_Medio",
        y="Fonte_Recrutamento",
        size="Funcionarios",
        title="Desempenho por fonte de recrutamento",
        hover_data={"Score_Medio": ":.2f", "Funcionarios": True},
        color_discrete_sequence=[AZUL],
    )
    fig.update_xaxes(range=[0.8, 4.2], title_text="Score médio de desempenho (1 a 4)")
    fig.update_yaxes(title_text="")
    return _layout_padrao(fig, altura=500)
