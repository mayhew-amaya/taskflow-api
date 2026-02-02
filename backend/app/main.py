from fastapi import FastAPI
from app.routes import router
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(router)