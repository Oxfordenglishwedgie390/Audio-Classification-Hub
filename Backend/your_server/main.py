"""
Audio Classification Hub — FastAPI Backend
Handles: register, login, audio upload, pipeline trigger, .whl build, download, welcome email
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import List

from dotenv import load_dotenv
load_dotenv()  # load .env before anything else

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import (
    create_user,
    get_user_by_email,
    user_exists,
    save_whl_path,
    get_whl_path,
)
from pipeline.preprocess import clean_audio
from pipeline.embedding import get_embedding
from pipeline.averaging import build_master
from pipeline.injector import inject_embedding, inject_company_embeddings
from pipeline.builder import build_whl
from login import validate_login, send_welcome_email

# ── Paths ─────────────────────────────────────────────────────────────────────
THIS_DIR     = Path(__file__).parent
FRONTEND_DIR = THIS_DIR.parent.parent / "Fronted"   # Full_Working/Fronted
BASE_DB      = THIS_DIR.parent.parent / "DataBase"

# WORKSPACES is intentionally placed OUTSIDE the server directory so
# WatchFiles never sees the generated build files and never triggers a reload.
WORKSPACES   = THIS_DIR.parent.parent / "workspaces"   # Full_Working/workspaces
WORKSPACES.mkdir(exist_ok=True)


# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="Audio Classification Hub", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handler — always return JSON, never plain text ───────────
from fastapi import Request
from fastapi.exceptions import RequestValidationError

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    tb = traceback.format_exc()
    print(f"\n[UNHANDLED ERROR] {type(exc).__name__}: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {str(exc)}"},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )

# ── Serve static assets at the SAME paths the HTML expects ───────────────────
# HTML files reference: css/style.css, js/main.js, js/api.js etc.
# So we mount these directories at the root level (no /static/ prefix needed).
if FRONTEND_DIR.exists():
    css_dir = FRONTEND_DIR / "css"
    js_dir  = FRONTEND_DIR / "js"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")



# ════════════════════════════════════════════════════════════════════════════
#  ROUTE 1 — REGISTER
#  POST /api/register
#  Body (multipart): name, email, password
# ════════════════════════════════════════════════════════════════════════════

@app.post("/api/register")
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    if not name.strip():
        raise HTTPException(400, "Name is required")
    if "@" not in email or "." not in email:
        raise HTTPException(400, "Invalid email address")
    if len(password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    if user_exists(email):
        raise HTTPException(409, "Email already registered. Please log in.")

    username = name.strip().lower().replace(" ", "_")
    create_user(name=name, email=email, password=password, username=username)

    return JSONResponse({"status": "ok", "message": "Account created", "username": username})


# ════════════════════════════════════════════════════════════════════════════
#  ROUTE 2 — LOGIN
#  POST /api/login
#  Body (form): email, password
# ════════════════════════════════════════════════════════════════════════════

@app.post("/api/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
):
    user = validate_login(email, password)
    if not user:
        raise HTTPException(401, "Invalid email or password")

    return JSONResponse({
        "status": "ok",
        "name": user["name"],
        "email": user["email"],
        "username": user["username"],
        "whl_ready": bool(user.get("whl_path")),
    })


# ════════════════════════════════════════════════════════════════════════════
#  ROUTE 3 — UPLOAD AUDIO + RUN FULL PIPELINE
#  POST /api/process
#  Body (multipart): email, files[] (.wav/.mp3/.flac)
# ════════════════════════════════════════════════════════════════════════════

@app.post("/api/process")
async def process_audio(
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    files: List[UploadFile] = File(...),
):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(404, "User not found. Please register first.")

    if not files or not (5 <= len(files) <= 20):
        raise HTTPException(400, "Please provide between 5 and 20 audio files.")

    allowed = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in allowed:
            raise HTTPException(400, f"Unsupported file type: {f.filename}. Use .wav .mp3 .flac .m4a")

    username = user["username"]

    # ── Create unique workspace for this build ────────────────────────────
    build_id = str(uuid.uuid4())[:8]
    workspace = WORKSPACES / f"{username}_{build_id}"
    uploads_dir = workspace / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # ── Save uploaded files ───────────────────────────────────────────────
    saved_paths = []
    user_voice_dir = BASE_DB / username / "voices"
    user_voice_dir.mkdir(parents=True, exist_ok=True)

    for f in files:
        dest = uploads_dir / f.filename
        content = await f.read()
        with open(dest, "wb") as out:
            out.write(content)
        perm = user_voice_dir / f.filename
        with open(perm, "wb") as out:
            out.write(content)
        saved_paths.append(str(dest))

    # ── PIPELINE ─────────────────────────────────────────────────────────
    try:
        audio_arrays = []
        skipped_count = 0
        for p in saved_paths:
            try:
                audio_arrays.append(clean_audio(p))
            except ValueError as e:
                if "too short" in str(e):
                    skipped_count += 1
                else:
                    raise e
                    
        if len(audio_arrays) < 5:
            raise ValueError(f"Only {len(audio_arrays)} valid audio files (>= 2s) found. Minimum 5 required.")

        embeddings   = [get_embedding(a) for a in audio_arrays]
        master       = build_master(embeddings)

        import numpy as np
        emb_path = BASE_DB / username / "embedding.npy"
        np.save(str(emb_path), master)

        inject_embedding(master, workspace)
        whl_path = build_whl(workspace)
        save_whl_path(email, whl_path)

        background_tasks.add_task(
            send_welcome_email,
            name=user["name"],
            email=email,
            whl_path=whl_path,
        )

    except Exception as e:
        import traceback
        print(f"\n[PIPELINE ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        shutil.rmtree(workspace, ignore_errors=True)
        raise HTTPException(500, f"Pipeline failed: {type(e).__name__}: {str(e)}")


    return JSONResponse({
        "status": "ok",
        "message": f"Voice embedding created. Accepted {len(audio_arrays)} files, skipped {skipped_count} short files." if skipped_count else "Voice embedding created and .whl built successfully",
        "build_id": build_id,
        "email": email,
        "accepted_files": len(audio_arrays),
        "skipped_files": skipped_count
    })


# ════════════════════════════════════════════════════════════════════════════
#  ROUTE 3.5 — UPLOAD COMPANY AUDIO + RUN CLASSIFICATION PIPELINE
#  POST /api/process_company
#  Body (multipart): email, files[] (from folder upload)
# ════════════════════════════════════════════════════════════════════════════

@app.post("/api/process_company")
async def process_company_audio(
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    files: List[UploadFile] = File(...),
):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(404, "User not found. Please register first.")

    from collections import defaultdict
    person_files = defaultdict(list)
    allowed = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}

    # Pydantic validation alternative: manual robust check for folder structure
    for f in files:
        parts = f.filename.split('/')
        if len(parts) != 2:
            raise HTTPException(400, f"Invalid file path format: {f.filename}. Expected PersonName/filename")
        person_name, actual_filename = parts
        
        ext = Path(actual_filename).suffix.lower()
        if ext not in allowed:
            raise HTTPException(400, f"Unsupported file type: {actual_filename}. Use .wav .mp3 .flac .m4a")
            
        person_files[person_name].append(f)

    if not person_files:
        raise HTTPException(400, "No valid audio files received.")

    for person, f_list in person_files.items():
        if not (5 <= len(f_list) <= 20):
            raise HTTPException(400, f"Person '{person}' has {len(f_list)} files. Must be between 5 and 20.")

    username = user["username"]
    build_id = str(uuid.uuid4())[:8]
    workspace = WORKSPACES / f"{username}_company_{build_id}"
    uploads_dir = workspace / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    company_embeddings = {}
    total_accepted = 0
    total_skipped = 0

    try:
        import numpy as np
        
        for person, f_list in person_files.items():
            saved_paths = []
            for f in f_list:
                dest = uploads_dir / f"{person}_{Path(f.filename).name}"
                content = await f.read()
                with open(dest, "wb") as out:
                    out.write(content)
                saved_paths.append(str(dest))

            audio_arrays = []
            skipped = 0
            for p in saved_paths:
                try:
                    audio_arrays.append(clean_audio(p))
                except ValueError as e:
                    if "too short" in str(e):
                        skipped += 1
                    else:
                        raise e
            
            if len(audio_arrays) < 5:
                raise ValueError(f"Person '{person}' only has {len(audio_arrays)} valid files (>= 2s). Minimum 5 required.")

            total_accepted += len(audio_arrays)
            total_skipped += skipped

            embeddings   = [get_embedding(a) for a in audio_arrays]
            master       = build_master(embeddings)
            company_embeddings[person] = master

        inject_company_embeddings(company_embeddings, workspace)
        whl_path = build_whl(workspace)
        save_whl_path(email, whl_path)

        background_tasks.add_task(
            send_welcome_email,
            name=user["name"],
            email=email,
            whl_path=whl_path,
        )

    except Exception as e:
        import traceback
        print(f"\n[PIPELINE ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        shutil.rmtree(workspace, ignore_errors=True)
        raise HTTPException(500, f"Pipeline failed: {type(e).__name__}: {str(e)}")

    return JSONResponse({
        "status": "ok",
        "message": f"Company embeddings created. Accepted {total_accepted} files, skipped {total_skipped} short files." if total_skipped else "Company voice embeddings created and .whl built successfully",
        "build_id": build_id,
        "email": email,
        "accepted_files": total_accepted,
        "skipped_files": total_skipped
    })


# ════════════════════════════════════════════════════════════════════════════
#  ROUTE 4 — DOWNLOAD .whl
#  GET /api/download?email=user@example.com
# ════════════════════════════════════════════════════════════════════════════

@app.get("/api/download")
async def download_whl(email: str):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(404, "User not found")

    whl_path = get_whl_path(email)
    if not whl_path or not Path(whl_path).exists():
        raise HTTPException(404, "No .whl file found. Please complete voice registration first.")

    return FileResponse(
        path=whl_path,
        filename=Path(whl_path).name,
        media_type="application/octet-stream",
    )


# ════════════════════════════════════════════════════════════════════════════
#  ROUTE 5 — CHECK STATUS
#  GET /api/status?email=user@example.com
# ════════════════════════════════════════════════════════════════════════════

@app.get("/api/status")
async def check_status(email: str):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(404, "User not found")

    whl_path = get_whl_path(email)
    ready    = bool(whl_path and Path(whl_path).exists())

    return JSONResponse({
        "status": "ok",
        "whl_ready": ready,
        "name": user["name"],
        "email": email,
        "whl_filename": Path(whl_path).name if ready else None,
    })


# ════════════════════════════════════════════════════════════════════════════
#  ROUTE 6 — VOICE VERIFY (test a sample against registered embedding)
#  POST /api/verify
#  Body (multipart): email, file (audio)
#  Returns: confidence 0–100, label, match (bool), cosine_score
# ════════════════════════════════════════════════════════════════════════════

@app.post("/api/verify")
async def verify_voice(
    email: str = Form(...),
    file: UploadFile = File(...),
):
    import numpy as np
    import tempfile, os

    user = get_user_by_email(email)
    if not user:
        raise HTTPException(404, "User not found. Please register first.")

    username = user["username"]

    # Load stored master embedding
    emb_path = BASE_DB / username / "embedding.npy"
    if not emb_path.exists():
        raise HTTPException(404, "No registered voiceprint found. Please complete the onboarding first.")

    master = np.load(str(emb_path))   # (192,)

    # Validate file type
    ext = Path(file.filename).suffix.lower()
    if ext not in {".wav", ".mp3", ".flac", ".ogg", ".webm", ".mp4", ".m4a"}:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    # Save to a temp file for processing
    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        audio  = clean_audio(tmp_path)
        test_emb = get_embedding(audio)   # (192,)
    except Exception as e:
        os.unlink(tmp_path)
        raise HTTPException(422, f"Could not process audio: {str(e)}")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    # Cosine similarity in [-1, 1] → scale to [0, 100]
    dot   = float(np.dot(master, test_emb))
    norm  = float(np.linalg.norm(master) * np.linalg.norm(test_emb))
    cosine = dot / norm if norm > 0 else 0.0

    # Map cosine similarity to a display confidence percentage:
    #   display% = cosine * 100 + 20  (adds a fixed +20 boost)
    #   cosine 0.20 → 40%  |  0.45 → 65%  |  0.62 → 82%  |  0.80 → 100%
    confidence = round(min(100, max(0, (cosine * 100) + 20)), 1)

    # Label thresholds
    if confidence >= 82:
        label   = "Strong Match"
        matched = True
        color   = "green"
        icon    = "fa-shield-check"
    elif confidence >= 65:
        label   = "Partial Match"
        matched = True
        color   = "amber"
        icon    = "fa-circle-half-stroke"
    elif confidence >= 45:
        label   = "Weak Match"
        matched = False
        color   = "orange"
        icon    = "fa-triangle-exclamation"
    else:
        label   = "No Match"
        matched = False
        color   = "red"
        icon    = "fa-xmark-circle"

    return JSONResponse({
        "status":       "ok",
        "confidence":   confidence,        # 0.0 – 100.0
        "cosine_score": round(cosine, 4),  # raw cosine similarity
        "label":        label,
        "matched":      matched,
        "color":        color,
        "icon":         icon,
    })


# ════════════════════════════════════════════════════════════════════════════
#  ROUTE 6 — SERVE FRONTEND PAGES
# ════════════════════════════════════════════════════════════════════════════

def _fe(page: str):
    """Return a FileResponse for a frontend page."""
    path = FRONTEND_DIR / page
    if not path.exists():
        raise HTTPException(404, f"Page not found: {page}")
    return FileResponse(str(path))

@app.get("/")
async def serve_index():
    return _fe("index.html")

@app.get("/auth")
async def serve_auth():
    return _fe("auth.html")

@app.get("/onboarding-type")
async def serve_onboarding_type():
    return _fe("onboarding-type.html")

@app.get("/onboarding-record")
async def serve_onboarding_record():
    return _fe("onboarding-record.html")

@app.get("/onboarding-processing")
async def serve_onboarding_processing():
    return _fe("onboarding-processing.html")

@app.get("/download")
async def serve_download():
    return _fe("download.html")

@app.get("/auth.html")
async def serve_auth_html():
    return _fe("auth.html")

@app.get("/onboarding-type.html")
async def serve_onboarding_type_html():
    return _fe("onboarding-type.html")

@app.get("/onboarding-record.html")
async def serve_onboarding_record_html():
    return _fe("onboarding-record.html")

@app.get("/onboarding-processing.html")
async def serve_onboarding_processing_html():
    return _fe("onboarding-processing.html")

@app.get("/download.html")
async def serve_download_html():
    return _fe("download.html")

@app.get("/onboarding-company.html")
async def serve_company_html():
    return _fe("onboarding-company.html")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
