from datetime import datetime, time, timedelta

from dateutil import parser as dateparser
from googleapiclient.errors import HttpError

from input_processing.google_auth import calendar_service
from utils.logger import get_logger

logger = get_logger(__name__)


def _parse_deadline(deadline: str) -> datetime:
    """Parse a freeform deadline string into a datetime. Fallback: +7 days."""
    if not deadline or deadline.lower() in ("not specified", "n/a", "none", ""):
        return datetime.now() + timedelta(days=7)
    try:
        parsed = dateparser.parse(deadline, fuzzy=True, default=datetime.now())
        if parsed.date() < datetime.now().date():
            # If parse returned something in the past (e.g. "Friday" interpreted as last week), push to next week
            parsed = parsed + timedelta(days=7)
        return parsed
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse deadline '{deadline}': {e}")
        return datetime.now() + timedelta(days=7)


def _priority_reminder_minutes(priority: str) -> int:
    return {"high": 30, "medium": 60 * 2, "low": 60 * 24}.get(
        (priority or "").lower(), 60 * 24
    )


def push_tasks_to_calendar(
    action_items: list[dict],
    calendar_id: str = "primary",
    account: str | None = None,
) -> dict:
    """Create a Google Calendar event per task. Returns counts."""
    service = calendar_service(account)
    created = 0
    failed = 0
    errors = []

    for item in action_items:
        task = item.get("task", "").strip()
        if not task:
            continue

        start = _parse_deadline(item.get("deadline", ""))
        # Default 30-min timed event at 9am if no time component supplied
        if start.hour == 0 and start.minute == 0:
            start = datetime.combine(start.date(), time(9, 0))
        end = start + timedelta(minutes=30)

        event = {
            "summary": task,
            "description": (
                f"Priority: {item.get('priority', 'N/A')}\n"
                f"Created by AI Workflow Copilot"
            ),
            "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": _priority_reminder_minutes(item.get("priority", ""))}
                ],
            },
        }

        try:
            service.events().insert(calendarId=calendar_id, body=event).execute()
            created += 1
        except HttpError as e:
            failed += 1
            errors.append(str(e))
            logger.error(f"Failed to create event for '{task}': {e}")

    return {"created": created, "failed": failed, "errors": errors}
