# Project Summary
This project aims to develop an AI module integrated with a Laravel platform, facilitating the prediction of digitalization indicators in municipalities and enabling automatic clustering of these municipalities based on their profiles. The project leverages a Streamlit interface for testing the AI functionalities, which include visualizing results through simple graphs.

# Project Module Description
The project consists of several key modules:
- **AI Module**: Predicts the evolution of numeric indicators and clusters municipalities using unsupervised clustering techniques.
- **API Module**: Provides endpoints for the AI functionalities, allowing Laravel integration.
- **Streamlit Interface**: A user-friendly interface for testing and visualizing the AI module's capabilities.

# Directory Tree
```
.
├── Dockerfile                 # Docker configuration for containerized deployment
├── api.py                     # FastAPI implementation for AI functionalities
├── api_documentation.md       # Documentation for API endpoints and usage
├── docker-compose.yml         # Docker Compose file for multi-container deployment
├── integration_guide.md       # Guide for Laravel developers to integrate the API
├── requirements.txt           # Python dependencies for the API
├── simple_api.py              # Simplified API implementation without FastAPI
└── uploads                    # Directory containing various data and dashboard files
    ├── ai_module.py          # AI module implementation
    ├── dashboard              # Frontend dashboard files
    └── extracted_data         # Data files used by the AI module
```

# File Description Inventory
- **Dockerfile**: Defines the environment for the application.
- **api.py**: Main API file using FastAPI to handle requests for predictions and clustering.
- **api_documentation.md**: Comprehensive documentation of the API, including endpoints and expected responses.
- **docker-compose.yml**: Configuration for running multiple services with Docker.
- **integration_guide.md**: Step-by-step instructions for integrating the API with Laravel.
- **requirements.txt**: Lists all Python packages required to run the API.
- **simple_api.py**: A simpler implementation of the API for compatibility issues.
- **uploads/**: Contains AI module code, data files, and a dashboard for visualization.

# Technology Stack
- **Backend**: Python with FastAPI (and Flask for simple API)
- **Frontend**: Streamlit for the user interface
- **Data Storage**: CSV and JSON files for data handling
- **Containerization**: Docker and Docker Compose for deployment

# Usage
1. **Install Dependencies**: Run `pip install -r requirements.txt` to install necessary Python packages.
2. **Run the API**:
   - For FastAPI: Execute `python api.py` or `python simple_api.py` for a simplified version.
   - For Docker: Use `docker-compose up -d` to start the application in a containerized environment.
