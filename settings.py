import os
import json
from dotenv import load_dotenv

# Carrega .env apenas em ambiente local
if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()

# =========================
# CALENDAR
# =========================

CALENDAR_ID = os.getenv("CALENDAR_ID")
if not CALENDAR_ID:
    raise RuntimeError("CALENDAR_ID não definido")

# =========================
# GOOGLE CREDENTIALS
# =========================

google_credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

if google_credentials_json:
    # Caminho principal (GitHub Secrets / produção)
    try:
        GOOGLE_CREDENTIALS_DICT = json.loads(google_credentials_json)
    except json.JSONDecodeError as e:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON inválido") from e

    # Corrige quebras de linha da private_key (OBRIGATÓRIO)
    GOOGLE_CREDENTIALS_DICT["private_key"] = (
        GOOGLE_CREDENTIALS_DICT["private_key"].replace("\\n", "\n")
    )

else:
    # Fallback local (modo antigo / desenvolvimento)
    GOOGLE_CREDENTIALS_DICT = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN"),
    }
