import json
import os
import random
import time
from datetime import datetime
from faker import Faker

fake = Faker("pt_BR")

# Arquivo de log que faz o papel do tópico Kafka: cada linha é um evento JSON
ARQUIVO_EVENTOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendas.jsonl")

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
    f"🚀 Produtor de eventos iniciado! Enviando dados para '{ARQUIVO_EVENTOS}'..."
)

# Abre o arquivo em modo append: novos eventos sempre vão para o final
producer = open(ARQUIVO_EVENTOS, "a", encoding="utf-8")

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

        # Publica o evento como uma linha JSON e força a gravação no disco
        # para o consumidor enxergar imediatamente
        producer.write(json.dumps(evento, ensure_ascii=False) + "\n")
        producer.flush()
        print(
            f"📦 Venda enviada: {evento['cliente']} comprou {evento['produto']} (R$ {evento['valor_total']:.2f})"
        )

        # Aguarda 1 segundo antes de enviar a próxima venda
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\n🛑 Produtor encerrado pelo usuário.")
    producer.close()