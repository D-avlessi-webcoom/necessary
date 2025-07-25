import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import pandas as pd
import numpy as np
from datetime import datetime

# Add the directory containing ai_module.py to the Python path
sys.path.append('/workspace/uploads')

# Import the AIModule class
from ai_module import AIModule

# Initialize the AI Module
ai_module = AIModule(data_dir='./extracted_data')
ai_module.load_data()

class SimpleAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def _set_error_headers(self, status_code=400):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def _create_response(self, success, data, message):
        return json.dumps({
            "success": success,
            "data": data,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }).encode('utf-8')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type, Authorization")
        self.end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            # Root endpoint
            if path == '/':
                self._set_headers()
                response = self._create_response(
                    True,
                    {
                        "name": "SID Platform AI Module API",
                        "version": "1.0.0",
                        "status": "running"
                    },
                    "API is operational"
                )
                self.wfile.write(response)
            
            # Health check endpoint
            elif path == '/health':
                self._set_headers()
                response = self._create_response(
                    True,
                    {
                        "status": "healthy",
                        "communes_count": len(ai_module.data['communes']),
                        "years_available": sorted(ai_module.data['donnees']['year'].unique().tolist()),
                        "indicators_count": len(ai_module.data['donnees']['indicateur_id'].unique())
                    },
                    "System is healthy"
                )
                self.wfile.write(response)
            
            # Get communes endpoint
            elif path == '/communes':
                self._set_headers()
                communes = ai_module.data['communes'].to_dict(orient='records')
                response = self._create_response(
                    True,
                    communes,
                    f"Successfully retrieved {len(communes)} communes"
                )
                self.wfile.write(response)
            
            # Get indicators endpoint
            elif path == '/indicators':
                self._set_headers()
                # Create indicator options with descriptive names
                indicator_names = {
                    1: "Nombre de sessions ordinaires du conseil municipal",
                    2: "Taux de participation aux sessions",
                    3: "Taux d'exécution du budget",
                    4: "Nombre de services en ligne",
                    5: "Présence sur les réseaux sociaux",
                    6: "Fréquence de mise à jour du site web",
                    7: "Taux d'utilisation des services numériques",
                    8: "Nombre de consultations publiques en ligne",
                    9: "Taux d'informatisation des procédures administratives",
                    10: "Indice de satisfaction citoyenne"
                }
                
                indicators = ai_module.data['donnees']['indicateur_id'].unique()
                indicator_list = [
                    {
                        "id": int(ind),
                        "name": indicator_names.get(int(ind), f"Indicateur {ind}")
                    } 
                    for ind in sorted(indicators)
                ]
                
                response = self._create_response(
                    True,
                    indicator_list,
                    f"Successfully retrieved {len(indicator_list)} indicators"
                )
                self.wfile.write(response)
            
            # Get years endpoint
            elif path == '/years':
                self._set_headers()
                years = sorted(ai_module.data['donnees']['year'].unique().tolist())
                response = self._create_response(
                    True,
                    years,
                    f"Successfully retrieved {len(years)} years"
                )
                self.wfile.write(response)
            
            # Get dashboard data endpoint
            elif path == '/dashboard':
                self._set_headers()
                query_params = parse_qs(parsed_path.query)
                years_to_predict = int(query_params.get('years_to_predict', ['2'])[0])
                
                if years_to_predict <= 0 or years_to_predict > 10:
                    self._set_error_headers()
                    response = self._create_response(
                        False,
                        None,
                        "Years to predict must be between 1 and 10"
                    )
                    self.wfile.write(response)
                    return
                
                dashboard_data = ai_module.prepare_dashboard_data(years_to_predict=years_to_predict)
                response = self._create_response(
                    True,
                    dashboard_data,
                    "Successfully generated dashboard data"
                )
                self.wfile.write(response)
            
            else:
                self._set_error_headers(404)
                response = self._create_response(
                    False,
                    None,
                    f"Endpoint not found: {path}"
                )
                self.wfile.write(response)
                
        except Exception as e:
            self._set_error_headers(500)
            response = self._create_response(
                False,
                None,
                f"Internal server error: {str(e)}"
            )
            self.wfile.write(response)
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Predict indicators endpoint
            if path == '/predict':
                years_to_predict = request_data.get('years_to_predict', 2)
                commune_ids = request_data.get('commune_ids', None)
                indicator_ids = request_data.get('indicator_ids', None)
                # Add support for specifying start_year
                start_year = request_data.get('start_year', None)
                
                if years_to_predict <= 0 or years_to_predict > 10:
                    self._set_error_headers()
                    response = self._create_response(
                        False,
                        None,
                        "Years to predict must be between 1 and 10"
                    )
                    self.wfile.write(response)
                    return
                
                # Get predictions with optional start_year parameter
                predictions = ai_module.predict_indicators(
                    years_to_predict=years_to_predict,
                    communes=commune_ids,
                    start_year=start_year
                )
                
                # Filter by indicator IDs if provided
                if indicator_ids:
                    predictions = predictions[predictions['indicateur_id'].isin(indicator_ids)]
                
                # Convert to records for JSON serialization and ensure int64 objects are converted to int
                predictions_list = json.loads(predictions.to_json(orient='records'))
                
                # Get historical data for context
                communes = commune_ids if commune_ids else ai_module.data['communes']['id'].unique()
                
                historical_data = ai_module.data['donnees']
                historical_data = historical_data[historical_data['commune_id'].isin(communes)]
                
                if indicator_ids:
                    historical_data = historical_data[historical_data['indicateur_id'].isin(indicator_ids)]
                
                historical_list = json.loads(
                    historical_data[['commune_id', 'indicateur_id', 'year', 'valeur']].rename(
                        columns={'valeur': 'predicted_value'}
                    ).assign(is_prediction=False).to_json(orient='records')
                )
                
                # Combine historical and predicted data
                combined_data = historical_list + predictions_list
                
                self._set_headers()
                response = self._create_response(
                    True,
                    {
                        "predictions": combined_data,
                        "years_predicted": years_to_predict,
                        "communes": [int(x) for x in communes],
                        "indicators": indicator_ids if indicator_ids else [int(x) for x in ai_module.data['donnees']['indicateur_id'].unique()]
                    },
                    f"Successfully generated predictions for {len(predictions)} data points"
                )
                self.wfile.write(response)
            
            # Clustering endpoint
            elif path == '/cluster':
                n_clusters = request_data.get('n_clusters', None)
                max_clusters = request_data.get('max_clusters', 10)
                
                # Perform clustering
                clusters = ai_module.cluster_communes(n_clusters=n_clusters, max_clusters=max_clusters)
                
                # Get cluster characteristics
                characteristics = ai_module.get_cluster_characteristics()
                
                # Process indicator names for better readability
                indicator_names = {
                    1: "Nombre de sessions ordinaires du conseil municipal",
                    2: "Taux de participation aux sessions",
                    3: "Taux d'exécution du budget",
                    4: "Nombre de services en ligne",
                    5: "Présence sur les réseaux sociaux",
                    6: "Fréquence de mise à jour du site web",
                    7: "Taux d'utilisation des services numériques",
                    8: "Nombre de consultations publiques en ligne",
                    9: "Taux d'informatisation des procédures administratives",
                    10: "Indice de satisfaction citoyenne"
                }
                
                # Process distinctive indicators to include names
                for cluster_id, data in characteristics['distinctive_indicators'].items():
                    top_indicators_with_names = []
                    for ind in data['top_indicators']:
                        top_indicators_with_names.append({
                            'id': ind,
                            'name': indicator_names.get(ind, f"Indicateur {ind}"),
                            'value': data['mean_values'][ind]
                        })
                    characteristics['distinctive_indicators'][cluster_id]['top_indicators_with_names'] = top_indicators_with_names
                
                # Add commune names to cluster results
                commune_names = dict(zip(ai_module.data['communes']['id'], ai_module.data['communes']['nom']))
                clusters_with_names = []
                
                for i, commune_id in enumerate(clusters['commune_ids']):
                    clusters_with_names.append({
                        'commune_id': commune_id,
                        'commune_name': commune_names.get(commune_id, str(commune_id)),
                        'cluster': clusters['cluster_labels'][i]
                    })
                
                self._set_headers()
                response = self._create_response(
                    True,
                    {
                        "clusters": clusters,
                        "characteristics": characteristics,
                        "communes_with_clusters": clusters_with_names,
                        "n_clusters": clusters['n_clusters']
                    },
                    f"Successfully clustered communes into {clusters['n_clusters']} groups"
                )
                self.wfile.write(response)
            
            else:
                self._set_error_headers(404)
                response = self._create_response(
                    False,
                    None,
                    f"Endpoint not found: {path}"
                )
                self.wfile.write(response)
                
        except Exception as e:
            self._set_error_headers(500)
            response = self._create_response(
                False,
                None,
                f"Internal server error: {str(e)}"
            )
            self.wfile.write(response)


def run(server_class=HTTPServer, handler_class=SimpleAPIHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")


if __name__ == "__main__":
    run()