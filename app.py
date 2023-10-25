# ----- Analise dos dados -----#
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# ----- Geração de graficos ----- #
import plotly.io as pio
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# servidor
from flask import Flask, jsonify
from flask_cors import CORS  # Importe a extensão Flask-CORS

# ----- Intregrando os Datasets ----- #
tb_desmatamento = pd.read_csv("../base_de_dados/Desmatamento.csv", delimiter=";", header=0, index_col=False,
                              decimal=',', low_memory=False)
tb_meteorologico = pd.read_csv("../base_de_dados/Meteorologico.csv", delimiter=";", header=0, index_col=False,
                               decimal=',', low_memory=False)

# Colocando tipo de dados por coluna desmatamento
tb_desmatamento = tb_desmatamento.astype({'ano': int,
                                          'estado': str,
                                          'area': int,
                                          'desmatado': float,
                                          'incremento': float,
                                          'floresta': float,
                                          'nuvem': float,
                                          'nao_observado': float,
                                          'nao_floresta': float,
                                          'hidrografia': float}).drop(
    columns=["nao_observado", "nao_floresta", "hidrografia"])

# --------- Fazendo analise de dados meteorologicos ---------#

# Formatando o tipo de data para pegamos só o ano.
tb_meteorologico["data"] = tb_meteorologico["data"].apply(lambda x: int(str(x)[:4]))
# Pegando dado por ano que seja igual ou acima de 2008
tb_meteorologico = tb_meteorologico.loc[tb_meteorologico['data'] >= 2010]
# ordenando dataset
tb_meteorologico = tb_meteorologico.sort_values(by=['data', 'estado'])
# renomeando colunas
tb_meteorologico = tb_meteorologico.rename(columns={"data": "ano"})

# calulando a media da precipitação por ano e estado
tb_meteorologico = tb_meteorologico.groupby(['estado', 'ano'])['precipitacao_total'].mean().reset_index()

tb_meteorologico.loc[tb_meteorologico["estado"] == "Mato-Grosso", ["estado"]] = "Mato Grosso"

# ----- Analise Desmatamento ----- #
# Pegando dado por ano que seja igual ou acima de 2008
tb_desmatamento_geral = tb_desmatamento.loc[tb_desmatamento['ano'] >= 2010]

# Organizando o Dataset por Estado e Ano
tb_desmatamento_geral = tb_desmatamento_geral[["ano", "estado", "incremento"]].groupby(["ano", "estado"]).sum()

tb_desmatamento_geral.reset_index(inplace=True)

# Merge entre os Datasets para fazer a correlação
tb_correlacao = pd.merge(tb_desmatamento_geral, tb_meteorologico)


# Função que Gera os Graficos de Correlação
def gera_graficos(df, t, xt, y1t, y2t):
    # Criar um MinMaxScaler
    scaler = MinMaxScaler()

    # Normalizar as colunas 'precipitacao_total' e 'incremento'
    df[['precipitacao_total', 'incremento']] = scaler.fit_transform(df[['precipitacao_total', 'incremento']])

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Adicionando as linhas ao gráfico, com as escalas de cada eixo y definidas
    fig.add_trace(
        go.Scatter(x=df['ano'], y=df['incremento'], name=y1t, line=dict(color='green'))
    )

    fig.add_trace(
        go.Scatter(x=df['ano'], y=df['precipitacao_total'], name=y2t, line=dict(color='blue'))
    )

    # Adicionando título e legenda aos eixos
    fig.update_layout(
        title=t,
        xaxis_title=xt,
        yaxis_title=y1t,
        yaxis2_title=y2t,
    )

    # Exibindo gráfico
    # fig.show()

    return fig.to_json()


# Instanciando servidor
app = Flask(__name__)
CORS(app)  # Configure o aplicativo Flask para usar o Flask-CORS


