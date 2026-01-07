"""
SOAP Client module for ATS Mileage Sync.

This module handles SOAP web service communication for fetching mileage data
from external reporting services using XML-based SOAP envelopes.
"""

import requests
from .logger import log_debug

# SOAP Envelope Template for mileage report requests
SOAP_ENVELOPE_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <wsMileageReport xmlns="http://tempuri.org/">
      <User>
        <UserName>{username}</UserName>
        <Password>{password}</Password>
        <CompanyCode>{company_code}</CompanyCode>
      </User>
      <DeviceID></DeviceID>
      <Startdate>{start_date}</Startdate>
      <Enddate>{end_date}</Enddate>
    </wsMileageReport>
  </soap:Body>
</soap:Envelope>
"""


def fetch_mileage_xml(
    *,
    soap_url: str,
    soap_action: str,
    username: str,
    password: str,
    company_code: str,
    start_date: str,
    end_date: str,
    timeout_sec: int = 60,
) -> str:
    """
    Fetch mileage data from SOAP web service.

    Sends a SOAP request to the mileage reporting service and returns
    the XML response containing mileage records for the specified date range.

    Args:
        soap_url: URL of the SOAP web service endpoint
        soap_action: SOAP action header for the request
        username: Service authentication username
        password: Service authentication password
        company_code: Company identifier for the service
        start_date: Start date for mileage data (ISO format)
        end_date: End date for mileage data (ISO format)
        timeout_sec: Request timeout in seconds (default: 60)

    Returns:
        Raw XML response string from the SOAP service

    Raises:
        requests.HTTPError: If the SOAP request fails with an HTTP error
    """
    #log_debug(f"SOAP REQUEST START | URL={soap_url} | Start={start_date} | End={end_date}")
    print(f"DEBUG SOAP: Starting SOAP request to {soap_url} for {start_date} to {end_date}")

    # Prepare SOAP request headers
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": soap_action,
    }

    # Format SOAP envelope with provided parameters
    body = SOAP_ENVELOPE_TEMPLATE.format(
        username=username,
        password=password,
        company_code=company_code,
        start_date=start_date,
        end_date=end_date,
    )
    print(f"DEBUG SOAP: SOAP envelope prepared with company code: {company_code}")

    #log_debug("Sending SOAP request...")
    print("DEBUG SOAP: Sending SOAP request...")

    # Send SOAP request
    resp = requests.post(
        soap_url,
        data=body.encode("utf-8"),
        headers=headers,
        timeout=timeout_sec,
    )
    resp.raise_for_status()

    #log_debug(f"SOAP REQUEST COMPLETE | Status={resp.status_code} | ResponseLength={len(resp.text)}")
    print(f"DEBUG SOAP: SOAP request completed - Status: {resp.status_code}, Response length: {len(resp.text)}")
    return resp.text
