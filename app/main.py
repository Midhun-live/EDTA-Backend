from fastapi import FastAPI, APIRouter
from app.api.assessment import router as assessment_router

app = FastAPI(
    title="EDTA Backend",
    version="0.1.0"
)

app.include_router(assessment_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}