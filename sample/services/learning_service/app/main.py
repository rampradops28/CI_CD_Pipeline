from fastapi import FastAPI

app = FastAPI(title="CI/CD Learning API")

@app.get("/")
def read_root():
    return {"message": "Welcome to CI/CD Learning API", "status": "active"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
