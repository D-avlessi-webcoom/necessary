import sys
import os
import csv
import json
from datetime import datetime

def load_csv(file_path):
    """Load a CSV file and return its contents as a list of dictionaries"""
    print(f"Loading {file_path}...")
    data = []
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def main():
    print("\n===== Testing AI Module Prediction Data =====\n")
    
    # Load CSV files manually
    base_dir = 'extracted_data'
    annees = load_csv(os.path.join(base_dir, 'annees.csv'))
    communes = load_csv(os.path.join(base_dir, 'communes.csv'))
    donnees = load_csv(os.path.join(base_dir, 'donnees.csv'))
    
    if not annees or not communes or not donnees:
        print("Failed to load one or more required data files.")
        return
    
    # Get available years
    years = set()
    year_lookup = {}
    for row in annees:
        year = row.get('annee')
        if year:
            years.add(year)
            year_lookup[row.get('id')] = year
    
    print(f"Available years in the data: {sorted(years)}")
    
    # Get available communes
    commune_names = {}
    for row in communes:
        commune_id = row.get('id')
        commune_name = row.get('nom')
        if commune_id and commune_name:
            commune_names[commune_id] = commune_name
    
    print(f"\nSample communes (showing first 5):")
    for i, (commune_id, commune_name) in enumerate(list(commune_names.items())[:5]):
        print(f"{commune_id}: {commune_name}")
    
    # Get available indicators and years from donnees
    indicators = set()
    data_years = set()
    for row in donnees:
        indicator_id = row.get('indicateur_id')
        annee_id = row.get('annee_id')
        if indicator_id:
            indicators.add(indicator_id)
        if annee_id and annee_id in year_lookup:
            data_years.add(year_lookup[annee_id])
    
    print(f"\nAvailable indicators: {sorted(indicators)}")
    print(f"Years in data: {sorted(data_years)}")
    
    # Convert years to integers for prediction analysis
    int_years = [int(y) for y in data_years if y.isdigit()]
    
    if int_years:
        max_year = max(int_years)
        print(f"\nLatest year in data: {max_year}")
        print(f"Years that would be predicted (2-year forecast): {max_year+1}, {max_year+2}")
        print(f"Years that would be predicted (5-year forecast): {max_year+1}, {max_year+2}, {max_year+3}, {max_year+4}, {max_year+5}")
    
    # Manual prediction analysis for a specific commune and indicator
    test_commune_id = "1"  # Banikoara
    test_indicator_id = "1"  # First indicator
    
    print(f"\n\n===== Manual Prediction Analysis =====")
    print(f"For commune: {commune_names.get(test_commune_id, test_commune_id)} (ID: {test_commune_id})")
    print(f"For indicator ID: {test_indicator_id}")
    
    # Extract historical values for this commune and indicator
    historical_values = []
    for row in donnees:
        if (row.get('commune_id') == test_commune_id and 
            row.get('indicateur_id') == test_indicator_id):
            
            annee_id = row.get('annee_id')
            if annee_id in year_lookup:
                year = year_lookup[annee_id]
                if year.isdigit():
                    historical_values.append({
                        'year': int(year),
                        'value': float(row.get('valeur', 0))
                    })
    
    # Sort by year
    historical_values.sort(key=lambda x: x['year'])
    
    print("\nHistorical values:")
    for item in historical_values:
        print(f"Year: {item['year']}, Value: {item['value']}")
    
    # Simple linear trend for demonstration
    if len(historical_values) >= 2:
        # Calculate average yearly change
        total_change = historical_values[-1]['value'] - historical_values[0]['value']
        years_span = historical_values[-1]['year'] - historical_values[0]['year']
        
        if years_span > 0:
            avg_yearly_change = total_change / years_span
            
            # Project forward 5 years
            last_year = historical_values[-1]['year']
            last_value = historical_values[-1]['value']
            
            print("\nSimple linear projection (for demonstration):")
            for i in range(1, 6):
                projected_year = last_year + i
                projected_value = last_value + (avg_yearly_change * i)
                # Ensure values are within reasonable bounds
                if projected_value < 0:
                    projected_value = 0
                if projected_value > 100 and test_indicator_id in ["1", "5"]:  # Assuming these are percentage indicators
                    projected_value = 100
                    
                print(f"Projected Year: {projected_year}, Projected Value: {projected_value:.2f}")

if __name__ == "__main__":
    main()