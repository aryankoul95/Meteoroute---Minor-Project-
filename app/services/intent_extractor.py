import re
from datetime import datetime, timedelta
from typing import Optional

from app.schemas.intent import TravelIntent

HINDI_RANGE = re.compile(r"[\u0900-\u097F]")


def detect_language(text: str) -> str:
    hindi_chars = len(HINDI_RANGE.findall(text))

    if hindi_chars >= 2:
        return "Hindi"

    if re.search(r"[A-Za-z]", text):
        return "English"

    return "Unknown"


def detect_intent(text: str) -> str:
    text_lower = text.lower()

    weather_keywords = [
        "weather", "temperature", "forecast", "rain", "snow",
        "wind", "humidity", "precipitation",
        "\u092e\u094c\u0938\u092e", "\u0924\u093e\u092a\u092e\u093e\u0928",
        "\u092c\u093e\u0930\u093f\u0936", "\u092c\u0930\u094d\u092b", "\u092b\u093c\u0941\u0930\u0938\u0924"
    ]

    route_keywords = [
        "travel", "journey", "route", "go", "drive",
        "from", "destination",
        "\u091c\u093e\u0928\u093e", "\u091c\u093e\u090a\u0902",
        "\u0938\u0947", "\u0924\u0915", "\u0930\u093e\u0938\u094d\u0924\u093e"
    ]

    if any(keyword in text_lower for keyword in weather_keywords):
        return "weather_query"

    if any(keyword in text_lower for keyword in route_keywords):
        return "route_planning"

    return "unknown"

def extract_locations(text: str) -> tuple[Optional[str], Optional[str]]:
    match = re.search(
        r"\bfrom\s+(.+?)\s+to\s+(.+?)(?:\s+(?:tomorrow|today|at|on)\b|[.!?]|$)",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).strip(), match.group(2).strip()

    hindi_match = re.search(
        r"(.+?)\s+\u0938\u0947\s+(.+?)(?:\s+\u091c\u093e\u0928\u093e(?:\s+\u0939\u0948)?|[।!?]|$)",
        text,
    )

    if hindi_match:
        origin = hindi_match.group(1).strip()
        destination = hindi_match.group(2).strip()

        # Remove introductory date/time phrases before the origin.
        origin = re.sub(
            r"^.*?(?:\u0915\u0932|\u0906\u091c).*?\d{1,2}\s+\u092c\u091c\u0947\s+",
            "",
            origin,
        ).strip()

        # Remove a leading "मुझे" if it remains.
        origin = re.sub(r"^\u092e\u0941\u091d\u0947\s+", "", origin).strip()

        return origin, destination

    return None, None

def extract_departure_time(text: str) -> Optional[str]:
    now = datetime.now()

    if re.search(r"\btomorrow\b", text, re.IGNORECASE) or "\u0915\u0932" in text:
        date = now + timedelta(days=1)
        date_str = date.strftime("%Y-%m-%d")
    elif re.search(r"\btoday\b", text, re.IGNORECASE) or "\u0906\u091c" in text:
        date_str = now.strftime("%Y-%m-%d")
    else:
        date_str = None

    time_match = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)\b",
        text,
    )

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridiem = time_match.group(3).upper()

        if meridiem == "PM" and hour != 12:
            hour += 12
        elif meridiem == "AM" and hour == 12:
            hour = 0

        if date_str:
            return f"{date_str}T{hour:02d}:{minute:02d}:00"

        return f"{hour:02d}:{minute:02d}:00"

    hindi_time_match = re.search(
        r"(\d{1,2})(?::(\d{2}))?\s+\u092c\u091c\u0947",
        text,
    )

    if hindi_time_match:
        hour = int(hindi_time_match.group(1))
        minute = int(hindi_time_match.group(2) or 0)

        if "\u0936\u093e\u092e" in text or "\u0930\u093e\u0924" in text:
            if hour != 12:
                hour += 12

        if date_str:
            return f"{date_str}T{hour:02d}:{minute:02d}:00"

        return f"{hour:02d}:{minute:02d}:00"

    if date_str:
        return f"{date_str}T00:00:00"

    return None


def extract_travel_intent(text: str) -> TravelIntent:
    language = detect_language(text)
    intent = detect_intent(text)
    origin, destination = extract_locations(text)
    departure_time = extract_departure_time(text)

    return TravelIntent(
        language=language,
        intent=intent,
        origin=origin,
        destination=destination,
        departure_time=departure_time,
    )



