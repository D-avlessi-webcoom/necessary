import orjson
from fastapi.responses import ORJSONResponse
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import uvicorn
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Add the directory containing ai_module.py to the Python path
sys.path.append('./')

# Import the AIModule class
from ai_module import AIModule

# Initialize the FastAPI app
app = FastAPI(
    title="SID Platform AI Module API",
    description="API for predicting indicators and clustering communes in the SID Platform",
    version="1.0.0"
)

# Add CORS middleware to allow requests from the Laravel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the AI Module
ai_module = None

# Models for request and response
class PredictionRequest(BaseModel):
    years_to_predict: int
    commune_ids: Optional[List[int]] = None
    indicator_ids: Optional[List[int]] = None

class ClusteringRequest(BaseModel):
    n_clusters: Optional[int] = None
    max_clusters: Optional[int] = 10

class APIResponse(BaseModel):
    success: bool
    data: Any
    message: str
    timestamp: str

# Dependency to ensure AI module is loaded
async def get_ai_module():
    global ai_module
    if ai_module is None:
        ai_module = AIModule(data_dir='./extracted_data')
        ai_module.load_data()
    return ai_module

# Root endpoint
@app.get("/", response_model=APIResponse)
async def root():
    return {
        "success": True,
        "data": {
            "name": "SID Platform AI Module API",
            "version": "1.0.0",
            "status": "running"
        },
        "message": "API is operational",
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health", response_model=APIResponse)
async def health_check():
    try:
        ai = await get_ai_module()
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "communes_count": len(ai.data['communes']),
                "years_available": sorted(ai.data['donnees']['year'].unique().tolist()),
                "indicators_count": len(ai.data['donnees']['indicateur_id'].unique())
            },
            "message": "System is healthy",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": f"System is unhealthy: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Get available communes endpoint
@app.get("/communes", response_model=APIResponse)
async def get_communes(ai: AIModule = Depends(get_ai_module)):
    try:
        communes_df = ai.data['communes']
        cleaned_communes_df = communes_df.replace({np.nan: None, np.inf: None, -np.inf: None}).copy()
        communes = cleaned_communes_df.to_dict(orient='records')

        response_data = {
            "success": True,
            "data": communes,
            "message": f"Successfully retrieved {len(communes)} communes",
            "timestamp": datetime.now().isoformat()
        }
        # Use ORJSONResponse instead of default JSONResponse
        return ORJSONResponse(content=response_data) # Ensure APIResponse model is compatible if used

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving commun

