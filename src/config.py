"""
Configuration module for ATS Mileage Sync application.

This module handles loading and validation of environment variables
required for SOAP web service communication and MSSQL database connection.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _req(name: str) -> str:
    """
    Get a required environment variable.

    Args:
        name: Environment variable name

    Returns:
        The environment variable value

    Raises:
        RuntimeError: If the environment variable is not set
    """
    val = os.getenv(name)
    if not val:
        print(f"DEBUG CONFIG: Missing required environment variable: {name}")
        raise RuntimeError(f"Missing env var: {name}")
    print(f"DEBUG CONFIG: Loaded {name} = {'*' * len(val) if 'PASSWORD' in name else val}")
    return val


@dataclass(frozen=True)
class Settings:
    """
    Application settings loaded from environment variables.

    This dataclass contains all configuration required for the application
    to communicate with SOAP services and MSSQL database. All fields are
    loaded from environment variables and the class is frozen to prevent
    modification after initialization.
    """

    # SOAP Web Service Configuration
    soap_url: str = _req("SOAP_URL")
    soap_action: str = _req("SOAP_ACTION")
    soap_username: str = _req("SOAP_USERNAME")
    soap_password: str = _req("SOAP_PASSWORD")
    soap_company_code: str = _req("SOAP_COMPANY_CODE")

    # MSSQL Database Configuration
    mssql_driver: str = _req("MSSQL_DRIVER")
    mssql_server: str = _req("MSSQL_SERVER")
    mssql_database: str = _req("MSSQL_DATABASE")
    mssql_user: str = _req("MSSQL_USER")
    mssql_password: str = _req("MSSQL_PASSWORD")
   
    
    # Application Settings
    deduplicate: bool = os.getenv("DEDUPLICATE", "true").lower() in ("1", "true", "yes", "y")

    def __post_init__(self):
        """Post-initialization hook to log successful settings loading."""
        print("DEBUG CONFIG: Settings loaded successfully")
        print(f"DEBUG CONFIG: DEDUPLICATE = {self.deduplicate}")