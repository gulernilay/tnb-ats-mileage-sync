"""
XML Parser module for ATS Mileage Sync.

This module parses SOAP XML responses from mileage reporting services
and extracts structured mileage record data for database insertion.
"""

from dataclasses import dataclass
from lxml import etree

DEBUG = True  # Set to False in production


@dataclass
class MileageRecord:
    """
    Represents a single mileage record from the SOAP response.

    Attributes:
        device_id: Unique identifier for the GPS/tracking device
        license_plate: Vehicle license plate number (optional)
        mileage: Mileage reading in kilometers (optional)
    """
    device_id: str
    license_plate: str | None
    mileage: int | None


def parse_mileage_response(xml_text: str) -> list[MileageRecord]:
    """
    Parse SOAP XML response and extract mileage records.

    This function processes XML responses from mileage reporting web services,
    extracts individual mileage records, and converts them into structured data.

    Args:
        xml_text: Raw XML response string from SOAP service

    Returns:
        List of MileageRecord objects containing parsed data
    """
    if DEBUG:
        print("DEBUG PARSER: Starting XML parsing")
        print(f"DEBUG PARSER: XML length = {len(xml_text)}")

    root = etree.fromstring(xml_text.encode("utf-8"))

    # Find MileageL records within SOAP response
    items = root.xpath("//*[local-name()='MileageL']")

    if DEBUG:
        print(f"DEBUG PARSER: Found {len(items)} MileageL items")

    records: list[MileageRecord] = []

    for idx, item in enumerate(items, start=1):
        # Extract data fields from XML
        device_id = _first_text(item, ["DeviceId", "DeviceID"])
        plate = _first_text(item, ["License_Plate", "LicensePlate"])
        mileage_txt = _first_text(item, ["Mileage", "KM", "Km"])

        if DEBUG:
            print(
                f"DEBUG PARSER [{idx}]: "
                f"DeviceId={device_id} | "
                f"Plate={plate} | "
                f"MileageRaw={mileage_txt}"
            )

        # Parse mileage value
        mileage = None
        if mileage_txt:
            try:
                mileage = int(mileage_txt.strip())
            except Exception as e:
                if DEBUG:
                    print(
                        f"DEBUG PARSER [{idx}]: "
                        f"Mileage parse failed ({mileage_txt}) | {e}"
                    )

        # Only create record if device_id exists (required field)
        if device_id:
            records.append(
                MileageRecord(
                    device_id=device_id,
                    license_plate=plate,
                    mileage=mileage
                )
            )
        else:
            if DEBUG:
                print(f"DEBUG PARSER [{idx}]: SKIPPED (DeviceId missing)")

    if DEBUG:
        print(f"DEBUG PARSER: Parsing complete. Total records = {len(records)}")

    return records


def _first_text(parent: etree._Element, names: list[str]) -> str | None:
    """
    Extract text content from the first matching XML element.

    Searches for elements with the given names and returns the text content
    of the first element found that contains non-empty text.

    Args:
        parent: Parent XML element to search within
        names: List of possible element names to search for

    Returns:
        Text content of the first matching element, or None if not found
    """
    for n in names:
        nodes = parent.xpath(f".//*[local-name()='{n}']")
        if nodes:
            text = nodes[0].text
            if text and text.strip():
                return text.strip()
    return None
