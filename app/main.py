from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.assessment import router as assessment_router, share_router
from app.api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="EDTA Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://edta-frontend-39ac.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(assessment_router)
app.include_router(share_router)
app.include_router(auth_router)