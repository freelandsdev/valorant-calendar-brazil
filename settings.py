from dotenv import load_dotenv
import os
import json

load_dotenv()

CALENDAR_ID = os.getenv("CALENDAR_ID")

# Lê as credenciais do JSON (do secret GOOGLE_SERVICE_ACCOUNT_JSON)
google_credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

if google_credentials_json:
    # Faz parse do JSON string
    GOOGLE_CREDENTIALS_DICT = json.loads(google_credentials_json)
    # Garante que a private_key tenha quebras de linha corretas
    if "private_key" in GOOGLE_CREDENTIALS_DICT:
        GOOGLE_CREDENTIALS_DICT["private_key"] = GOOGLE_CREDENTIALS_DICT["private_key"].replace('\\n', '\n')
else:
    # Fallback para variáveis individuais (compatibilidade local)
    GOOGLE_CREDENTIALS_DICT = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n'),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN")
    }