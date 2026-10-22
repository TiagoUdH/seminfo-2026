import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Arquivo de log escrito pelo producer.py: cada linha é um evento JSON
ARQUIVO_EVENTOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendas.jsonl")

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Dashboard de Vendas em Tempo Real",
    page_icon="📊",
    layout="wide",
)

st.title("⚡ E-commerce Live Analytics - Pipeline de Eventos + Streamlit")
st.markdown(
    "Este painel consome dados de vendas em tempo real de um log de eventos local."
)


def tamanho_arquivo():
    return os.path.getsize(ARQUIVO_EVENTOS) if os.path.exists(ARQUIVO_EVENTOS) else 0


def ler_novos_eventos():
    # Lê apenas os bytes gravados depois da última leitura (o "offset")
    if st.session_state.offset > tamanho_arquivo():
        # O arquivo foi apagado ou recriado: volta para o início
        st.session_state.offset = 0
    if not os.path.exists(ARQUIVO_EVENTOS):
        return []

    with open(ARQUIVO_EVENTOS, "rb") as arquivo:
        arquivo.seek(st.session_state.offset)
        conteudo = arquivo.read()

    # Consome só linhas completas; uma linha ainda sendo escrita fica para a próxima
    fim = conteudo.rfind(b"\n") + 1
    st.session_state.offset += fim
    linhas = conteudo[:fim].decode("utf-8").splitlines()
    return [json.loads(linha) for linha in linhas if linha.strip()]


# Inicializa o histórico na sessão do Streamlit se não existir
if "historico_vendas" not in st.session_state:
    st.session_state.historico_vendas = []
    # Começa do fim do arquivo para pegar apenas os eventos novos
    st.session_state.offset = tamanho_arquivo()

# Bloco de execução em tempo real (atualiza a cada 1 segundo usando st.fragment)
# O layout é criado dentro do fragment: fragments não podem escrever em
# containers criados fora deles que não foram preenchidos na execução inicial
@st.fragment(run_every=1)
def atualizar_dados():
    # Layout das Métricas no Topo
    col1, col2, col3 = st.columns(3)

    st.divider()

    # Layout dos Gráficos e Tabelas
    col_grafico, col_tabela = st.columns([2, 1])
    col_grafico.subheader("📈 Faturamento Acumulado por Categoria")
    col_tabela.subheader("🚨 Últimas Transações")

    # Coleta os eventos gravados desde a última atualização
    novos_dados = ler_novos_eventos()

    if novos_dados:
        st.session_state.historico_vendas.extend(novos_dados)

    # Converte o histórico acumulado em DataFrame do Pandas
    if st.session_state.historico_vendas:
        df = pd.DataFrame(st.session_state.historico_vendas)

        # Cálculo das métricas globais
        faturamento_total = df["valor_total"].sum()
        total_transacoes = len(df)
        ticket_medio = (
            faturamento_total / total_transacoes if total_transacoes > 0 else 0
        )

        # Atualiza os componentes visuais das métricas
        col1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")
        col2.metric("Total de Vendas", f"{total_transacoes}")
        col3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

        # Gráfico de barras por categoria
        df_categoria = (
            df.groupby("categoria")["valor_total"].sum().reset_index()
        )
        fig = px.bar(
            df_categoria,
            x="categoria",
            y="valor_total",
            color="categoria",
            text_auto=".2f",
            labels={
                "categoria": "Categoria",
                "valor_total": "Faturamento (R$)",
            },
        )
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        col_grafico.plotly_chart(fig, width="stretch")

        # Tabela com as últimas 10 transações
        df_tabela = df[
            ["data_hora", "cliente", "produto", "valor_total"]
        ].tail(10)
        df_tabela.columns = ["Horário", "Cliente", "Produto", "Valor (R$)"]
        col_tabela.dataframe(
            df_tabela.iloc[::-1], width="stretch", hide_index=True
        )
    else:
        st.info(
            "Aguardando novas vendas... Certifique-se de que o produtor está rodando."
        )


# Chama a função reativa
atualizar_dados()