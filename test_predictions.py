import sys
import os
import pandas as pd
from ai_module import AIModule

def main():
    print("\n===== Testing AI Module Prediction Functionality =====\n")
    
    # Initialize the AI Module with the correct data directory
    print("Initializing AI Module...")
    ai_module = AIModule(data_dir='extracted_data')
    
    # Load the data
    print("Loading data...")
    success = ai_module.load_data()
    if not success:
        print("Failed to load data. Check the data directory.")
        return
    
    # Get available years
    years = sorted(ai_module.data['donnees']['year'].unique().tolist())
    print(f"Available years in the data: {years}")
    
    # Get available communes
    communes = ai_module.data['communes'][['id', 'nom']]
    print(f"\nSample communes (showing first 5):")
    print(communes.head())
    
    # Get available indicators
    indicators = ai_module.data['donnees']['indicateur_id'].unique()
    print(f"\nAvailable indicators: {sorted(indicators)}")
    
    # Test prediction for 2 years ahead for specific communes
    test_communes = [1, 2]  # Banikoara and Gogounou
    years_to_predict = 2
    print(f"\n\n===== Testing Prediction for {years_to_predict} years ahead =====")
    print(f"Predicting for communes: {test_communes}")
    
    predictions = ai_module.predict_indicators(
        years_to_predict=years_to_predict,
        communes=test_communes
    )
    
    if predictions.empty:
        print("No predictions were generated.")
    else:
        print(f"\nGenerated {len(predictions)} predictions.")
        print("\nSample predictions (showing first 10 rows):")
        pd.set_option('display.max_columns', None)
        print(predictions.head(10))
        
        # Show predicted years
        pred_years = predictions['year'].unique()
        print(f"\nYears predicted: {sorted(pred_years)}")
        
    # Test prediction for 5 years ahead
    years_to_predict = 5
    print(f"\n\n===== Testing Prediction for {years_to_predict} years ahead =====")
    
    predictions = ai_module.predict_indicators(
        years_to_predict=years_to_predict,
        communes=test_communes
    )
    
    if predictions.empty:
        print("No predictions were generated.")
    else:
        print(f"\nGenerated {len(predictions)} predictions.")
        print(f"\nYears predicted: {sorted(predictions['year'].unique())}")
        
    # Test prediction for specific indicators
    test_indicators = [1, 2, 3]  # First three indicators
    years_to_predict = 3
    print(f"\n\n===== Testing Prediction for specific indicators =====")
    print(f"Predicting for indicators: {test_indicators}")
    
    predictions = ai_module.predict_indicators(
        years_to_predict=years_to_predict,
        communes=test_communes
    )
    
    # Filter predictions for the test indicators
    filtered_predictions = predictions[predictions['indicateur_id'].isin(test_indicators)]
    
    if filtered_predictions.empty:
        print("No predictions were generated for the specified indicators.")
    else:
        print(f"\nGenerated {len(filtered_predictions)} predictions for the specified indicators.")
        print("\nSample indicator predictions (showing first 10 rows):")
        print(filtered_predictions.head(10))

    # Test dashboard data preparation
    print("\n\n===== Testing Dashboard Data Preparation =====")
    try:
        dashboard_data = ai_module.prepare_dashboard_data(years_to_predict=2)
        print("Dashboard data prepared successfully.")
        print(f"Years included in dashboard: {dashboard_data['years']}")
        print(f"Number of communes included: {len(dashboard_data['communes'])}")
        print(f"Number of indicators included: {len(dashboard_data['indicators'])}")
        print(f"Number of data points: {len(dashboard_data['indicator_data'])}")
    except Exception as e:
        print(f"Failed to prepare dashboard data: {e}")

if __name__ == "__main__":
    main()