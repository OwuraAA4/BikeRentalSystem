import sqlite3
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from database import connect_db, close_db

# Define the cost for each bicycle type
bicycle_costs = {
    "Mountain Bike": 300,
    "Hybrid Bike": 350,
    "Electric Bike": 1000,
    "Road Bike": 200,
    "Gravel Bike": 230,
    "Folding Bike": 400,
    "BMX": 250,
}

# Recommend based on rental frequency
def recommend_by_rental_frequency():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, COUNT(*) AS rental_count
        FROM rentals
        JOIN bicycles ON rentals.bicycle_id = bicycles.id
        GROUP BY type
    """)
    all_types = cursor.fetchall()
    close_db(conn)

    if all_types:
        df = pd.DataFrame(all_types, columns=['Type', 'Rental Count'])
        # Plot rental frequency as a bubble chart
        unique_types = df['Type'].unique()
        colors = plt.cm.get_cmap('tab20', len(unique_types))  # Choose a color map
        color_map = {unique_types[i]: colors(i) for i in range(len(unique_types))}
        bubble_colors = df['Type'].map(color_map)
        
        plt.figure(figsize=(10, 6))
        plt.scatter(df['Type'], df['Rental Count'], s=df['Rental Count']*10, c=bubble_colors, alpha=0.6, edgecolors="w", linewidth=2)
        plt.title("Rental Frequency by Bicycle Type")
        plt.xlabel("Bicycle Type")
        plt.ylabel("Rental Count")
        plt.xticks(rotation=45)
        plt.show()
        
        highest_rental_type = max(all_types, key=lambda x: x[1])
        print(f"Recommended Bicycle based on rental frequency: {highest_rental_type[0]}")
        return [{"Type": highest_rental_type[0], "Rental Count": highest_rental_type[1]}]
    return []

# Recommend based on age (select the oldest bicycle)
def recommend_by_age():
    conn = connect_db()
    cursor = conn.cursor()
    current_year = datetime.now().year
    cursor.execute("SELECT id, type, brand, purchase_date FROM bicycles")
    all_bicycles = cursor.fetchall()
    close_db(conn)

    bicycles_with_age = []
    for bike in all_bicycles:
        purchase_year = int(bike[3][:4]) if bike[3] else current_year
        age = current_year - purchase_year
        bicycles_with_age.append((bike[1], age))

    if bicycles_with_age:
        df = pd.DataFrame(bicycles_with_age, columns=['Type', 'Age'])

        # Plot the age of bicycles
        plt.figure(figsize=(10, 6))
        plt.bar(df['Type'], df['Age'], color='cornflowerblue')
        plt.title("Bicycle Ages by Type")
        plt.xlabel("Bicycle Type")
        plt.ylabel("Age")
        plt.xticks(rotation=45)
        plt.show()

        oldest_bike = max(bicycles_with_age, key=lambda x: x[1])
        print(f"Recommended Bicycle based on age: {oldest_bike[0]} ")
        return [{"Type": oldest_bike[0], "Age": oldest_bike[1]}]
    return []

# Recommend based on condition (select the type with highest % of damaged bikes)
def recommend_by_condition():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT type, condition, COUNT(*) AS condition_count
        FROM bicycles
        WHERE condition IN ('Fair', 'New', 'Good', 'Damaged')
        GROUP BY type, condition
        ORDER BY type, condition
    """)
    bikes_by_condition = cursor.fetchall()
    close_db(conn)

    if bikes_by_condition:
        df = pd.DataFrame(bikes_by_condition, columns=['Type', 'Condition', 'Condition Count'])
        pivot_df = df.pivot(index='Type', columns='Condition', values='Condition Count').fillna(0)

        # Calculate percentage of damaged bikes
        pivot_df_percentage = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100
        result_df = pivot_df.astype(int).astype(str) + " (" + pivot_df_percentage.round(1).astype(str) + "%)"
        
        # Display the result table
        print(result_df)

        # Plot condition percentages as a stacked bar chart
        pivot_df_percentage.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='Set3')
        plt.title("Bicycle Condition Distribution by Type")
        plt.xlabel("Bicycle Type")
        plt.ylabel("Percentage")
        plt.xticks(rotation=45)
        plt.legend(title='Condition')
        plt.show()

        # Find the type with the highest % of damaged bikes
        highest_damaged_type = pivot_df_percentage['Damaged'].idxmax()
        print(f"Recommended Bicycle based on condition (highest damaged percentage): {highest_damaged_type} ")
        return [{"Type": highest_damaged_type, "Damaged Percentage": pivot_df_percentage.loc[highest_damaged_type, 'Damaged']}]
    return []

