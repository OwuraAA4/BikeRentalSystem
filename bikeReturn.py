import sqlite3
from datetime import datetime
from database import connect_db, close_db

# Define an additional daily fee for late returns
LATE_FEE_PER_DAY = 5  # Flat late fee added on top of rental rate for each late day

# Function to calculate late fees based on rental rate and additional fees
def calculate_fees(rental_date, return_date, rental_rate):
    # Clean up the rental rate string
    cleaned_rate = rental_rate.replace("£", "").replace("Â", "").split("/")[0].strip()
    
    try:
        rental_rate_per_day = float(cleaned_rate)  # Convert cleaned rate to a float
    except ValueError:
        print("Error: Could not parse rental rate.")
        return 0  # Return 0 if rental rate is invalid

    days_rented = (return_date - rental_date).days
    allowed_rental_days = 7  # Allowed rental period before late fees apply

    # Calculate late fees if the return is after the allowed days
    if days_rented > allowed_rental_days:
        late_days = days_rented - allowed_rental_days
        return late_days * (rental_rate_per_day + LATE_FEE_PER_DAY)
    return 0

# Function to return a bicycle with optional damage handling
def return_bike(bike_id, damage_details=None, damage_charge=0, new_condition="Good"):
    conn = connect_db()
    cursor = conn.cursor()

    # Retrieve the rental record and rental rate for the bicycle
    cursor.execute("""
        SELECT rentals.rental_date, bicycles.rental_rate, bicycles.condition
        FROM rentals
        JOIN bicycles ON rentals.bicycle_id = bicycles.id
        WHERE rentals.bicycle_id = ? AND rentals.return_date IS NULL
    """, (bike_id,))
    rental_record = cursor.fetchone()

    # If no active rental is found, return an error message
    if not rental_record:
        close_db(conn)
        return f"No active rental found for Bicycle ID {bike_id}."

    # Extract rental_date, rental_rate, and current condition
    rental_date_str, rental_rate, current_condition = rental_record
    rental_date = datetime.strptime(rental_date_str, "%Y-%m-%d")
    return_date = datetime.now()

    # Calculate fees
    late_fee = calculate_fees(rental_date, return_date, rental_rate)
    total_damage_charge = damage_charge if damage_details else 0
    total_fees = late_fee + total_damage_charge

    # Update the rentals table with the return date, fees, and any damage details
    cursor.execute("""
        UPDATE rentals
        SET return_date = ?, fees = ?, damage_details = ?
        WHERE bicycle_id = ? AND return_date IS NULL
    """, (return_date.strftime("%Y-%m-%d"), total_fees, damage_details, bike_id))

    # Update the bicycle's condition and status
    cursor.execute("""
    UPDATE bicycles
    SET condition = ?, status = ?
    WHERE id = ?
    """, (new_condition, "Unavailable" if new_condition == "Damaged" else "Available", bike_id))

    conn.commit()
    close_db(conn)

    # Return confirmation message
    return_message = f"Bicycle Return processed for Bicycle ID {bike_id}."
    if late_fee > 0:
        return_message += f" Late fee: £{late_fee:.2f}."
    if damage_charge > 0:
        return_message += f" Damage charge: £{damage_charge:.2f}."
    if new_condition == "Damaged":
        return_message += " Bicycle marked as 'Damaged' and made unavailable for rental."

    return return_message

# Testing the return_bike function
# if __name__ == "__main__":
#     # Sample test cases
#     print(return_bike(1, damage_details="Broken chain", damage_charge=15, new_condition="Damaged"))  # Test case with damage
#     print(return_bike(2))  # Test case without damage
