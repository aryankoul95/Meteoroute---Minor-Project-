import xml.etree.ElementTree as ET
from typing import Optional


CAP_NAMESPACE = {
    "cap": "urn:oasis:names:tc:emergency:cap:1.2"
}


def _get_text(
    element: ET.Element,
    path: str,
) -> Optional[str]:
    """Safely extract text from a CAP XML element."""

    node = element.find(
        path,
        CAP_NAMESPACE,
    )

    if node is None:
        return None

    return node.text.strip() if node.text else None


def _parse_alert_info(
    info: ET.Element,
) -> dict:

    area = info.find(
        "cap:area",
        CAP_NAMESPACE,
    )

    area_data = {}

    if area is not None:

        area_data = {
            "area_desc": _get_text(
                area,
                "cap:areaDesc",
            ),

            "polygon": _get_text(
                area,
                "cap:polygon",
            ),

            "circle": _get_text(
                area,
                "cap:circle",
            ),

            "geocode": [],
        }

        for value in area.findall(
            "cap:geocode",
            CAP_NAMESPACE,
        ):

            name = _get_text(
                value,
                "cap:valueName",
            )

            code = _get_text(
                value,
                "cap:value",
            )

            if name or code:

                area_data["geocode"].append(
                    {
                        "value_name": name,
                        "value": code,
                    }
                )

    return {
        "language": _get_text(
            info,
            "cap:language",
        ),

        "category": _get_text(
            info,
            "cap:category",
        ),

        "event": _get_text(
            info,
            "cap:event",
        ),

        "urgency": _get_text(
            info,
            "cap:urgency",
        ),

        "severity": _get_text(
            info,
            "cap:severity",
        ),

        "certainty": _get_text(
            info,
            "cap:certainty",
        ),

        "effective": _get_text(
            info,
            "cap:effective",
        ),

        "onset": _get_text(
            info,
            "cap:onset",
        ),

        "expires": _get_text(
            info,
            "cap:expires",
        ),

        "sender_name": _get_text(
            info,
            "cap:senderName",
        ),

        "headline": _get_text(
            info,
            "cap:headline",
        ),

        "description": _get_text(
            info,
            "cap:description",
        ),

        "instruction": _get_text(
            info,
            "cap:instruction",
        ),

        "area": area_data,
    }


def parse_cap_alert(
    xml_content: str,
) -> dict:

    root = ET.fromstring(
        xml_content
    )

    alert_identifier = _get_text(
        root,
        "cap:identifier",
    )

    sender = _get_text(
        root,
        "cap:sender",
    )

    sent = _get_text(
        root,
        "cap:sent",
    )

    status = _get_text(
        root,
        "cap:status",
    )

    msg_type = _get_text(
        root,
        "cap:msgType",
    )

    scope = _get_text(
        root,
        "cap:scope",
    )

    info_elements = root.findall(
        "cap:info",
        CAP_NAMESPACE,
    )

    info_list = []

    for info in info_elements:

        info_list.append(
            _parse_alert_info(info)
        )

    return {
        "identifier": alert_identifier,
        "sender": sender,
        "sent": sent,
        "status": status,
        "message_type": msg_type,
        "scope": scope,
        "info": info_list,
    }


def parse_cap_feed(
    xml_content: str,
) -> list[dict]:

    """
    Parse one CAP alert XML document.

    Returns a list containing the normalized
    alert object.
    """

    return [
        parse_cap_alert(
            xml_content
        )
    ]