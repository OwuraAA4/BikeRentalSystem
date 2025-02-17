import sqlite3
import json
from datetime import datetime
from datetime import datetime, timedelta
from database import connect_db, close_db
import membershipManager

# Memberships dictionary for testing
# memberships = {
#     "1001": {
#         "active": True,
#         "RentalLimit": 5,               # "RentalLimit"
#         "MembershipEndDate": "2024-12-31"  # Sample future date
#     },
#     "999": {
#         "active": False,
#         "RentalLimit": 0,               # "RentalLimit"
#         "MembershipEndDate": "2023-01-01"  # Sample past date
#     },
#     # Add more members as needed
# }

# # Convert MembershipEndDate to datetime for each member
# for member_id in memberships:
#     memberships[member_id]["MembershipEndDate"] = datetime.strptime(
#         memberships[member_id]["MembershipEndDate"], "%Y-%m-%d"
#     )

# Load the memberships data from the JSON file
def load_memberships():
    try:
        with open("membership.json", "r") as file:
            memberships = json.load(file)
            
            # Convert MembershipEndDate strings to datetime objects for consistency
            for member_id, details in memberships.items():
                details["MembershipEndDate"] = datetime.strptime(details["MembershipEndDate"], "%Y-%m-%d")
                
            return memberships
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Could not load membership data.")
        return {}

# Function to rent a bicycle
def rent_bike(member_id, bike_id, rental_duration):
    memberships = load_memberships()  # Load the membership dictionary
    conn = connect_db()
    cursor = conn.cursor()

    # Convert member_id to string if necessary
    member_id = str(member_id)

    # Step 1: Verify if the member is active
    if not membershipManager.check_membership(member_id, memberships):
        close_db(conn)
        return f"Member ID {member_id} is not active."

    # Step 2: Check if the member has reached their rental limit
    current_rentals = cursor.execute(
        "SELECT COUNT(*) FROM rentals WHERE member_id = ? AND return_date IS NULL",
        (member_id,)
    ).fetchone()[0]

    rental_limit = membershipManager.get_rental_limit(member_id, memberships)
    if current_rentals >= rental_limit:
        close_db(conn)
        return f"Member ID {member_id} has reached the rental limit of {rental_limit}."

    # Step 3: Check if the bicycle is available
    cursor.execute("SELECT status FROM bicycles WHERE id = ?", (bike_id,))
    bike_status = cursor.fetchone()
    if not bike_status:
        close_db(conn)
        return f"Bicycle ID {bike_id} does not exist."
    elif bike_status[0] != "Available":
        close_db(conn)
        return f"Bicycle ID {bike_id} is not available for rent. It is {bike_status[0]}"

    # Step 4: Process the rental with rental duration and expected return date
    rental_date = datetime.now()
    expected_return_date = rental_date + timedelta(days=rental_duration)
    
    cursor.execute("UPDATE bicycles SET status = 'Rented' WHERE id = ?", (bike_id,))
    cursor.execute("INSERT INTO rentals (bicycle_id, rental_date, expected_return_date, member_id) VALUES (?, ?, ?, ?)",
                   (bike_id, rental_date.strftime("%Y-%m-%d"), expected_return_date.strftime("%Y-%m-%d"), member_id))
    conn.commit()

    close_db(conn)
    return f"Rental successful. Bicycle ID {bike_id} rented by Member ID {member_id} for {rental_duration} days. Expected return date: {expected_return_date.strftime('%Y-%m-%d')}"

# Testing Purposes Only
# Uncomment it if you want to test this module
# Testing the rent_bike function
if __name__ == "__main__":
    # Test the function with various scenarios
    print(rent_bike("1001", 1, 3))  # Expected to succeed if bike_id 1 is available
    print(rent_bike("1005", 2, 10))   # Expected to succeed if bike_id 2 is available
    print(rent_bike("1004", 4, 1))   # Expected to fail due to inactive member
