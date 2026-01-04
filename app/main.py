from fastapi import FastAPI
from app.api.assessment import router as assessment_router
from app.api.auth import router as auth_router


app = FastAPI(
    title="EDTA Backend",
    version="1.0.0"
)

app.include_router(assessment_router)
app.include_router(auth_router)