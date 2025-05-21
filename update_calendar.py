from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from settings import GOOGLE_CREDENTIALS_DICT, CALENDAR_ID

SCOPES = ['https://www.googleapis.com/auth/calendar']

credentials = service_account.Credentials.from_service_account_info(
    GOOGLE_CREDENTIALS_DICT,
    scopes=SCOPES
)

service = build('calendar', 'v3', credentials=credentials)

calendar_id = CALENDAR_ID


def criar_ou_atualizar_evento(jogo):
    title = f"Masters Toronto: {jogo['teams']}"
    description = f"{jogo['stage']} - {jogo['evento']}\n\n🔗 {jogo['url']}"
    start_time = jogo['inicio']
    end_time = jogo['fim'] if jogo['fim'] else start_time + timedelta(hours=2)

    start_str = start_time.isoformat()
    end_str = end_time.isoformat()

    # Busca eventos existentes com o mesmo título no mesmo dia
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        q=title
    ).execute()

    events = events_result.get('items', [])

    event_body = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_str,
            "timeZone": "America/Sao_Paulo",
        },
        "end": {
            "dateTime": end_str,
            "timeZone": "America/Sao_Paulo",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 10},
            ],
        },
    }

    if events:
        # Atualiza o primeiro evento encontrado
        event_id = events[0]['id']
        updated_event = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_body
        ).execute()
        print(f"✅ Evento atualizado: {updated_event['summary']}")
    else:
        # Cria um novo evento
        created_event = service.events().insert(
            calendarId=calendar_id,
            body=event_body
        ).execute()
        print(f"✅ Evento criado: {created_event['summary']}")
