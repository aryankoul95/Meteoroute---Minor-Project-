import os
import re
from datetime import datetime, timedelta
from typing import Optional

from google import genai
from google.genai import types

from app.schemas.intent import TravelIntent


# =========================================================
# RULE-BASED HELPERS
# =========================================================

def detect_language(text: str) -> str:
    devanagari_count = len(
        re.findall(r"[\u0900-\u097F]", text)
    )

    english_count = len(
        re.findall(r"[A-Za-z]", text)
    )

    if devanagari_count >= 2:
        return "Hindi"

    if english_count > 0:
        return "English"

    return "Unknown"


def detect_intent(text: str) -> str:
    text_lower = text.lower()

    weather_keywords = [
        "weather",
        "temperature",
        "rain",
        "forecast",
        "wind",
        "snow",
        "बारिश",
        "मौसम",
        "तापमान",
        "हवा",
    ]

    route_keywords = [
        "travel",
        "journey",
        "route",
        "go",
        "drive",
        "trip",
        "यात्रा",
        "जाना",
        "रास्ता",
        "सफर",
    ]

    if any(
        keyword in text_lower
        for keyword in weather_keywords
    ):
        return "weather_query"

    if any(
        keyword in text_lower
        for keyword in route_keywords
    ):
        return "route_planning"

    return "unknown"


def extract_english_locations(text: str):
    patterns = [
        r"from\s+(.+?)\s+to\s+(.+?)(?:\s+tomorrow|\s+today|\s+at\s+|\s+on\s+|$)",
        r"from\s+(.+?)\s+to\s+(.+)$",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            origin = match.group(1).strip(" ,.")
            destination = match.group(2).strip(" ,.")

            return origin, destination

    return None, None


def extract_hindi_locations(text: str):
    patterns = [
        r"(.+?)\s+से\s+(.+?)\s+जाना",
        r"(.+?)\s+से\s+(.+?)\s+जाना\s+है",
        r"(.+?)\s+से\s+(.+?)\s+जाऊँ",
        r"(.+?)\s+से\s+(.+?)\s+जाना चाहता",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
        )

        if match:
            origin = match.group(1).strip(" ,.")
            destination = match.group(2).strip(" ,.")

            return origin, destination

    return None, None


def extract_departure_time(
    text: str,
) -> Optional[str]:

    now = datetime.now()

    if re.search(
        r"\btomorrow\b",
        text,
        re.IGNORECASE,
    ):
        departure_date = (
            now.date() + timedelta(days=1)
        )

    elif re.search(
        r"\btoday\b",
        text,
        re.IGNORECASE,
    ):
        departure_date = now.date()

    elif "कल" in text:
        departure_date = (
            now.date() + timedelta(days=1)
        )

    elif "आज" in text:
        departure_date = now.date()

    else:
        departure_date = None

    time_match = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM)\b",
        text,
        re.IGNORECASE,
    )

    if time_match and departure_date:

        hour = int(time_match.group(1))

        minute = int(
            time_match.group(2) or 0
        )

        meridiem = (
            time_match.group(3).upper()
        )

        if meridiem == "PM" and hour != 12:
            hour += 12

        if meridiem == "AM" and hour == 12:
            hour = 0

        return datetime.combine(
            departure_date,
            datetime.min.time().replace(
                hour=hour,
                minute=minute,
            ),
        ).isoformat()

    return None


# =========================================================
# RULE-BASED INTENT EXTRACTION
# =========================================================

def extract_travel_intent(
    text: str,
) -> TravelIntent:

    language = detect_language(text)

    intent = detect_intent(text)

    origin = None
    destination = None

    if language == "Hindi":

        origin, destination = (
            extract_hindi_locations(text)
        )

    elif language == "English":

        origin, destination = (
            extract_english_locations(text)
        )

    departure_time = extract_departure_time(text)

    return TravelIntent(
        language=language,
        intent=intent,
        origin=origin,
        destination=destination,
        departure_time=departure_time,
    )


# =========================================================
# GEMINI FUNCTION DECLARATION
# =========================================================

TRAVEL_INTENT_TOOL = {
    "name": "extract_travel_intent",
    "description": (
        "Extract structured travel intent from an "
        "English or Hindi travel query. Identify "
        "the language, intent, origin, destination, "
        "and departure time."
    ),
    "parameters": {
        "type": "object",
        "properties": {

            "language": {
                "type": "string",
                "enum": [
                    "English",
                    "Hindi",
                    "Unknown",
                ],
                "description": (
                    "Language used in the user's query."
                ),
            },

            "intent": {
                "type": "string",
                "enum": [
                    "route_planning",
                    "weather_query",
                    "unknown",
                ],
                "description": (
                    "Primary intent of the user's query."
                ),
            },

            "origin": {
                "type": "string",
                "description": (
                    "Starting location. "
                    "Use an empty string if "
                    "it cannot be identified."
                ),
            },

            "destination": {
                "type": "string",
                "description": (
                    "Destination location. "
                    "Use an empty string if "
                    "it cannot be identified."
                ),
            },

            "departure_time": {
                "type": "string",
                "description": (
                    "Departure time in ISO 8601 format "
                    "when it can be determined. "
                    "Use an empty string otherwise."
                ),
            },
        },

        "required": [
            "language",
            "intent",
            "origin",
            "destination",
            "departure_time",
        ],
    },
}


# =========================================================
# GEMINI LLM FUNCTION CALLING
# =========================================================

async def extract_travel_intent_llm(
    text: str,
) -> TravelIntent:

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=api_key
    )

    tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=TRAVEL_INTENT_TOOL["name"],
                description=TRAVEL_INTENT_TOOL[
                    "description"
                ],
                parameters=TRAVEL_INTENT_TOOL[
                    "parameters"
                ],
            )
        ]
    )

    config = types.GenerateContentConfig(
        tools=[tool]
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=(
            "You are the intent extraction component "
            "of MeteoRoute.\n\n"
            "Extract structured travel information "
            "from the user's query.\n"
            "Support both English and Hindi.\n"
            "Do not invent locations or travel details.\n"
            "If information is missing, use an empty "
            "string.\n"
            "For departure_time, use ISO 8601 format "
            "when a date and time are available.\n\n"
            f"User query:\n{text}"
        ),
        config=config,
    )

    function_call = None

    for candidate in response.candidates:

        for part in candidate.content.parts:

            if part.function_call:

                if (
                    part.function_call.name
                    == "extract_travel_intent"
                ):
                    function_call = (
                        part.function_call
                    )

                    break

        if function_call:
            break

    if function_call is None:

        raise RuntimeError(
            "Gemini did not return the expected "
            "extract_travel_intent function call."
        )

    arguments = dict(
        function_call.args
    )

    # -----------------------------------------------------
    # IMPORTANT:
    # Relative dates are calculated locally instead of
    # trusting the LLM to invent a calendar date.
    # -----------------------------------------------------

    deterministic_departure_time = (
        extract_departure_time(text)
    )

    return TravelIntent(
        language=arguments.get(
            "language",
            "Unknown",
        ),

        intent=arguments.get(
            "intent",
            "unknown",
        ),

        origin=arguments.get(
            "origin"
        ) or None,

        destination=arguments.get(
            "destination"
        ) or None,

        departure_time=(
            deterministic_departure_time
            or arguments.get(
                "departure_time"
            )
            or None
        ),
    )