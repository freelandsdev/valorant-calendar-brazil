from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from settings import GOOGLE_CREDENTIALS_DICT, CALENDAR_ID

SCOPES = ['https://www.googleapis.com/auth/calendar']

credentials = service_account.Credentials.from_service_account_info(
    GOOGLE_CREDENTIALS_DICT,
    scopes=SCOPES
)

service = build('calendar', 'v3', credentials=credentials)

calendar_id = CALENDAR_ID


def validar_credenciais():
    """
    Valida se as credenciais têm acesso ao calendário.
    Retorna True se válido, False caso contrário.
    """
    try:
        # Tenta acessar o calendário para verificar se existe
        calendar = service.calendars().get(calendarId=calendar_id).execute()
        print(f"✅ Calendário encontrado: {calendar.get('summary', 'Sem nome')}")
        
        # Tenta listar eventos (teste básico de acesso)
        service.events().list(calendarId=calendar_id, maxResults=1).execute()
        print("✅ Acesso ao calendário confirmado")
        
        # Nota: Permissão de escrita será testada ao criar o primeiro evento
        # Isso evita criar eventos de teste desnecessários
        
        return True
    except HttpError as e:
        if e.resp.status == 403:
            print(f"❌ ERRO: Service Account não tem acesso ao calendário")
            print(f"   Detalhes: {e.error_details if hasattr(e, 'error_details') else str(e)}")
            print("\n📋 Para corrigir:")
            print("   1. Acesse https://calendar.google.com")
            print("   2. Vá em Configurações > Configurações do calendário")
            print("   3. Encontre seu calendário e clique nele")
            print("   4. Na seção 'Compartilhar com pessoas específicas'")
            print(f"   5. Clique em 'Adicionar pessoas' e adicione:")
            print(f"      📧 {GOOGLE_CREDENTIALS_DICT.get('client_email', 'N/A')}")
            print("   6. Selecione permissão: 'Fazer alterações em eventos'")
            print("   7. Clique em 'Enviar'")
            return False
        elif e.resp.status == 404:
            print(f"❌ ERRO: Calendário não encontrado")
            print(f"   Calendar ID: {calendar_id}")
            print("   Verifique se o CALENDAR_ID está correto")
            return False
        else:
            print(f"❌ ERRO ao validar credenciais: {e}")
            return False
    except Exception as e:
        print(f"❌ ERRO inesperado ao validar credenciais: {e}")
        return False


def criar_ou_atualizar_evento(jogo):
    title = f"VCT 2026: Americas Kickoff - {jogo['teams']}"
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

    try:
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
    except HttpError as e:
        if e.resp.status == 403:
            print(f"❌ ERRO ao criar/atualizar evento: Sem permissão de escrita")
            print(f"   Verifique se o service account tem acesso ao calendário")
            raise
        else:
            print(f"❌ ERRO ao criar/atualizar evento: {e}")
            raise
