from api import app

if __name__ == "__main__":
    import gunicorn
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app -b 0.0.0.0:8080