import sqlite3
from database import connect_db, close_db  # Import connection functions from database.py

# Function to search bicycles based on dynamic criteria
def search_bicycles(type=None, brand=None, frame_size=None):
    # Check if all search criteria are empty
    if not type and not brand and not frame_size:
        return "Please specify at least one search criterion."
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Start with base query
    query = "SELECT * FROM bicycles WHERE 1=1"
    parameters = []

    # Add filters based on available parameters
    if type:
        query += " AND type = ?"
        parameters.append(type)
    if brand:
        query += " AND brand = ?"
        parameters.append(brand)
    if frame_size:
        query += " AND frame_size = ?"
        parameters.append(frame_size)

    # Execute the dynamically built query with parameters
    cursor.execute(query, parameters)
    results = cursor.fetchall()
    close_db(conn)

    # Return results if found, or a message if no results match
    return results if results else "No bicycles found matching the criteria."

# Function to display search results
def display_results(results):
    if not results:
        print("No bicycles found for the given criteria.")
    else:
        for row in results:
            print(f"ID: {row[0]}, Brand: {row[1]}, Type: {row[2]}, Frame Size: {row[3]}, "
                  f"Rental Rate: {row[4]}, Purchase Date: {row[5]}, Condition: {row[6]}, Status: {row[7]}")

# Testing Purposes Only
# Uncomment it if you want to test this module
# Testing the search functions
# if __name__ == "__main__":
#    # Test search by brand
#    print("Search by brand 'Trek':")
#    display_results(search_by_brand("Trek"))

#    # Test search by type
#    print("\nSearch by type 'Mountain Bike':")
#    display_results(search_by_type("Mountain Bike"))

#    Test search by frame size
#    print("\nSearch by frame size 'Medium':")
#    display_results(search_by_frame_size("Medium"))