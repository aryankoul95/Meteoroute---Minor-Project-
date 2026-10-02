from typing import Optional


def _to_text(value) -> Optional[str]:
    """
    Convert a value to a clean string.
    Return None when the value is missing.
    """

    if value is None:
        return None

    text = str(value).strip()

    return text if text else None


def normalize_cap_alert(
    alert: dict,
) -> dict:
    """
    Normalize a parsed CAP alert into a consistent
    MeteoRoute hazard format.
    """

    info_list = alert.get(
        "info",
        [],
    )

    normalized_info = []

    for info in info_list:

        area = info.get(
            "area",
            {},
        )

        normalized_info.append(
            {
                "language": _to_text(
                    info.get("language")
                ),

                "category": _to_text(
                    info.get("category")
                ),

                "event": _to_text(
                    info.get("event")
                ),

                "urgency": _to_text(
                    info.get("urgency")
                ),

                "severity": _to_text(
                    info.get("severity")
                ),

                "certainty": _to_text(
                    info.get("certainty")
                ),

                "effective": _to_text(
                    info.get("effective")
                ),

                "onset": _to_text(
                    info.get("onset")
                ),

                "expires": _to_text(
                    info.get("expires")
                ),

                "sender_name": _to_text(
                    info.get("sender_name")
                ),

                "headline": _to_text(
                    info.get("headline")
                ),

                "description": _to_text(
                    info.get("description")
                ),

                "instruction": _to_text(
                    info.get("instruction")
                ),

                "area": {
                    "area_desc": _to_text(
                        area.get("area_desc")
                    ),

                    "polygon": _to_text(
                        area.get("polygon")
                    ),

                    "circle": _to_text(
                        area.get("circle")
                    ),

                    "geocode": (
                        area.get(
                            "geocode",
                            [],
                        )
                    ),
                },
            }
        )

    return {
        "identifier": _to_text(
            alert.get("identifier")
        ),

        "sender": _to_text(
            alert.get("sender")
        ),

        "sent": _to_text(
            alert.get("sent")
        ),

        "status": _to_text(
            alert.get("status")
        ),

        "message_type": _to_text(
            alert.get("message_type")
        ),

        "scope": _to_text(
            alert.get("scope")
        ),

        "source": "CAP",

        "info": normalized_info,
    }


def normalize_cap_feed(
    alerts: list[dict],
) -> list[dict]:
    """
    Normalize a list of parsed CAP alerts.
    """

    return [
        normalize_cap_alert(alert)
        for alert in alerts
    ]