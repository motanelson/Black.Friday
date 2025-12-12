import time
from datetime import datetime, timedelta

def segundos_ate_ano_novo():
    agora = datetime.now()
    ano_novo = datetime(agora.year + 1, 1, 1, 0, 0, 0)
    diferenca = ano_novo - agora
    return int(diferenca.total_seconds())

# Loop que imprime a cada segundo
print("\033c\033[40;37m")
while True:
    segundos = segundos_ate_ano_novo()
    print(f"Segundos até ao Ano Novo: {segundos}")
    time.sleep(1)