# Get available indicators endpoint
@app.get("/indicators", response_model=APIResponse)
async def get_indicators(ai: AIModule = Depends(get_ai_module)):
    try:
        # Load indicators from the CSV file
        indicators_file_path = os.path.join('./extracted_data', 'indicateurs.csv')
        # Using on_bad_lines='skip' to handle problematic rows
        indicators_df = pd.read_csv(indicators_file_path, on_bad_lines='skip')
        
        indicators = ai.data['donnees']['indicateur_id'].unique()
        
        # Create a mapping from indicator ID to name
        indicator_names = {}
        for _, row in indicators_df.iterrows():
            indicator_names[row['id']] = row['nom']
        
        indicator_list = [
            {
                "id": int(ind),
                "name": indicator_names.get(int(ind), f"Indicateur {ind}")
            } 
            for ind in sorted(indicators)
        ]
        
        return {
            "success": True,
            "data": indicator_list,
            "message": f"Successfully retrieved {len(indicator_list)} indicators",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving indicators: {str(e)}")

# Get available years endpoint
@app.get("/years", response_model=APIResponse)
async def get_years(ai: AIModule = Depends(get_ai_module)):
    try:
        years = sorted(ai.data['donnees']['year'].unique().tolist())
        return {
            "success": True,
            "data": years,
            "message": f"Successfully retrieved {len(years)} years",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving years: {str(e)}")

# Predict indicators endpoint
@app.post("/predict", response_model=APIResponse)
async def predict_indicators(request: PredictionRequest, ai: AIModule = Depends(get_ai_module)):
    try:
        # Validate input
        if request.years_to_predict <= 0:
            raise HTTPException(status_code=400, detail="Years to predict must be positive")
        if request.years_to_predict > 10:
            raise HTTPException(status_code=400, detail="Years to predict cannot exceed 10")

        # Get predictions
        predictions = ai.predict_indicators(
            years_to_predict=request.years_to_predict,
            communes=request.commune_ids
        )
        
        # Filter by indicator IDs if provided
        if request.indicator_ids:
            predictions = predictions[predictions['indicateur_id'].isin(request.indicator_ids)]
        
        # Convert to records for JSON serialization
        predictions_list = predictions.to_dict(orient='records')
        
        # Get historical data for context
        communes = request.commune_ids if request.commune_ids else ai.data['communes']['id'].unique()
        indicator_filter = request.indicator_ids if request.indicator_ids else None
        
        historical_data = ai.data['donnees']
        historical_data = historical_data[historical_data['commune_id'].isin(communes)]
        
        if indicator_filter:
            historical_data = historical_data[historical_data['indicateur_id'].isin(indicator_filter)]
        
        historical_list = historical_data[['commune_id', 'indicateur_id', 'year', 'valeur']].rename(
            columns={'valeur': 'predicted_value'}
        ).assign(is_prediction=False).to_dict(orient='records')
        
        # Combine historical and predicted data
        combined_data = historical_list + predictions_list
        
        return {
            "success": True,
            "data": {
                "predictions": combined_data,
                "years_predicted": request.years_to_predict,
                "communes": list(communes),
                "indicators": request.indicator_ids if request.indicator_ids else list(ai.data['donnees']['indicateur_id'].unique())
            },
            "message": f"Successfully generated predictions for {len(predictions)} data points",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")

# Clustering endpoint
@app.post("/cluster", response_model=APIResponse)
async def cluster_communes(request: ClusteringRequest, ai: AIModule = Depends(get_ai_module)):
    try:
        # Perform clustering
        clusters = ai.cluster_communes(n_clusters=request.n_clusters, max_clusters=request.max_clusters)
        
        # Get cluster characteristics
        characteristics = ai.get_cluster_characteristics()
        
        # Process indicator names for better readability
        # Load indicators from the CSV file
        indicators_file_path = os.path.join('./extracted_data', 'indicateurs.csv')
        # Using on_bad_lines='skip' to handle problematic rows
        indicators_df = pd.read_csv(indicators_file_path, on_bad_lines='skip')
        
        # Create a mapping from indicator ID to name
        indicator_names = {}
        for _, row in indicators_df.iterrows():
            indicator_names[row['id']] = row['nom']
        
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
        commune_names = dict(zip(ai.data['communes']['id'], ai.data['communes']['nom']))
        clusters_with_names = []
        
        for i, commune_id in enumerate(clusters['commune_ids']):
            clusters_with_names.append({
                'commune_id': commune_id,
                'commune_name': commune_names.get(commune_id, str(commune_id)),
                'cluster': clusters['cluster_labels'][i]
            })
        
        return {
            "success": True,
            "data": {
                "clusters": clusters,
                "characteristics": characteristics,
                "communes_with_clusters": clusters_with_names,
                "n_clusters": clusters['n_clusters']
            },
            "message": f"Successfully clustered communes into {clusters['n_clusters']} groups",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clustering communes: {str(e)}")

# Get dashboard data endpoint (combines predictions and clustering)
@app.get("/dashboard", response_model=APIResponse)
async def get_dashboard_data(
    years_to_predict: int = Query(2, ge=1, le=10),
    ai: AIModule = Depends(get_ai_module)
):
    try:
        # Get dashboard data
        dashboard_data = ai.prepare_dashboard_data(years_to_predict=years_to_predict)
        
        return {
            "success": True,
            "data": dashboard_data,
            "message": "Successfully generated dashboard data",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard data: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