# GRAFICOS DE CORRELAÇÃO
@app.route("/")
def general_graph():
    # ----- Analise conjunta ----- #

    # Fazendo a Correlação Geral dos dados
    tb_correlacao_geral = tb_correlacao[["ano", "incremento", "precipitacao_total"]].groupby(["ano"]).sum()
    tb_correlacao_geral.reset_index(inplace=True)
    # ----- Grafico de Correlação Geral entre os Datasets ----- #
    fig = gera_graficos(tb_correlacao_geral, "Correlação entre Desmatamento e Precipitação Geral", "Ano",
                        "Desmatamento (Área (km²)", "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


@app.route("/acre")
def acre_graph():
    fig = gera_graficos(pd.DataFrame(tb_correlacao.loc[tb_correlacao['estado'] == "Acre"]),
                        "Correlação entre Desmatamento e Precipitação no Estado Acre", "Ano",
                        "Desmatamento (Área (km²)",
                        "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


@app.route("/amapa")
def amapa_graph():
    fig = gera_graficos(pd.DataFrame(tb_correlacao.loc[tb_correlacao['estado'] == "Amapa"]),
                        "Correlação entre Desmatamento e Precipitação no Estado Amapa", "Ano",
                        "Desmatamento (Área (km²)", "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


@app.route("/amazonas")
def amazonas_graph():
    fig = gera_graficos(pd.DataFrame(tb_correlacao.loc[tb_correlacao['estado'] == "Amazonas"]),
                        "Correlação entre Desmatamento e Precipitação no Estado Amazonas", "Ano",
                        "Desmatamento (Área (km²)", "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


@app.route("/maranhao")
def maranhao_graph():
    fig = gera_graficos(pd.DataFrame(tb_correlacao.loc[tb_correlacao['estado'] == "Maranhao"]),
                        "Correlação entre Desmatamento e Precipitação no Estado Maranhao", "Ano",
                        "Desmatamento (Área (km²)", "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


@app.route("/mato_grosso")
def mato_grosso_graph():
    fig = gera_graficos(pd.DataFrame(tb_correlacao.loc[tb_correlacao['estado'] == "Mato Grosso"]),
                        "Correlação entre Desmatamento e Precipitação no Estado Mato-Grosso", "Ano",
                        "Desmatamento (Área (km²)", "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


@app.route("/para")
def para_graph():
    fig = gera_graficos(pd.DataFrame(tb_correlacao.loc[tb_correlacao['estado'] == "Para"]),
                        "Correlação entre Desmatamento e Precipitação no Estado Para", "Ano",
                        "Desmatamento (Área (km²)", "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


@app.route("/rondonia")
def rondonia_graph():
    fig = gera_graficos(pd.DataFrame(tb_correlacao.loc[tb_correlacao['estado'] == "Rondonia"]),
                        "Correlação entre Desmatamento e Precipitação no Estado Rondonia", "Ano",
                        "Desmatamento (Área (km²)", "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


@app.route("/tocantins")
def tocantins_graph():
    fig = gera_graficos(pd.DataFrame(tb_correlacao.loc[tb_correlacao['estado'] == "Tocantins"]),
                        "Correlação entre Desmatamento e Precipitação no Estado Tocantins", "Ano",
                        "Desmatamento (Área (km²)", "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


@app.route("/roraima")
def roraima_graph():
    fig = gera_graficos(pd.DataFrame(tb_correlacao.loc[tb_correlacao['estado'] == "Roraima"]),
                        "Correlação entre Desmatamento e Precipitação no Estado Roraima", "Ano",
                        "Desmatamento (Área (km²)", "Precipitação (mm)")
    return fig, 200, {'Content-Type': 'application/json'}


# GRAFICOS DE DESMATAMENTO
@app.route("/desmatamentoTotal")
def desmatamento_valores_totais_graph():
    tb_desmatamento_valores_totais = tb_desmatamento_geral[["estado", "incremento"]].groupby(["estado"]).sum()
    tb_desmatamento_valores_totais.reset_index(inplace=True)
    fig = px.bar(tb_desmatamento_valores_totais, x='estado', y='incremento', color="estado",
                 labels={'desmatado': 'Área Desmatada (km²)', 'estado': 'Estados'},
                 title='Área Amazônica já Desmatada por Estado (km²)')

    return fig.to_json(), 200, {'Content-Type': 'application/json'}


@app.route("/desmatamentoAnoTotal")
def desmatamento_valores_totais_ano_graph():
    fig = px.bar(tb_desmatamento_geral, x='ano', y='incremento', color="estado",
                 labels={'desmatado': 'Área Desmatada (km²)', 'estado': 'Estados', 'ano': 'Anos'},
                 title='Área Amazônica Geral Desmatada por Ano (km²)')

    return fig.to_json(), 200, {'Content-Type': 'application/json'}


# GRAFICOS DE CHUVA

@app.route("/mediaPrecipitacaoAno")
def media_precipitacao_total_ano_graph():
    # ----- Grafico da precipitação por estado ----- #
    tb_pluviometrico = tb_meteorologico.copy()
    labels = {'precipitacao_total': 'Pricipitação média (mm)', 'estado': 'Estados', 'ano': 'Anos'}
    title = 'Média de chuvas por ano'
    fig = px.line(tb_pluviometrico, x="ano", y="precipitacao_total", color="estado", labels=labels, title=title)

    return fig.to_json(), 200, {'Content-Type': 'application/json'}


@app.route("/precipitacaoTotalAno")
def precipitacao_total_ano_graph():
    # ----- Grafico da precipitação por estado ----- #
    tb_pluviometrico = tb_meteorologico.copy()
    labels = {'precipitacao_total': 'Pricipitação total (mm)', 'estado': 'Estados', 'ano': 'Anos'}
    title = 'Quantidade de chuva por ano'

    tb_pluviometrico = tb_pluviometrico.groupby(['ano'])['precipitacao_total'].sum().reset_index()
    fig = px.bar(tb_pluviometrico, x='ano', y='precipitacao_total', title=title, labels=labels)

    return fig.to_json(), 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(debug=True)