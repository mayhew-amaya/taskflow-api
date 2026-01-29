from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="TaskFlow API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(router)