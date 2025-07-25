import os
import sys
import csv
import json
import requests
from datetime import datetime
import http.server
import socketserver
import threading
import time

class MockLaravelClient:
    """Simulates a Laravel client making requests to the AI Module"""
    
    def __init__(self, api_url="http://localhost:8080"):
        self.api_url = api_url
        
    def health_check(self):
        """Simulates the AIModuleService.getHealth() method in Laravel"""
        print(f"[Laravel Client] Checking API health at {self.api_url}/health")
        # Since we can't actually connect to an API, we'll use our local data
        return self._simulate_api_response("health")
    
    def get_communes(self):
        """Simulates the AIModuleService.getCommunes() method in Laravel"""
        print(f"[Laravel Client] Getting communes from {self.api_url}/communes")
        return self._simulate_api_response("communes")
    
    def get_indicators(self):
        """Simulates the AIModuleService.getIndicators() method in Laravel"""
        print(f"[Laravel Client] Getting indicators from {self.api_url}/indicators")
        return self._simulate_api_response("indicators")
        
    def predict_indicators(self, years_to_predict, commune_ids=None, indicator_ids=None):
        """Simulates the AIModuleService.predictIndicators() method in Laravel"""
        print(f"[Laravel Client] Predicting indicators for {years_to_predict} years")
        if commune_ids:
            print(f"   - For communes: {commune_ids}")
        if indicator_ids:
            print(f"   - For indicators: {indicator_ids}")
        
        return self._simulate_api_response("predict", {
            'years_to_predict': years_to_predict,
            'commune_ids': commune_ids,
            'indicator_ids': indicator_ids
        })
    
    def cluster_communes(self, n_clusters=None, max_clusters=None):
        """Simulates the AIModuleService.clusterCommunes() method in Laravel"""
        print(f"[Laravel Client] Clustering communes")
        return self._simulate_api_response("cluster", {
            'n_clusters': n_clusters,
            'max_clusters': max_clusters
        })
    
    def get_dashboard_data(self, years_to_predict=2):
        """Simulates the AIModuleService.getDashboardData() method in Laravel"""
        print(f"[Laravel Client] Getting dashboard data with {years_to_predict} years prediction")
        return self._simulate_api_response("dashboard", {
            'years_to_predict': years_to_predict
        })
    
    def _simulate_api_response(self, endpoint, payload=None):
        """Simulate API responses using local data files"""
        # Load the necessary data files
        base_dir = 'extracted_data'
        
        try:
            annees = self._load_csv(os.path.join(base_dir, 'annees.csv'))
            communes = self._load_csv(os.path.join(base_dir, 'communes.csv'))
            donnees = self._load_csv(os.path.join(base_dir, 'donnees.csv'))
            
            # Build responses based on endpoint
            if endpoint == "health":
                years = set()
                for row in annees:
                    if 'annee' in row:
                        years.add(row['annee'])
                
                return {
                    "success": True,
                    "data": {
                        "status": "healthy",
                        "communes_count": len(communes),
                        "years_available": sorted(years),
                        "indicators_count": len(set(row.get('indicateur_id') for row in donnees))
                    },
                    "message": "System is healthy",
                    "timestamp": datetime.now().isoformat()
                }
                
            elif endpoint == "communes":
                return {
                    "success": True,
                    "data": communes,
                    "message": f"Successfully retrieved {len(communes)} communes",
                    "timestamp": datetime.now().isoformat()
                }
                
            elif endpoint == "indicators":
                # Create indicator options with descriptive names as shown in the API
                indicator_names = {
                    "1": "Nombre de sessions ordinaires du conseil municipal",
                    "2": "Taux de participation aux sessions",
                    "3": "Taux d'exécution du budget",
                    "4": "Nombre de services en ligne",
                    "5": "Présence sur les réseaux sociaux",
                    "6": "Fréquence de mise à jour du site web",
                    "7": "Taux d'utilisation des services numériques",
                    "8": "Nombre de consultations publiques en ligne",
                    "9": "Taux d'informatisation des procédures administratives",
                    "10": "Indice de satisfaction citoyenne"
                }
                
                indicators = set(row.get('indicateur_id') for row in donnees if row.get('indicateur_id'))
                indicator_list = [
                    {
                        "id": int(ind),
                        "name": indicator_names.get(ind, f"Indicateur {ind}")
                    } 
                    for ind in sorted(indicators)
                ]
                
                return {
                    "success": True,
                    "data": indicator_list,
                    "message": f"Successfully retrieved {len(indicator_list)} indicators",
                    "timestamp": datetime.now().isoformat()
                }
                
            elif endpoint == "predict":
                # Simulated prediction logic
                years_to_predict = payload.get('years_to_predict', 2)
                commune_ids = payload.get('commune_ids')
                indicator_ids = payload.get('indicator_ids')
                
                # Get the latest year in the data
                year_lookup = {}
                for row in annees:
                    if 'id' in row and 'annee' in row and row['annee'].isdigit():
                        year_lookup[row['id']] = int(row['annee'])
                
                max_year = max(year_lookup.values())
                
                # Generate predictions
                predictions = []
                
                # If no communes specified, use all communes
                if not commune_ids:
                    commune_ids = [row['id'] for row in communes]
                
                # Filter indicators if specified
                available_indicators = set(row.get('indicateur_id') for row in donnees if row.get('indicateur_id'))
                if indicator_ids:
                    indicators_to_predict = [str(i) for i in indicator_ids if str(i) in available_indicators]
                else:
                    indicators_to_predict = list(available_indicators)
                
                # Get historical data to simulate trends
                historical_data = {}
                for row in donnees:
                    commune_id = row.get('commune_id')
                    indicator_id = row.get('indicateur_id')
                    annee_id = row.get('annee_id')
                    
                    if commune_id and indicator_id and annee_id and annee_id in year_lookup:
                        key = f"{commune_id}_{indicator_id}"
                        if key not in historical_data:
                            historical_data[key] = []
                            
                        historical_data[key].append({
                            'year': year_lookup[annee_id],
                            'value': float(row.get('valeur', 0))
                        })
                
                # Generate predictions for future years
                for commune_id in commune_ids:
                    for indicator_id in indicators_to_predict:
                        key = f"{commune_id}_{indicator_id}"
                        if key in historical_data:
                            # Sort by year
                            values = sorted(historical_data[key], key=lambda x: x['year'])
                            
                            if len(values) >= 2:
                                # Simple linear projection
                                last_year = values[-1]['year']
                                last_value = values[-1]['value']
                                total_change = values[-1]['value'] - values[0]['value']
                                years_span = values[-1]['year'] - values[0]['year']
                                
                                # Avoid division by zero
                                avg_yearly_change = 0
                                if years_span > 0:
                                    avg_yearly_change = total_change / years_span
                                
                                # Generate predictions for future years
                                for i in range(1, years_to_predict + 1):
                                    predicted_year = last_year + i
                                    predicted_value = last_value + (avg_yearly_change * i)
                                    
                                    # Ensure values are within reasonable bounds
                                    if predicted_value < 0:
                                        predicted_value = 0
                                    if predicted_value > 100 and indicator_id in ["1", "2", "5", "8"]:
                                        predicted_value = 100
                                    
                                    predictions.append({
                                        'commune_id': commune_id,
                                        'indicateur_id': indicator_id,
                                        'year': predicted_year,
                                        'predicted_value': round(predicted_value, 2),
                                        'is_prediction': True
                                    })
                
                # For context, include historical data as well
                historical_list = []
                for key, values in historical_data.items():
                    commune_id, indicator_id = key.split('_')
                    
                    # Only include if in the requested communes and indicators
                    if commune_id in commune_ids and indicator_id in indicators_to_predict:
                        for item in values:
                            historical_list.append({
                                'commune_id': commune_id,
                                'indicateur_id': indicator_id,
                                'year': item['year'],
                                'predicted_value': item['value'],
                                'is_prediction': False
                            })
                
                # Combine historical and predicted data
                combined_data = historical_list + predictions
                
                return {
                    "success": True,
                    "data": {
                        "predictions": combined_data,
                        "years_predicted": years_to_predict,
                        "communes": commune_ids,
                        "indicators": indicators_to_predict
                    },
                    "message": f"Successfully generated predictions for {len(predictions)} data points",
                    "timestamp": datetime.now().isoformat()
                }
                
            elif endpoint == "dashboard":
                # This would be a combination of predictions and clustering
                # For simplicity, we'll just return a basic structure
                years_to_predict = payload.get('years_to_predict', 2)
                
                # First get predictions
                predictions_response = self._simulate_api_response("predict", {'years_to_predict': years_to_predict})
                
                return {
                    "success": True,
                    "data": {
                        "indicator_data": predictions_response['data']['predictions'],
                        "communes": communes,
                        "years": sorted(set(item['year'] for item in predictions_response['data']['predictions'])),
                        "indicators": sorted(set(int(item['indicateur_id']) for item in predictions_response['data']['predictions']))
                    },
                    "message": "Successfully generated dashboard data",
                    "timestamp": datetime.now().isoformat()
                }
            
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Endpoint {endpoint} not implemented in simulation",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Error simulating API response: {e}")
            return {
                "success": False,
                "data": None,
                "message": f"Error simulating API response: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _load_csv(self, file_path):
        """Load a CSV file and return its contents as a list of dictionaries"""
        data = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return data
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []


def test_laravel_integration():
    """Test the Laravel integration by simulating API calls"""
    print("\n===== TESTING LARAVEL INTEGRATION =====\n")
    
    client = MockLaravelClient()
    
    # Test 1: Health Check
    print("\n=== Test 1: Health Check ===")
    health_response = client.health_check()
    print(json.dumps(health_response, indent=2))
    
    # Test 2: Get Communes
    print("\n=== Test 2: Get Communes ===")
    communes_response = client.get_communes()
    print(f"Retrieved {len(communes_response['data'])} communes")
    if communes_response['data']:
        print("Sample communes:")
        for commune in communes_response['data'][:5]:
            print(f"  - {commune['id']}: {commune['nom']}")
    
    # Test 3: Get Indicators
    print("\n=== Test 3: Get Indicators ===")
    indicators_response = client.get_indicators()
    print(f"Retrieved {len(indicators_response['data'])} indicators")
    if indicators_response['data']:
        print("Sample indicators:")
        for indicator in indicators_response['data'][:5]:
            print(f"  - {indicator['id']}: {indicator['name']}")
    
    # Test 4: Predict Indicators (2 years)
    print("\n=== Test 4: Predict Indicators (2 years) ===")
    predict_response = client.predict_indicators(years_to_predict=2, commune_ids=["1", "2"], indicator_ids=["1", "2", "3"])
    
    if predict_response['success']:
        predictions = predict_response['data']['predictions']
        years_predicted = predict_response['data']['years_predicted']
        print(f"Successfully predicted for {years_predicted} years")
        print(f"Total data points: {len(predictions)}")
        
        # Show predictions for specific commune and indicator
        test_commune = "1"
        test_indicator = "1"
        
        print(f"\nPredictions for Commune {test_commune}, Indicator {test_indicator}:")
        filtered = [p for p in predictions if p['commune_id'] == test_commune and p['indicateur_id'] == test_indicator]
        filtered.sort(key=lambda x: x['year'])
        
        for item in filtered:
            is_pred = "PREDICTION" if item['is_prediction'] else "Historical"
            print(f"  - Year {item['year']}: {item['predicted_value']} ({is_pred})")
    
    # Test 5: Dashboard Data
    print("\n=== Test 5: Dashboard Data ===")
    dashboard_response = client.get_dashboard_data(years_to_predict=3)
    
    if dashboard_response['success']:
        dashboard_data = dashboard_response['data']
        print(f"Dashboard data generated successfully")
        print(f"  - Years included: {dashboard_data['years']}")
        print(f"  - Communes: {len(dashboard_data['communes'])}")
        print(f"  - Indicators: {len(dashboard_data['indicators'])}")
        print(f"  - Total data points: {len(dashboard_data['indicator_data'])}")
    
    print("\n===== LARAVEL INTEGRATION TESTING COMPLETE =====")
    



if __name__ == "__main__":
    test_laravel_integration()