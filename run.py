import uvicorn
from freedomwall_app import app


if __name__ == "__main__":
    # uvicorn.run(app)
    uvicorn.run(app,host = '0.0.0.0')