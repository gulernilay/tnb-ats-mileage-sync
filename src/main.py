import argparse
from datetime import datetime
from .config import Settings
from .job import run_yesterday, run_for_date
from .logger import log_info

def main():
    #log_info("Starting ATS Mileage Sync")
    print("DEBUG: Starting ATS Mileage Sync")
    print("ATS Mileage Sync")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD (bu gün için km çekip DB'ye yazar)")
    args = parser.parse_args()
    print(f"DEBUG: Parsed arguments - date: {args.date}")

    settings = Settings()
    #log_info("Settings loaded")
    print("DEBUG: Settings loaded successfully")

    if args.date:
        target = datetime.strptime(args.date, "%Y-%m-%d")
        #log_info(f"Running for specific date: {target.date()}")
        print(f"DEBUG: Running for specific date: {target.date()}")
        summary = run_for_date(target, settings)
    else:
        #log_info("Running for yesterday")
        print("DEBUG: Running for yesterday")
        summary = run_yesterday(settings)

    #log_info(f"Job completed. Summary: {summary}")
    print(f"DEBUG: Job completed with summary: {summary}")
    print(summary)

if __name__ == "__main__":
    main()
