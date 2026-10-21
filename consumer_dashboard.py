import json
import pandas as pd
import plotly.express as px
import streamlit as st
from kafka import KafkaConsumer

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Dashboard de Vendas em Tempo Real",
    page_icon="📊",
    layout="wide",
)

st.title("⚡ E-commerce Live Analytics - Pipeline Kafka + Streamlit")
st.markdown(
    "Este painel consome dados de vendas em tempo real de um cluster Apache Kafka."
)


# Função para criar o consumidor Kafka com cache para não reconectar a cada reload
@st.cache_resource
def get_kafka_consumer():
    consumer = KafkaConsumer(
        "vendas-ecommerce",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest",  # Pega apenas as mensagens novas
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )
    return consumer


consumer = get_kafka_consumer()

# Inicializa o histórico na sessão do Streamlit se não existir
if "historico_vendas" not in st.session_state:
    st.session_state.historico_vendas = []

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

    # Coleta as mensagens já disponíveis no Kafka sem bloquear a renderização
    # (iterar o consumer só retorna após consumer_timeout_ms sem mensagens,
    # o que nunca acontece com o produtor enviando 1 venda por segundo)
    novos_dados = []
    lotes = consumer.poll(timeout_ms=200, max_records=100)
    for mensagens in lotes.values():
        novos_dados.extend(message.value for message in mensagens)

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
        col_grafico.plotly_chart(fig, use_container_width=True)

        # Tabela com as últimas 10 transações
        df_tabela = df[
            ["data_hora", "cliente", "produto", "valor_total"]
        ].tail(10)
        df_tabela.columns = ["Horário", "Cliente", "Produto", "Valor (R$)"]
        col_tabela.dataframe(
            df_tabela.iloc[::-1], use_container_width=True, hide_index=True
        )
    else:
        st.info(
            "Aguardando dados do Kafka... Certifique-se de que o produtor está rodando."
        )


# Chama a função reativa
atualizar_dados()