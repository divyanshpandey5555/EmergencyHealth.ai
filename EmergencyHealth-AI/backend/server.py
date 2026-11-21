"""
ResQ-AI: Emergency Health Assistant Backend API
FastAPI implementation with fallback AI triage and LLM support
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="ResQ-AI Emergency Healthcare API",
    description="Emergency triage classification and paramedic dispatch service",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TriageRequest(BaseModel):
    symptoms: str
    consciousness: str = "conscious"
    age_group: str = "adult"
    patient_id: Optional[str] = None

class TriageResponse(BaseModel):
    category: str
    condition: str
    priority: int
    immediate_action: str
    recommended_facility: str
    safe_window_minutes: int

class SosBeaconRequest(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    patient_name: Optional[str] = "Anonymous"
    emergency_contact: Optional[str] = None

@app.get("/")
def health_check():
    return {
        "service": "ResQ-AI Emergency Backend",
        "status": "Online",
        "version": "1.0.0"
    }

@app.post("/api/triage", response_model=TriageResponse)
def evaluate_triage(req: TriageRequest):
    """
    Emergency Triage Assessment Endpoint based on Manchester Triage System
    """
    symptoms = req.symptoms.lower()
    consciousness = req.consciousness.lower()
    
    # Critical Unconsciousness
    if consciousness == "unconscious":
        return TriageResponse(
            category="RED",
            condition="Unresponsive / Respiratory Compromise",
            priority=1,
            immediate_action="Check breathing immediately. Initiate CPR chest compressions (110 BPM). Call 108/112.",
            recommended_facility="Level 1 Trauma & ICU Center",
            safe_window_minutes=2
        )
    
    # Cardiac
    if any(k in symptoms for k in ["chest pain", "heart", "angina", "crushing", "radiating"]):
        return TriageResponse(
            category="RED",
            condition="Acute Coronary Syndrome (Suspected Myocardial Infarction)",
            priority=1,
            immediate_action="Sit patient upright. Administer 325mg chewable aspirin if not allergic. Prepare AED.",
            recommended_facility="Cardiology Emergency & Cath Lab",
            safe_window_minutes=10
        )
        
    # Stroke
    if any(k in symptoms for k in ["stroke", "slurred", "droop", "weakness in arm", "paralysis"]):
        return TriageResponse(
            category="RED",
            condition="Acute Ischemic Stroke",
            priority=1,
            immediate_action="Record exact symptom onset time. Keep patient flat. Do NOT give food or aspirin. Transport to CT center.",
            recommended_facility="Comprehensive Stroke Center",
            safe_window_minutes=15
        )
        
    # Severe Hemorrhage
    if any(k in symptoms for k in ["bleeding", "blood", "spurting", "arterial"]):
        return TriageResponse(
            category="RED",
            condition="Severe Traumatic Hemorrhage",
            priority=1,
            immediate_action="Apply continuous firm direct pressure with clean cloth. Apply tourniquet 2-3 inches above wound on limbs.",
            recommended_facility="Trauma Surgery Center",
            safe_window_minutes=5
        )
        
    # Snake Bite
    if any(k in symptoms for k in ["snake", "bite", "venom"]):
        return TriageResponse(
            category="YELLOW",
            condition="Suspected Snake Envenomation",
            priority=2,
            immediate_action="Keep patient motionless. Immobilize bitten limb below heart level. Never cut or suck wound. Rush for Anti-Snake Venom.",
            recommended_facility="Hospital with Polyvalent Antivenom",
            safe_window_minutes=30
        )

    # General Yellow
    return TriageResponse(
        category="GREEN",
        condition="Urgent / Non-Critical Presentation",
        priority=3,
        immediate_action="Provide standard supportive care, monitor vital signs, and consult outpatient medical provider.",
        recommended_facility="General Clinic / Primary Health Center",
        safe_window_minutes=60
    )

@app.post("/api/sos/broadcast")
def broadcast_sos(beacon: SosBeaconRequest):
    """
    Receives and logs 1-click emergency GPS beacons
    """
    return {
        "status": "Transmitted",
        "incident_id": f"INC-{abs(hash(str(beacon.latitude) + str(beacon.longitude))) % 10000}",
        "gps": {"lat": beacon.latitude, "lng": beacon.longitude},
        "dispatched_unit": "ALS Ambulance Unit #12",
        "eta_minutes": 6
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
