import sqlite3
from datetime import datetime

import sqlite3
from datetime import datetime

# Step 1: Database connection and disconnection functions
def connect_db():
    return sqlite3.connect("BicycleRental.db")

def close_db(conn):
    conn.close()


# Step 2: Table creation function
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    # Create bicycles table
    cursor.execute('''CREATE TABLE IF NOT EXISTS bicycles (
                        id INTEGER PRIMARY KEY,
                        brand TEXT,
                        type TEXT,
                        frame_size TEXT,
                        rental_rate TEXT,
                        purchase_date TEXT,
                        condition TEXT,
                        status TEXT
                    )''')
    # Create rentals table
    cursor.execute('''CREATE TABLE IF NOT EXISTS rentals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bicycle_id INTEGER,
                        rental_date TEXT,
                        expected_return_date TEXT,  
                        return_date TEXT,
                        member_id INTEGER,
                        fees REAL,
                        damage_details TEXT,
                        FOREIGN KEY (bicycle_id) REFERENCES bicycles (id)
                    )''')
    conn.commit()
    close_db(conn)


# Step 3: Data loading and cleaning function
def load_and_clean_data():
    conn = connect_db()
    cursor = conn.cursor()

    # Load Bicycle_Info.txt
    with open("Bicycle_Info.txt", "r") as bike_file:
        for line in bike_file:
            fields = line.strip().split("|")  # Assuming fields are seperated by |

            # Extract each field and clean data
            try:
                bike_id = int(fields[0])
                brand = fields[1].strip() if fields[1].strip() else "Unknown"
                bike_type = fields[2].strip() if fields[2].strip() else "Unknown"
                frame_size = fields[3].strip() if fields[3].strip() else "Unknown"
                rental_rate = clean_rental_rate(fields[4]) if fields[4] else "0/day"
                purchase_date = clean_date(fields[5].strip())
                condition = fields[6].strip() if fields[6].strip() else "Good"
                status = fields[7].strip() if fields[7].strip() else "Available"

                # Insert into bicycles table
                cursor.execute('''INSERT OR IGNORE INTO bicycles (id, brand, type, frame_size, rental_rate, purchase_date, condition, status)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                               (bike_id, brand, bike_type, frame_size, rental_rate, purchase_date, condition, status))

            except (IndexError, ValueError) as e:
                print(f"Error in Bicycle_Info.txt - Skipping line: {line}, Error: {e}")

    # Load Rental_History.txt
    with open("Rental_History.txt", "r") as rental_file:
        for line in rental_file:
            fields = line.strip().split("|")

            # Extract each field and clean data
            try:
                bicycle_id = int(fields[0])
                rental_date = clean_date(fields[1].strip())
                return_date = clean_date(fields[2].strip())
                member_id = clean_member_id(fields[3].strip())

                # Insert into rentals table
                cursor.execute('''INSERT INTO rentals (bicycle_id, rental_date, return_date, member_id)
                                  VALUES (?, ?, ?, ?)''', 
                               (bicycle_id, rental_date, return_date, member_id))

            except (IndexError, ValueError) as e:
                print(f"Error in Rental_History.txt - Skipping line: {line}, Error: {e}")

    # Commit and close connection
    conn.commit()
    close_db(conn)

# Helper function to clean rental rate
def clean_rental_rate(rate):
    # Ensure consistent format like 
    if "£" in rate:
        rate = rate.replace("£", "").strip()
    if "/" not in rate:
        rate += "/day"  # Default to daily rate if no period is specified
    return rate

# Helper function to clean date
def clean_date(date_str):
    # Handle different date formats, defaulting to a standard format
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    print(f"Invalid date format for {date_str}, setting as NULL")
    return None  # Return None if no valid date format is found

# Helper function to clean member ID
def clean_member_id(member_id):
    # Ensure Member ID is a valid integer, default to None if invalid
    try:
        return int(member_id)
    except ValueError:
        print(f"Invalid Member ID '{member_id}', setting as NULL")
        return None

# Step 4: Initialization function
def initialize_database():
    create_tables()
    load_and_clean_data()

# Run the initialization function to set up the database
if __name__ == "__main__":
    initialize_database()
