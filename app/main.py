from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.llm_extract import ExtractionError, extract_fields
from app.models import FreeTextRequest, TamScoreRequest, TamScoreResponse
from app.scoring import score_tam

app = FastAPI(
    title="TAM Scoring Agent",
    description="Answers: is this company part of my addressable universe?",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/score", response_model=TamScoreResponse)
def score(request: TamScoreRequest) -> TamScoreResponse:
    return score_tam(request)


@app.post("/score/freetext", response_model=TamScoreResponse)
def score_freetext(request: FreeTextRequest) -> TamScoreResponse:
    try:
        extracted = extract_fields(request.text)
    except ExtractionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return score_tam(extracted)
