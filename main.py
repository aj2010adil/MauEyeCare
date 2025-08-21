from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from config import settings
from database import create_start_app_handler, create_stop_app_handler
from auth import router as auth_router
from patients import router as patients_router
from visits import router as visits_router
from prescriptions import router as prescriptions_router
from dashboard import router as dashboard_router
from insights import router as insights_router
from pos_router import router as pos_router
from lab_router import router as lab_router
from consent_router import router as consent_router
from system import router as system_router
from inventory import router as inventory_router
from ai_router import router as ai_router


app = FastAPI(title="MauEyeCare API", description="Local clinic management system", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", create_start_app_handler(app))
app.add_event_handler("shutdown", create_stop_app_handler(app))

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(patients_router, prefix="/api/patients", tags=["patients"])
app.include_router(visits_router, prefix="/api/visits", tags=["visits"])
app.include_router(prescriptions_router, prefix="/api/prescriptions", tags=["prescriptions"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(insights_router, prefix="/api/insights", tags=["insights"])
app.include_router(pos_router, prefix="/api/pos", tags=["pos"])
app.include_router(lab_router, prefix="/api/lab", tags=["lab"])
app.include_router(consent_router, prefix="/api/consents", tags=["consents"])
app.include_router(system_router, prefix="/api/system", tags=["system"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["inventory"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])

# Mount static files for uploads
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}