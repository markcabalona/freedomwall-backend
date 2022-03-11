import uvicorn
from freedomwall_app import app


if __name__ == "__main__":
    uvicorn.run("freedomwall_app:app", reload=True)
    # uvicorn.run("freedomwall_app:app",host = '0.0.0.0',reload=True)
