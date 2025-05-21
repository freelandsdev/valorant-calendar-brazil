import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import random

from settings import CALENDAR_ID
from update_calendar import criar_ou_atualizar_evento

BASE_URL = "https://www.vlr.gg"
TARGET_EVENT_NAME = "Champions Tour 2025: Masters Toronto"
END_DATE = datetime.strptime("Jun 23, 2025", "%b %d, %Y")
timezone = pytz.timezone("America/Sao_Paulo")
emojis = ["🎯", "🔥", "💥", "🎮", "🚩", "✨", "🏆", "🧨"]


def buscar_jogos():
    jogos = []
    for page in range(1, 10):
        print(f"\n🔍 Buscando página {page}...")
        url = f"{BASE_URL}/matches/?page={page}"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        blocos = soup.select(".wf-label.mod-large, .match-item")

        data_atual = None
        for bloco in blocos:
            classes = bloco.get("class", [])

            # Dentro do for onde trata datas:
            if "wf-label" in classes and "mod-large" in classes:
                data_text = bloco.get_text(strip=True).replace("Today", "").replace("Yesterday", "").strip()
                try:
                    data_atual = parser.parse(data_text)
                except Exception as e:
                    print(f"Data inválida: {data_text}")

                    data_atual = None

            # Jogo
            elif "match-item" in classes:
                if not data_atual or data_atual > END_DATE:
                    return jogos

                event_name_el = bloco.select_one(".match-item-event")
                if not event_name_el or TARGET_EVENT_NAME not in event_name_el.text:
                    continue

                link_el = bloco.get("href", "")
                time_el = bloco.select_one(".match-item-time")
                stage_el = bloco.select_one(".match-item-event-series")
                teams = bloco.select(".match-item-vs-team-name .text-of")

                if not (time_el and stage_el and len(teams) >= 2):
                    continue

                team1 = teams[0].get_text(strip=True)
                team2 = teams[1].get_text(strip=True)
                hour_str = time_el.get_text(strip=True)

                match_url = f"{BASE_URL}{link_el}"
                emoji = random.choice(emojis)

                try:
                    if "TBD" in hour_str or hour_str.strip() == "":
                        jogos.append({
                            "inicio": timezone.localize(datetime.combine(data_atual.date(), datetime.min.time())),
                            "fim": None,
                            "teams": f"{team1} vs {team2}",
                            "stage": stage_el.get_text(strip=True),
                            "evento": TARGET_EVENT_NAME,
                            "indefinido": True,
                            "url": match_url,
                            "emoji": emoji
                        })
                    else:
                        match_time = datetime.strptime(hour_str, "%I:%M %p").time()
                        start = timezone.localize(datetime.combine(data_atual.date(), match_time))
                        end = start + timedelta(hours=2)

                        jogos.append({
                            "inicio": start,
                            "fim": end,
                            "teams": f"{team1} vs {team2}",
                            "stage": stage_el.get_text(strip=True),
                            "evento": TARGET_EVENT_NAME,
                            "indefinido": False,
                            "url": match_url,
                            "emoji": emoji
                        })
                except Exception as error:
                    print(f"Erro ao processar jogo: {error}")
    return jogos


# Execução principal
jogos = buscar_jogos()

print(f"\n Total de jogos encontrados: {len(jogos)}\n")
for j in jogos:
    data_formatada = j["inicio"].strftime('%d/%m') if not j["indefinido"] else j["inicio"].strftime('%d/%m')
    status = "Horário a confirmar" if j["indefinido"] else j["inicio"].strftime('%I:%M %p')
    print(f"{j['emoji']} {data_formatada} | {status} | {j['teams']} - {j['stage']}")
    print(f"{j['url']}\n")
    criar_ou_atualizar_evento(j)
    break
