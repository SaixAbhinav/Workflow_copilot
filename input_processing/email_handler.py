import base64

from googleapiclient.errors import HttpError

from input_processing.google_auth import gmail_service
from utils.logger import get_logger

logger = get_logger(__name__)


def get_latest_emails(
    max_results: int = 5,
    account: str | None = None,
    page_token: str | None = None,
    query: str | None = None,
) -> dict:
    """Return a page of emails.

    `query` accepts Gmail search syntax (e.g. "from:boss@co is:unread").
    Returns: {"emails": [...], "next_page_token": str | None}
    """
    try:
        service = gmail_service(account)
        kwargs = {"userId": "me", "maxResults": max_results}
        if page_token:
            kwargs["pageToken"] = page_token
        if query:
            kwargs["q"] = query
        results = service.users().messages().list(**kwargs).execute()
    except HttpError as e:
        logger.error(f"Gmail API error: {e}")
        raise RuntimeError(f"Failed to fetch emails: {e}")

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        try:
            msg_data = service.users().messages().get(
                userId="me", id=msg["id"], format="full"
            ).execute()

            headers = msg_data["payload"]["headers"]
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "")
            body = _extract_body(msg_data["payload"])

            emails.append({"sender": sender, "subject": subject, "body": body})
        except Exception as e:
            logger.warning(f"Skipping message {msg['id']}: {e}")

    return {"emails": emails, "next_page_token": results.get("nextPageToken")}


def _extract_body(payload: dict) -> str:
    parts = payload.get("parts", [])
    if parts:
        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return ""
