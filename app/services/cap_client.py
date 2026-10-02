import httpx
import xml.etree.ElementTree as ET


IMD_CAP_RSS_URL = "https://cap-sources.s3.amazonaws.com/in-imd-en/rss.xml"


async def fetch_official_cap_alerts() -> list[str]:
    """
    Fetch official IMD CAP alert XML documents listed in the IMD RSS feed.
    """

    alerts = []

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(IMD_CAP_RSS_URL)
        response.raise_for_status()

        root = ET.fromstring(response.text)

        for item in root.findall(".//item"):
            link = item.findtext("link")

            if not link:
                continue

            try:
                alert_response = await client.get(link)
                alert_response.raise_for_status()
                alerts.append(alert_response.text)
            except Exception:
                continue

    return alerts