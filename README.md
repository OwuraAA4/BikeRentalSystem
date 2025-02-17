Bicycle Rental Management System
This Bicycle Rental Management System is designed to manage bicycle rentals, returns, and inventory recommendations for a bike rental store. The system is structured as a set of Python modules, integrated with a database (BicycleRental.db) and a Jupyter Notebook interface (menu.ipynb) for easy interaction.

Project Structure
menu.ipynb: The main user interface, created with Jupyter Notebook, using ipywidgets for an interactive experience. This notebook offers access to all core functionalities, including searching, renting, returning bicycles, and viewing recommendations for new purchases based on budget.

database.py: Handles database creation and connection, setting up tables (bicycles and rentals) to store inventory and rental history.

bikeSearch.py: Provides functions to search the inventory by bicycle attributes, such as type, brand, and frame size.

bikeRent.py: Manages bicycle rentals, verifying member eligibility, rental limits, and setting the expected return date.

bikeReturn.py: Handles bicycle returns, calculating any applicable late fees based on the rental rate and condition of return. The module also supports additional charges for damages and updates the bicycle’s availability and condition.

bikeSelect.py: Recommends bicycle types for purchase based on the available budget and other factors like rental frequency, age, and condition.

memberships.json: A dictionary file containing membership details, including rental limits and membership status, for eligibility checks during rentals.

Setup Instructions
Python and Libraries: Ensure Python 3.11 is installed. Recommended libraries include sqlite3, ipywidgets, and pandas 
Create the Database: Run database.py to initialize the BicycleRental.db database.
Launch the Interface:
Open menu.ipynb in Jupyter Notebook or Visual Studio Code (with the Jupyter extension).
Run all cells to launch the main menu, where options for each functionality are presented.
Using the System
Search Bicycles: Search the inventory by type, brand, or frame size.
Rent a Bicycle: Specify a member_id, bike_id, and rental duration. Late fees will apply if the bicycle is returned after the expected return date.
Return a Bicycle: Input bike_id, and optionally add damage details and charges if applicable. The system automatically calculates late fees.
Purchase Recommendations: Enter a budget to generate a suggested list of bicycle types to buy, based on rental frequency, age, condition, and popularity.
Key Features
Automated Late Fees and Damage Management: The system calculates late fees based on both a daily rate and a fixed late fee for each day overdue, and allows for optional damage charges, updating the bicycle's condition in the database.

Inventory Recommendations: Recommendations consider rental frequency, popularity, and condition. This approach maximizes budget efficiency by prioritizing high-demand and low-condition bikes for replacement or restocking.

Notes
Data Integrity: The system uses foreign key constraints and checks to ensure that rentals and returns are valid.
Recommendation Algorithm: The recommendation algorithm checks for bikes in demand, bike condition, bike age, and bike popularty. After
the one with the highest counts amongst are the checks is recommended.

Special Instructions
Ensure that memberships.json is correctly populated with up-to-date membership details before using the rental features.
Always check the database (BicycleRental.db) for updated records after running rental and return operations.