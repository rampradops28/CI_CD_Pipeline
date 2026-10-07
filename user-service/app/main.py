from fastapi import FastAPI

app = FastAPI(title="User Service")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