# Recommend based on type popularity (select the most popular type)
def recommend_by_type_popularity():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, COUNT(*) AS popularity
        FROM bicycles
        JOIN rentals ON bicycles.id = rentals.bicycle_id
        GROUP BY type
    """)
    all_types_popularity = cursor.fetchall()
    close_db(conn)

    if all_types_popularity:
        df = pd.DataFrame(all_types_popularity, columns=['Type', 'Popularity'])

        # Plot popularity as a horizontal bar chart
        plt.figure(figsize=(10, 6))
        plt.barh(df['Type'], df['Popularity'], color='lightcoral', edgecolor='black')
        plt.title("Bicycle Type Popularity Distribution")
        plt.xlabel("Popularity (Number of Rentals)")
        plt.ylabel("Bicycle Type")
        for i, popularity in enumerate(df['Popularity']):
            plt.text(popularity, i, str(popularity), va='center', fontsize=10)
        plt.show()

        most_popular_type = max(all_types_popularity, key=lambda x: x[1])
        print(f"Recommended Bicycle based on popularity: {most_popular_type[0]} ")
        return [{"Type": most_popular_type[0], "Popularity": most_popular_type[1]}]
    return []

# Purchase order recommendation based on budget
def recommend_purchase_order(budget):
    rental_freq_recs = recommend_by_rental_frequency()
    age_recs = recommend_by_age()
    condition_recs = recommend_by_condition()
    type_popularity_recs = recommend_by_type_popularity()

    # Combine all recommendations
    all_recommendations = rental_freq_recs + age_recs + condition_recs + type_popularity_recs
    
    # Count how many times each type appears across the recommendations
    bicycle_counts = Counter(rec.get('Type', rec.get('type')) for rec in all_recommendations)
    most_common_type, _ = bicycle_counts.most_common(1)[0]
    
    # Get the cost of the most common bicycle type
    cost = bicycle_costs.get(most_common_type, 0)

    # If the cost is within budget, calculate the units that can be bought
    if cost > 0 and cost <= budget:
        units = budget // cost
        recommendations = [{'type': most_common_type, 'units': int(units), 'cost_per_unit': cost, 'total_cost': units * cost}]
        
        # Plot the purchase order distribution
        plt.figure(figsize=(10, 6))
        plt.barh([rec['type'] for rec in recommendations], [rec['units'] for rec in recommendations], color='cornflowerblue')
        plt.title(f"Recommended Purchase Order (Budget: £{budget})")
        plt.xlabel("Bicycle Type")
        plt.ylabel("Units Recommended")
        for rec in recommendations:
            plt.text(rec['units'], rec['type'], f"£{rec['cost_per_unit']}/unit\nTotal: £{rec['total_cost']}", va='center')
        plt.show()
        
        return recommendations
    else:
        print(f"Recommended Bicycle: {most_common_type}")
        print(f"Cost per unit: £{cost}")
        print("Unfortunately, your budget is too low to purchase this bicycle.")
        print(f"To purchase at least 1 unit, you need at least £{cost}.")

    return []

# Testing the recommendation functions with graphs
# if __name__ == "__main__":
#     print("Bicycles recommended based on rental frequency:")
#     print(recommend_by_rental_frequency())

#     print("\nBicycles recommended based on age:")
#     print(recommend_by_age())

#     print("\nBicycles recommended based on condition:")
#     print(recommend_by_condition())

#     print("\nBicycles recommended based on type popularity:")
#     print(recommend_by_type_popularity())

#     print("\nFull Recommendation based on budget:")
#     print(recommend_purchase_order(1000))
