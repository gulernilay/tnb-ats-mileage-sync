"""
Database module for MSSQL operations in ATS Mileage Sync.

This module provides a wrapper class for Microsoft SQL Server database operations
including connection management, transaction handling, and mileage log insertion.
"""

from datetime import datetime
import pyodbc
from .logger import _send_mail, log_info
from .mail_client import send_html_mail
from .config import Settings
class MsSql:
    """
    Microsoft SQL Server database connection and operations wrapper.

    This class manages database connections, transactions, and provides methods
    for inserting mileage records and checking for existing records.
    """

    def __init__(self, *, driver: str, server: str, database: str, user: str, password: str):
        """
        Initialize database connection.

        Args:
            driver: MSSQL driver name (e.g., "ODBC Driver 17 for SQL Server")
            server: Database server hostname/IP
            database: Database name
            user: Database username
            password: Database password
        """
        log_info(f"Connecting to database: {server}/{database}")
        print(f"DEBUG DB: Connecting to database {server}/{database}")
        self.conn = pyodbc.connect(
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            "TrustServerCertificate=yes;"
        )
        self.conn.autocommit = False
        #log_info("Database connection established")
        print("DEBUG DB: Database connection established successfully")

    def insert_km_log(
        self,
        device_id: str,
        license_plate: str | None,
        date_str: str,
        mileage: int | None,
        # settings: dict,  # Add settings parameter
    ):
        sql = """
        INSERT INTO dbo.arac_km_log
        (DeviceId, License_Plate, [Date], Mileage, KayitTarihi)
        VALUES (?, ?, ?, ?, GETDATE())
        """
        cur = self.conn.cursor()
        cur.execute(sql, device_id, license_plate, date_str, mileage)

        print(f"DEBUG DB: Executed INSERT for Plate={license_plate}, Date={date_str}, KM={mileage}")

        

    def commit(self):
        """Commit the current database transaction."""
        log_info("Committing database transaction")
        print("DEBUG DB: Committing database transaction")
        self.conn.commit()

    def rollback(self):
        """Rollback the current database transaction."""
        log_info("Rolling back database transaction")
        print("DEBUG DB: Rolling back database transaction")
        self.conn.rollback()

    def close(self):
        """Close the database connection."""
        log_info("Closing database connection")
        print("DEBUG DB: Closing database connection")
        self.conn.close()

    def exists_for_date(self, device_id: str, date_str: str) -> bool:
        """
        Check if a mileage record exists for the given device and date.

        Args:
            device_id: Device identifier
            date_str: Date string in YYYY-MM-DD format

        Returns:
            True if a record exists, False otherwise
        """
        sql = """
        SELECT 1
        FROM dbo.arac_km_log WITH (NOLOCK)
        WHERE DeviceId = ?
          AND CONVERT(date, [Date]) = CONVERT(date, ?)
        """
        cur = self.conn.cursor()
        row = cur.execute(sql, device_id, date_str).fetchone()
        return row is not None
