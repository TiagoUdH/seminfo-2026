# E-commerce Live Analytics — Kafka + Streamlit

Pipeline de dados em tempo real: um produtor gera vendas fictícias de e-commerce e as publica em um tópico do Apache Kafka; um dashboard em Streamlit consome esse tópico e exibe faturamento, total de vendas, ticket médio, faturamento por categoria e as últimas transações.

## Estrutura

- `docker-compose.yml` — sobe Zookeeper e Kafka (porta `9092`)
- `producer.py` — envia uma venda fictícia por segundo para o tópico `vendas-ecommerce`
- `consumer_dashboard.py` — dashboard Streamlit que consome o tópico e atualiza a cada segundo

## Como rodar

1. Suba o Kafka:

   ```bash
   docker compose up -d
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Em um terminal, inicie o produtor:

   ```bash
   python producer.py
   ```

4. Em outro terminal, inicie o dashboard:

   ```bash
   streamlit run consumer_dashboard.py
   ```

O dashboard abre em http://localhost:8501. Produtor e dashboard devem ficar rodando ao mesmo tempo; o dashboard mostra apenas as vendas enviadas depois que ele foi aberto.
