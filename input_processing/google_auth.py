import os
import pickle
import re
import shutil

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config.settings import GMAIL_CLIENT_SECRET
from utils.logger import get_logger

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

TOKENS_DIR = "tokens"
ACTIVE_FILE = os.path.join(TOKENS_DIR, "active.txt")
LEGACY_TOKEN_PATH = "token.pkl"

logger = get_logger(__name__)


def _ensure_dir():
    os.makedirs(TOKENS_DIR, exist_ok=True)


def _safe_filename(email: str) -> str:
    return re.sub(r"[^A-Za-z0-9._@-]", "_", email) + ".pkl"


def _token_path(email: str) -> str:
    return os.path.join(TOKENS_DIR, _safe_filename(email))


def _lookup_email(creds) -> str:
    service = build("oauth2", "v2", credentials=creds)
    info = service.userinfo().get().execute()
    email = info.get("email")
    if not email:
        raise RuntimeError("Could not determine account email from Google.")
    return email


def _migrate_legacy():
    """One-time migration: move token.pkl into tokens/<email>.pkl."""
    if not os.path.exists(LEGACY_TOKEN_PATH):
        return
    _ensure_dir()
    try:
        with open(LEGACY_TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)
        if not set(SCOPES).issubset(set(creds.scopes or [])):
            # Old token lacks userinfo scope — can't identify email; drop it.
            logger.info("Legacy token lacks required scopes; discarding.")
            os.remove(LEGACY_TOKEN_PATH)
            return
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        email = _lookup_email(creds)
        with open(_token_path(email), "wb") as f:
            pickle.dump(creds, f)
        if not os.path.exists(ACTIVE_FILE):
            _write_active(email)
        os.remove(LEGACY_TOKEN_PATH)
        logger.info(f"Migrated legacy token to account '{email}'.")
    except Exception as e:
        logger.warning(f"Legacy token migration failed: {e}")


def _write_active(email: str):
    _ensure_dir()
    with open(ACTIVE_FILE, "w", encoding="utf-8") as f:
        f.write(email)


def list_accounts() -> list[str]:
    _migrate_legacy()
    if not os.path.isdir(TOKENS_DIR):
        return []
    accounts = []
    for name in os.listdir(TOKENS_DIR):
        if not name.endswith(".pkl"):
            continue
        path = os.path.join(TOKENS_DIR, name)
        try:
            with open(path, "rb") as f:
                creds = pickle.load(f)
            # Prefer creds.id_token email if available; otherwise derive from filename.
            email = getattr(creds, "_email", None) or name[:-4]
            accounts.append(email)
        except Exception as e:
            logger.warning(f"Skipping unreadable token {name}: {e}")
    return sorted(accounts)


def get_active_account() -> str | None:
    _migrate_legacy()
    if not os.path.exists(ACTIVE_FILE):
        accounts = list_accounts()
        return accounts[0] if accounts else None
    with open(ACTIVE_FILE, "r", encoding="utf-8") as f:
        email = f.read().strip()
    return email or None


def set_active_account(email: str):
    if not os.path.exists(_token_path(email)):
        raise ValueError(f"No stored credentials for '{email}'.")
    _write_active(email)


def remove_account(email: str):
    path = _token_path(email)
    if os.path.exists(path):
        os.remove(path)
    if get_active_account() == email:
        remaining = list_accounts()
        if remaining:
            _write_active(remaining[0])
        elif os.path.exists(ACTIVE_FILE):
            os.remove(ACTIVE_FILE)


def add_account() -> str:
    """Launch the OAuth flow; store and activate the new account. Returns email."""
    if not os.path.exists(GMAIL_CLIENT_SECRET):
        raise FileNotFoundError(
            f"Google client secret not found: {GMAIL_CLIENT_SECRET}\n"
            "Set GMAIL_CLIENT_SECRET in your .env file."
        )
    flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CLIENT_SECRET, SCOPES)
    creds = flow.run_local_server(port=0)
    email = _lookup_email(creds)
    _ensure_dir()
    with open(_token_path(email), "wb") as f:
        pickle.dump(creds, f)
    _write_active(email)
    logger.info(f"Added Google account '{email}'.")
    return email


def _load(email: str):
    path = _token_path(email)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        creds = pickle.load(f)
    if not set(SCOPES).issubset(set(creds.scopes or [])):
        logger.info(f"Scope mismatch for '{email}' — re-authenticating.")
        return None
    return creds


def _save(email: str, creds):
    _ensure_dir()
    with open(_token_path(email), "wb") as f:
        pickle.dump(creds, f)


def _credentials_for(email: str | None):
    _migrate_legacy()
    email = email or get_active_account()
    if not email:
        # No stored account yet — run the flow, which also activates it.
        email = add_account()
        return _load(email), email

    creds = _load(email)
    if creds and creds.valid:
        return creds, email
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save(email, creds)
            return creds, email
        except Exception as e:
            logger.warning(f"Refresh failed for '{email}': {e}")

    # Fall through: re-auth and keep same active slot.
    new_email = add_account()
    return _load(new_email), new_email


def gmail_service(account: str | None = None):
    creds, _ = _credentials_for(account)
    return build("gmail", "v1", credentials=creds)


def calendar_service(account: str | None = None):
    creds, _ = _credentials_for(account)
    return build("calendar", "v3", credentials=creds)
