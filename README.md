# E-commerce Live Analytics — Pipeline de Eventos + Streamlit

Pipeline de dados em tempo real: um produtor gera vendas fictícias de e-commerce e as publica em um log de eventos; um dashboard em Streamlit consome esse log e exibe faturamento, total de vendas, ticket médio, faturamento por categoria e as últimas transações.

Não precisa de Docker, Kafka nem permissão de administrador: o "broker" é um arquivo local `vendas.jsonl`, onde cada linha é um evento JSON. O funcionamento imita um tópico Kafka:

- o produtor só acrescenta eventos no final do arquivo (log append-only);
- o consumidor guarda até onde já leu (o *offset*) e, a cada segundo, lê apenas os eventos novos;
- ao abrir o dashboard, a leitura começa do fim do arquivo, como `auto_offset_reset="latest"` no Kafka.

## Estrutura

- `producer.py` — grava uma venda fictícia por segundo em `vendas.jsonl`
- `consumer_dashboard.py` — dashboard Streamlit que consome o log e atualiza a cada segundo

## Como rodar

1. Instale as dependências (não precisa de administrador):

   ```bash
   pip install --user -r requirements.txt
   ```

2. Em um terminal, inicie o produtor:

   ```bash
   python producer.py
   ```

3. Em outro terminal, inicie o dashboard:

   ```bash
   streamlit run consumer_dashboard.py
   ```

O dashboard abre em http://localhost:8501. Produtor e dashboard devem ficar rodando ao mesmo tempo; o dashboard mostra apenas as vendas enviadas depois que ele foi aberto.

Se o comando `streamlit` não for encontrado após instalar com `--user`, use `python -m streamlit run consumer_dashboard.py`.
