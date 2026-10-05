
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

destino = Path(__file__).parent / "dados" / "exemplo.csv"
destino.parent.mkdir(exist_ok=True)
agora = datetime.now()

with open(destino, "w", newline="", encoding="utf-8") as f:
    escritor = csv.writer(f, delimiter=";")
    escritor.writerow(["remessa", "tipo", "peso_kg", "criada_em", "status"])
    for i in range(14):
        criada = agora - timedelta(minutes=random.uniform(0, 24))
        tipo = "RETIRA_FACIL" if random.random() < 0.75 else "NORMAL"
        peso = f"{random.uniform(15, 650):.1f}".replace(".", ",")
        status = "separado" if random.random() < 0.15 else "pendente"
        escritor.writerow([80000001 + i, tipo, peso, f"{criada:%d/%m/%Y %H:%M:%S}", status])

print(f"Arquivo de exemplo criado em {destino}")
