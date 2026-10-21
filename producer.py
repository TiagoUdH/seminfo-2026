import json
import random
import time
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer

fake = Faker("pt_BR")

# Inicializa o produtor Kafka conectado na porta local
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode(
        "utf-8"
    ),
)

TOPIC_NAME = "vendas-ecommerce"

PRODUTOS = [
    {"nome": "Notebook Gamer", "categoria": "Eletrônicos", "preco": 4500.0},
    {"nome": "Smartphone Pro", "categoria": "Eletrônicos", "preco": 3200.0},
    {"nome": "Cadeira Ergonômica", "categoria": "Móveis", "preco": 1200.0},
    {"nome": "Fone Bluetooth", "categoria": "Eletrônicos", "preco": 250.0},
    {"nome": "Cafeteira Elétrica", "categoria": "Eletrodomésticos", "preco": 380.0},
    {"nome": "Livro de Python", "categoria": "Livros", "preco": 85.0},
    {"nome": "Tênis Esportivo", "categoria": "Calçados", "preco": 300.0},
]

print(
    f"🚀 Produtor de eventos iniciado! Enviando dados para o tópico '{TOPIC_NAME}'..."
)

try:
    while True:
        produto_escolhido = random.choice(PRODUTOS)
        # Adiciona uma variação aleatória de quantidade (1 a 3 itens)
        quantidade = random.randint(1, 3)

        evento = {
            "id_transacao": fake.uuid4(),
            "cliente": fake.name(),
            "cidade": fake.city(),
            "produto": produto_escolhido["nome"],
            "categoria": produto_escolhido["categoria"],
            "quantidade": quantidade,
            "valor_total": produto_escolhido["preco"] * quantidade,
            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Envia o evento para o Kafka
        producer.send(TOPIC_NAME, value=evento)
        print(
            f"📦 Venda enviada: {evento['cliente']} comprou {evento['produto']} (R$ {evento['valor_total']:.2f})"
        )

        # Aguarda 1 segundo antes de enviar a próxima venda
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\n🛑 Produtor encerrado pelo usuário.")
    producer.close()