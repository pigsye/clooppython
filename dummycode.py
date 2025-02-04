import os
import shelve

# Define database names
DB_FOLDER = "db"  # Change this to the actual DB folder path
DB_NAMES = ["accounts", "feedback", "logs", "orders", "products", "ratings", "reports", "submissions", "tags", "wishlist"]

def load_database(db_name):
    db_path = os.path.join(DB_FOLDER, db_name)
    try:
        with shelve.open(db_path) as db:
            print(f"\n📂 Database: {db_name}")
            if not db:
                print("⚠️  No records found.")
            else:
                for key, value in db.items():
                    print(f"🔑 {key}: {value}")
    except Exception as e:
        print(f"❌ Error reading {db_name}: {e}")

def main():
    print("\n🔍 Extracting all database contents...\n")
    for db in DB_NAMES:
        load_database(db)

if __name__ == "__main__":
    main()