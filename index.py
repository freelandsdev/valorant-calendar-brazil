import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import random
import time

from settings import CALENDAR_ID
from update_calendar import criar_ou_atualizar_evento

BASE_URL = "https://www.vlr.gg"
EVENT_URL = f"{BASE_URL}/event/2682/vct-2026-americas-kickoff"
TARGET_EVENT_NAME = "VCT 2026: Americas Kickoff"
END_DATE = datetime.strptime("Feb 16, 2026", "%b %d, %Y")
timezone = pytz.timezone("America/Sao_Paulo")
timezone_utc = pytz.UTC
emojis = ["🎯", "🔥", "💥", "🎮", "🚩", "✨", "🏆", "🧨"]


def get_headers():
    """Retorna headers realistas para simular um navegador real"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


def buscar_jogos():
    jogos = []
    print(f"\n🔍 Buscando jogos na página do evento...")
    print(f"URL: {EVENT_URL}")
    
    # Usar sessão para manter conexão e headers consistentes
    session = requests.Session()
    session.headers.update(get_headers())
    
    try:
        # Pequeno delay aleatório para parecer mais humano (0.5 a 2 segundos)
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)
        
        res = session.get(EVENT_URL, timeout=30)
        res.raise_for_status()  # Levanta exceção se houver erro HTTP
        
        soup = BeautifulSoup(res.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao fazer requisição: {e}")
        return jogos
    
    # Buscar todos os bracket-items (partidas)
    bracket_items = soup.select(".bracket-item")
    
    print(f"📊 Encontrados {len(bracket_items)} itens no bracket\n")
    
    for item in bracket_items:
        try:
            # Extrair link da partida
            href = item.get("href", "")
            if not href:
                continue
            match_url = f"{BASE_URL}{href}"
            
            # Extrair times
            team_elements = item.select(".bracket-item-team")
            if len(team_elements) < 2:
                continue
                
            team1_el = team_elements[0].select_one(".bracket-item-team-name span")
            team2_el = team_elements[1].select_one(".bracket-item-team-name span")
            
            # Extrair nomes dos times (pode ser vazio se TBD)
            team1 = team1_el.get_text(strip=True) if team1_el else ""
            team2 = team2_el.get_text(strip=True) if team2_el else ""
            
            # Se algum time não estiver definido, usar "A DEFINIR"
            if not team1:
                team1 = "A DEFINIR"
            if not team2:
                team2 = "A DEFINIR"
            
            teams_str = f"{team1} vs {team2}"
            
            # Extrair timestamp UTC
            status_el = item.select_one(".bracket-item-status.moment-tz-convert")
            if not status_el:
                continue
                
            utc_timestamp = status_el.get("data-utc-ts")
            if not utc_timestamp:
                continue
            
            # Converter timestamp UTC para datetime
            try:
                utc_timestamp_int = int(utc_timestamp)
                start_utc = datetime.fromtimestamp(utc_timestamp_int, tz=timezone_utc)
                start_local = start_utc.astimezone(timezone)
            except (ValueError, OSError) as e:
                print(f"⚠️  Erro ao converter timestamp {utc_timestamp}: {e}")
                continue
            
            # Verificar se está dentro do período do evento
            if start_local.date() > END_DATE.date():
                continue
            
            # Extrair stage/round (procurar no bracket-col-label da coluna pai)
            bracket_col = item.find_parent(class_="bracket-col")
            stage = "Main Event"
            if bracket_col:
                label_el = bracket_col.select_one(".bracket-col-label")
                if label_el:
                    stage_text = label_el.get_text(strip=True)
                    stage = f"Main Event–{stage_text}"
            
            # Determinar se o horário está indefinido (se algum time for A DEFINIR, considerar indefinido)
            indefinido = (team1 == "A DEFINIR" or team2 == "A DEFINIR")
            
            # Calcular fim do evento (2 horas após início)
            end_local = start_local + timedelta(hours=2)
            
            emoji = random.choice(emojis)
            
            jogos.append({
                "inicio": start_local,
                "fim": end_local,
                "teams": teams_str,
                "stage": stage,
                "evento": TARGET_EVENT_NAME,
                "indefinido": indefinido,
                "url": match_url,
                "emoji": emoji
            })
            
        except Exception as error:
            print(f"⚠️  Erro ao processar partida: {error}")
            continue
    
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
