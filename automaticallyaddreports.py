import os
import shelve

DB_FOLDER = "db"
DB_PATH_REPORT = os.path.join(DB_FOLDER, "reports")
DB_PATH_ACCOUNT = os.path.join(DB_FOLDER, "accounts")

# Example reports to add
sample_reports = [
    {
        "customerId": "1",  # Use actual user IDs from the accounts database
        "reportedBy": "2",
        "reason": "Inappropriate behavior",
    },
    {
        "customerId": "3",
        "reportedBy": "4",
        "reason": "Spam messages",
    },
    {
        "customerId": "5",
        "reportedBy": "6",
        "reason": "Spam messages",
    },
    {
        "customerId": "7",
        "reportedBy": "8",
        "reason": "Spam messages",
    },
    {
        "customerId": "9",
        "reportedBy": "10",
        "reason": "Spam messages",
    },
]

def recreate_reports_db():
    with shelve.open(DB_PATH_REPORT, writeback=True) as reports_db:
        for index, report in enumerate(sample_reports, start=1):
            report_id = str(index)  # Generate unique IDs
            reports_db[report_id] = {
                "id": report_id,  # Add unique ID to the report
                **report,         # Add the remaining fields from the sample report
            }
        print("Reports database has been recreated with sample data.")

if __name__ == "__main__":

    # Recreate reports database
    recreate_reports_db()