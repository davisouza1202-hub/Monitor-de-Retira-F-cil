#!/usr/bin/env python3
Monitor de Retira Fácil: mostra o tempo restante de cada remessa pendente.


import argparse
import csv
import os
import time
from datetime import datetime, timedelta

VERDE, AMARELO, VERMELHO = "\033[92m", "\033[93m", "\033[91m"
NEGRITO, RESET = "\033[1m", "\033[0m"
FORMATOS_DATA = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M")
STATUS_FINALIZADOS = {"separado", "concluido", "concluído", "cancelado"}


def converter_data(texto):
    for formato in FORMATOS_DATA:
        try:
            return datetime.strptime(texto.strip(), formato)
        except ValueError:
            continue
    raise ValueError(f"data inválida: {texto!r}")


def converter_peso(texto):
    texto = texto.strip()
    if "," in texto:  # formato brasileiro: 1.250,5
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


def ler_remessas(caminho, tipo, limite_kg, sla_min):
    """Retorna (remessas pendentes elegíveis, quantidade de linhas ignoradas)."""
    with open(caminho, newline="", encoding="utf-8-sig") as f:
        primeira = f.readline()
        f.seek(0)
        delimitador = ";" if primeira.count(";") > primeira.count(",") else ","
        linhas = list(csv.DictReader(f, delimiter=delimitador))

    remessas, ignoradas = [], 0
    for linha in linhas:
        try:
            dados = {k.strip().lower(): v for k, v in linha.items()}
            if dados["tipo"].strip().upper() != tipo:
                continue
            if dados["status"].strip().lower() in STATUS_FINALIZADOS:
                continue
            peso = converter_peso(dados["peso_kg"])
            if peso > limite_kg:
                continue
            criada = converter_data(dados["criada_em"])
        except (KeyError, ValueError, AttributeError):
            ignoradas += 1
            continue
        remessas.append({
            "remessa": dados["remessa"].strip(),
            "peso": peso,
            "prazo": criada + timedelta(minutes=sla_min),
        })
    return sorted(remessas, key=lambda r: r["prazo"]), ignoradas


def formatar_tempo(segundos):
    sinal = "-" if segundos < 0 else ""
    minutos, seg = divmod(abs(int(segundos)), 60)
    return f"{sinal}{minutos:02d}:{seg:02d}"


def classificar(segundos):
    if segundos < 0:
        return VERMELHO + NEGRITO, "ATRASADA"
    if segundos <= 5 * 60:
        return VERMELHO, "CRÍTICA"
    if segundos <= 10 * 60:
        return AMARELO, "ATENÇÃO"
    return VERDE, "NO PRAZO"


def desenhar(remessas, ignoradas, args):
    agora = datetime.now()
    print(f"{NEGRITO}RETIRA FÁCIL — até {args.limite_kg:g} kg — SLA {args.sla_min} min{RESET}")
    print(f"Atualizado às {agora:%H:%M:%S}\n")
    print(f"{'REMESSA':<14}{'PESO (kg)':>10}{'PRAZO':>10}{'RESTANTE':>11}   SITUAÇÃO")
    print("-" * 58)

    atrasadas = 0
    for r in remessas:
        restante = (r["prazo"] - agora).total_seconds()
        cor, situacao = classificar(restante)
        atrasadas += restante < 0
        prazo = f"{r['prazo']:%H:%M:%S}"
        print(f"{cor}{r['remessa']:<14}{r['peso']:>10.1f}{prazo:>10}"
              f"{formatar_tempo(restante):>11}   {situacao}{RESET}")

    if not remessas:
        print("Nenhuma remessa de retira fácil pendente. 👍")
    print(f"\nPendentes: {len(remessas)}   Atrasadas: {atrasadas}")
    if ignoradas:
        print(f"Atenção: {ignoradas} linha(s) ignorada(s) por dados inválidos.")


def main():
    parser = argparse.ArgumentParser(description="Contagem regressiva para retira fácil.")
    parser.add_argument("arquivo", nargs="?", default="dados/exemplo.csv", help="CSV exportado com as remessas")
    parser.add_argument("--tipo", default="RETIRA_FACIL", help="valor da coluna 'tipo' a monitorar")
    parser.add_argument("--limite-kg", type=float, default=400, help="peso máximo (padrão: 400)")
    parser.add_argument("--sla-min", type=int, default=20, help="prazo em minutos (padrão: 20)")
    parser.add_argument("--intervalo", type=float, default=1, help="segundos entre atualizações")
    parser.add_argument("--uma-vez", action="store_true", help="mostra uma vez e sai")
    args = parser.parse_args()

    os.system("")  
    try:
        while True:
            try:
                remessas, ignoradas = ler_remessas(args.arquivo, args.tipo.upper(), args.limite_kg, args.sla_min)
            except FileNotFoundError:
                raise SystemExit(f"Arquivo não encontrado: {args.arquivo}")
            if not args.uma_vez:
                print("\033[H\033[J", end="")
            desenhar(remessas, ignoradas, args)
            if args.uma_vez:
                break
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        print("\nMonitor encerrado.")


if __name__ == "__main__":
    main()
