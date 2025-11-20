from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

app = FastAPI(title="SuppAI API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In a full implementation we'd use MongoDB via provided helpers.
# For this MVP, we keep logic stateless and deterministic without persistence.

class SurveyResponse(BaseModel):
    energy: int = Field(ge=1, le=5)
    gut_health: int = Field(ge=1, le=5)
    muscle_gain: int = Field(ge=1, le=5)
    stress: int = Field(ge=1, le=5)
    sleep: int = Field(ge=1, le=5)
    allergies: int = Field(ge=1, le=5)
    autoimmune: int = Field(ge=1, le=5)  # eczema, asthma
    skin: int = Field(ge=1, le=5)
    digestion: int = Field(ge=1, le=5)
    country: str
    email: Optional[EmailStr] = None

class Recommendation(BaseModel):
    name: str
    reason: str
    dosage: Optional[str] = None
    sources: List[str] = []

class RecommendationResult(BaseModel):
    package_image_url: str
    recommendations: List[Recommendation]

# Research citations (university-level / meta-analyses) – simplified for demo
CITATIONS = {
    "vitamin_d": [
        "Harvard T.H. Chan School of Public Health – Vitamin D and Health",
        "University of Cambridge – Vitamin D and immune modulation"
    ],
    "creatine": [
        "University of Nottingham – Creatine and muscle performance",
        "Australian Institute of Sport – Creatine evidence"
    ],
    "probiotic": [
        "Johns Hopkins – Gut microbiome and probiotics",
        "Stanford Medicine – Probiotics in GI health"
    ],
    "magnesium": [
        "NIH ODS – Magnesium and sleep quality",
        "UC Berkeley – Stress and magnesium relationship"
    ],
    "omega_3": [
        "Harvard – Omega-3 and cardiovascular/skin benefits"
    ],
    "quercetin": [
        "NC State University – Quercetin and allergies"
    ],
    "zinc": [
        "University of Florida – Zinc and skin health"
    ],
    "ashwagandha": [
        "University of Michigan – Adaptogens for stress"
    ],
}

COUNTRY_DEFICIENCY = {
    "uk": "vitamin_d",
    "ireland": "vitamin_d",
    "canada": "vitamin_d",
    "sweden": "vitamin_d",
    "norway": "vitamin_d",
}


def build_recommendations(data: SurveyResponse) -> List[Recommendation]:
    recs: List[Recommendation] = []

    if data.energy >= 4:
        recs.append(Recommendation(
            name="Magnesium Glycinate",
            reason="Supports cellular energy and relaxation; often low in modern diets.",
            dosage="200–400 mg in the evening",
            sources=CITATIONS["magnesium"],
        ))

    if data.muscle_gain >= 3:
        recs.append(Recommendation(
            name="Creatine Monohydrate",
            reason="Improves high‑intensity performance and lean mass in numerous RCTs.",
            dosage="3–5 g daily",
            sources=CITATIONS["creatine"],
        ))

    if data.gut_health >= 3 or data.digestion >= 3:
        recs.append(Recommendation(
            name="Multi‑strain Probiotic",
            reason="Helps balance gut microbiota and supports digestion.",
            dosage="10–20B CFU daily",
            sources=CITATIONS["probiotic"],
        ))

    if data.stress >= 3 or data.sleep >= 3:
        recs.append(Recommendation(
            name="Ashwagandha (KSM‑66/Sensoril)",
            reason="Adaptogen studied for perceived stress and sleep quality.",
            dosage="300–600 mg daily",
            sources=CITATIONS["ashwagandha"],
        ))

    if data.skin >= 3 or data.allergies >= 3:
        recs.append(Recommendation(
            name="Omega‑3 (EPA/DHA)",
            reason="Anti‑inflammatory support with benefits for skin barrier and allergies.",
            dosage="1–2 g combined EPA/DHA daily",
            sources=CITATIONS["omega_3"],
        ))

    if data.allergies >= 4:
        recs.append(Recommendation(
            name="Quercetin",
            reason="Bioflavonoid studied for mast‑cell stabilization and seasonal allergies.",
            dosage="500–1000 mg daily with food",
            sources=CITATIONS["quercetin"],
        ))

    if data.skin >= 4:
        recs.append(Recommendation(
            name="Zinc Picolinate",
            reason="Supports skin integrity and immune function; deficiency correlates with acne.",
            dosage="15–30 mg daily with food",
            sources=CITATIONS["zinc"],
        ))

    # Regional deficiency logic
    if COUNTRY_DEFICIENCY.get(data.country.lower()) == "vitamin_d":
        recs.append(Recommendation(
            name="Vitamin D3 (cholecalciferol)",
            reason="High latitude regions have limited UVB; D3 supports immunity and mood.",
            dosage="1000–2000 IU daily",
            sources=CITATIONS["vitamin_d"],
        ))

    # Always keep list unique by name
    unique = {}
    for r in recs:
        unique[r.name] = r
    return list(unique.values())


@app.post("/recommend", response_model=RecommendationResult)
async def recommend(data: SurveyResponse):
    recs = build_recommendations(data)
    # Generated package image placeholder (could be a dynamic image service)
    package_image_url = "https://images.unsplash.com/photo-1586015555751-63f17a0b3bd9?q=80&w=1200&auto=format&fit=crop"
    return RecommendationResult(package_image_url=package_image_url, recommendations=recs)


class EmailPayload(BaseModel):
    email: EmailStr
    recommendations: List[Recommendation]


@app.post("/send-email")
async def send_email(payload: EmailPayload):
    # Placeholder: In production, integrate with a transactional email service.
    # Here we just acknowledge.
    return {"status": "queued", "email": payload.email, "count": len(payload.recommendations)}


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
