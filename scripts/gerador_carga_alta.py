#!/usr/bin/env python3
"""
Gerador de Carga Alta (10.000+ registros) para Benchmark e Testes EXPLAIN (B4)
Injeta grande massa de transações e parcelas para medição de tempos reais de execução.
"""

import mysql.connector
import random
from datetime import datetime, timedelta

def main():
    print("Injetando 10.000 transações sintéticas para benchmark EXPLAIN ANALYZE...")
    conn = mysql.connector.connect(host="localhost", port=3306, user="root", password="banco_secret", database="sistema_bancario")
    cursor = conn.cursor()

    tipos = ["PIX", "TED", "TRANSFERENCIA", "PAGAMENTO_BOLETO", "SAQUE", "DEPOSITO"]
    start_date = datetime(2023, 1, 1, 0, 0, 0)
    batch = []
    
    for i in range(1, 10001):
        c_origem = f"100{((i - 1) % 45) + 1:02d}-X"
        dest_idx = ((i * 3) % 45) + 1
        c_destino = f"100{dest_idx:02d}-X" if i % 4 != 0 else None
        tipo = tipos[i % len(tipos)]
        vlr = round(random.uniform(10.0, 15000.0), 2)
        dt = start_date + timedelta(minutes=i * 5)
        
        batch.append((c_origem, c_destino, tipo, vlr, dt))

        if len(batch) >= 1000:
            cursor.executemany(
                "INSERT INTO transacao (numero_conta_origem, numero_conta_destino, tipo, valor, data_hora) VALUES (%s, %s, %s, %s, %s);",
                batch
            )
            conn.commit()
            batch = []
            print(f"  {i} transações inseridas...")

    cursor.close()
    conn.close()
    print("Carga de 10.000 transações concluída com sucesso!")

if __name__ == "__main__":
    main()
