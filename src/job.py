"""
Job module for ATS Mileage Sync operations.

This module contains the main business logic for synchronizing mileage data
from SOAP web services to MSSQL database, including date range processing
and deduplication logic.
"""

from datetime import datetime, timedelta

from src.config import Settings
from src.db import MsSql
from src.parser import parse_mileage_response
from src.soap_client import fetch_mileage_xml
from src.mail_client import send_html_mail


def build_summary_mail(date_str: str, summary: dict, records: list[dict]) -> str:
    rows = ""
    for r in records:
        rows += f"""
        <tr>
            <td>{r['plate']}</td>
            <td>{r['device_id']}</td>
            <td>{r['mileage']}</td>
        </tr>
        """

    return f"""
    <h3>ATS Mileage Günlük Senkronizasyon</h3>

    <p><b>Tarih:</b> {date_str}</p>

    <ul>
        <li><b>Insert:</b> {summary['inserted']}</li>
        <li><b>Skip (Duplicate):</b> {summary['skipped']}</li>
        <li><b>Hata:</b> {summary['errors']}</li>
    </ul>

    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Plaka</th>
            <th>DeviceId</th>
            <th>KM</th>
        </tr>
        {rows}
    </table>
    """

def iso_range_for_day(day: datetime) -> tuple[str, str]:
    """
    Generate ISO 8601 datetime range for a full day.

    Args:
        day: Date for which to generate the range

    Returns:
        Tuple of (start_iso, end_iso) strings in ISO 8601 format
    """
    return (
        day.strftime("%Y-%m-%dT00:00:00"),
        day.strftime("%Y-%m-%dT23:59:59"),
    )


def run_for_date(target_date: datetime, settings: Settings) -> dict:
    start_iso, end_iso = iso_range_for_day(target_date)
    date_str = target_date.strftime("%Y-%m-%d")

    print(f"DEBUG JOB: Starting job for date {date_str}")

    db = MsSql(
        driver=settings.mssql_driver,
        server=settings.mssql_server,
        database=settings.mssql_database,
        user=settings.mssql_user,
        password=settings.mssql_password,
    )

    summary = {
        "date": date_str,
        "inserted": 0,
        "skipped": 0,
        "errors": 0,
    }

    inserted_records: list[dict] = []

    try:
        print(f"DEBUG JOB: Fetching XML from {start_iso} to {end_iso}")

        xml = fetch_mileage_xml(
            soap_url=settings.soap_url,
            soap_action=settings.soap_action,
            username=settings.soap_username,
            password=settings.soap_password,
            company_code=settings.soap_company_code,
            start_date=start_iso,
            end_date=end_iso,
        )

        print("DEBUG JOB: XML fetched successfully")

        records = parse_mileage_response(xml)
        print(f"DEBUG JOB: Parsed {len(records)} records")

        for r in records:
            if not r.device_id:
                continue

            if settings.deduplicate and db.exists_for_date(r.device_id, date_str):
                summary["skipped"] += 1
                continue

            db.insert_km_log(
                device_id=r.device_id,
                license_plate=r.license_plate,
                date_str=date_str,
                mileage=r.mileage,
            )

            inserted_records.append({
                "device_id": r.device_id,
                "plate": r.license_plate,
                "mileage": r.mileage,
            })

            summary["inserted"] += 1

        db.commit()
        print(f"DEBUG JOB: Commit successful ({summary['inserted']} rows)")

        if summary["inserted"] > 0:
            html = build_summary_mail(
                date_str=date_str,
                summary=summary,
                records=inserted_records,
            )

            send_html_mail(
                subject=f"ATS Mileage | {date_str} | {summary['inserted']} kayıt",
                html_body=html,
            )

    except Exception as e:
        db.rollback()
        summary["errors"] += 1

        print(f"❌ DEBUG JOB ERROR: {str(e)}")

        send_html_mail(
            subject=f"ATS Mileage | {date_str} | {summary['inserted']} kayıt",
            html_body=html
        )

    finally:
        db.close()
        print("DEBUG JOB: Database connection closed")

    print(
        f"DEBUG JOB: Completed | "
        f"Inserted={summary['inserted']} "
        f"Skipped={summary['skipped']} "
        f"Errors={summary['errors']}"
    )

    return summary


def run_yesterday(settings: Settings) -> dict:
    """
    Run mileage synchronization job for yesterday's date.

    Args:
        settings: Application configuration settings

    Returns:
        Dictionary with job summary (same format as run_for_date)
    """
    yesterday = datetime.now() - timedelta(days=1)
    print(f"DEBUG JOB: Running for yesterday ({yesterday.strftime('%Y-%m-%d')})")
    return run_for_date(yesterday, settings)
