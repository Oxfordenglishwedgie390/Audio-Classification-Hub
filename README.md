<div align="center">

<img src="Screenshots/Screenshot 2026-08-01 190641.png" alt="Audio Classification Hub" width="100%"/>

<br/><br/>

# 🎙️ Audio Classification Hub

### *Register once. Embed forever. Authenticate any voice in 2 lines of Python.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SpeechBrain](https://img.shields.io/badge/SpeechBrain-ECAPA--TDNN-FF6B6B?style=for-the-badge&logo=pytorch&logoColor=white)](https://speechbrain.github.io)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-00D4FF?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-22C55E?style=for-the-badge)](#)

<br/>

**B2C · B2B · Enterprise** &nbsp;|&nbsp; Voice Biometric Authentication as a Service &nbsp;|&nbsp; Zero Cloud Lock-In

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Live Product Preview](#-live-product-preview)
- [The Core Idea — Why No Training?](#-the-core-idea--why-no-training)
- [The AI Model — ECAPA-TDNN Deep Dive](#-the-ai-model--ecapa-tdnn-deep-dive)
- [System Architecture](#-system-architecture)
- [Backend — Deep Code Analysis](#-backend--deep-code-analysis)
- [Frontend — Page-by-Page Walkthrough](#-frontend--page-by-page-walkthrough)
- [What the User Gets — The .whl Package](#-what-the-user-gets--the-whl-package)
- [Complete User Journey](#-complete-user-journey)
- [Industry Use Cases](#-industry-use-cases--where-it-fits)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Local Setup & Installation](#-local-setup--installation)
- [Configuration](#-configuration)
- [Security Considerations](#-security-considerations)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 🌟 Overview

**Audio Classification Hub** is a production-grade, full-stack **Voice Authentication Platform** that
converts spoken voice samples into a permanent, portable identity vector — a **voiceprint** — and
packages it into a downloadable Python `.whl` file that any developer can install and use offline in 2 lines of code.

This is **not** a cloud-locked SaaS. The intelligence ships *with* the user.

### What Makes It Different

| Traditional Voice Auth | Audio Classification Hub |
|---|---|
| Requires cloud API calls on every verification | Fully **offline** after `.whl` install |
| Vendor lock-in, per-call billing | One-time registration, **zero recurring cost** |
| Data sent to third-party servers | Voiceprint stays on-premise |
| SDK tied to platform version | Pure Python wheel, works anywhere |
| Weeks to integrate | **2 lines of Python** |

---

## 🖥️ Live Product Preview

> The landing page features a WebGL shader canvas rendering animated chromatic voice waveforms
> built with Three.js. Every section uses glassmorphism, scroll-reveal animations, and a dark-mode design system.

| Page | What You See |
|---|---|
| **Landing** (`index.html`) | Animated waveform hero, 3-step explainer, bento feature grid, marquee social proof |
| **Auth** (`auth.html`) | Split-screen login/signup with live password strength indicator |
| **Type Select** (`onboarding-type.html`) | Individual vs. Team/Company card selector with animated ping rings |
| **Voice Recorder** (`onboarding-record.html`) | Live browser microphone recorder + drag-and-drop upload zone (5–20 samples) |
| **Processing** (`onboarding-processing.html`) | Real-time pipeline: MFCC heatmap, waveform, pitch contour, 192-dim embedding bars, UMAP projection |
| **Download** (`download.html`) | SDK download, code snippets, voice verification playground |

---

## 💡 The Core Idea — Why No Training?

> This is the most important architectural decision in the project.

### Traditional Deep Learning Approach ❌

Most voice recognition tutorials tell you to:
1. Collect thousands of hours of labeled speech data
2. Train a classifier from scratch (weeks of GPU time)
3. Re-train whenever you add a new user
4. Deploy a heavy model that classifies into fixed categories

**This approach cannot scale for personal authentication.** If you trained on 1,000 users and a
new user joins, you'd need to re-train the entire network.

### Our Approach — Pretrained Embedding + Cosine Similarity ✅

We use a concept from **metric learning**:

```
Pretrained Model (ECAPA-TDNN)
        ↓
Maps any voice → 192-dimensional vector space
        ↓
Voices from the SAME person  → vectors that are CLOSE together
Voices from DIFFERENT people → vectors that are FAR apart
```

The model was pre-trained on **VoxCeleb** — 2,000+ speakers, 1M+ utterances from YouTube.
It **learned the universal geometry of human voice space**. We do not train anything new. We just:

1. **Encode** the user's 5–20 voice samples into 192-dim vectors
2. **Average** them into a single master voiceprint
3. At verification time, compute **cosine similarity** between master and live sample
4. If similarity > threshold → **authenticated**

This is the same principle powering **FaceID**.

**Benefits:**
- ✅ Zero training time — new user registration takes ~60 seconds
- ✅ No GPU required at inference — runs on any CPU
- ✅ Adding users does not affect accuracy for others
- ✅ Model is compact and ships inside the `.whl`

---

## 🧠 The AI Model — ECAPA-TDNN Deep Dive

### Model: `speechbrain/spkrec-ecapa-voxceleb`

| Property | Value |
|---|---|
| **Architecture** | ECAPA-TDNN (Emphasized Channel Attention, Propagation and Aggregation — Time Delay Neural Network) |
| **Pre-trained on** | VoxCeleb 1 & 2 (2,000+ speakers, 1M+ utterances) |
| **Output** | 192-dimensional L2-normalized embedding vector |
| **Input format** | 16kHz mono float32 numpy array |
| **Inference device** | CPU (no GPU needed) |
| **Source** | HuggingFace Hub `speechbrain/spkrec-ecapa-voxceleb` |
| **Framework** | SpeechBrain + PyTorch |

### ECAPA-TDNN Architecture Flow

```
Raw Audio (16kHz PCM)
        ↓
  Frame-level Feature Extraction
  (Filter banks / MFCCs at each time step)
        ↓
  TDNN Layers with Dilation
  (Captures short + long-range temporal dependencies)
        ↓
  SE-Res2Block (Squeeze-and-Excitation + Residual)
  (Channel attention — emphasizes discriminative voice features)
        ↓
  Multi-scale Feature Aggregation (MFA)
  (Combines features from ALL TDNN layers)
        ↓
  Attentive Statistics Pooling
  (Collapses variable-length sequence → fixed representation)
        ↓
  Fully Connected Layer
        ↓
  192-dim L2-normalized Vector  ← THE VOICEPRINT
```

### Why 192 Dimensions?

The 192-dim space is specifically tuned for **speaker discrimination**:
- Each dimension captures abstract acoustic properties (vocal tract shape, pitch patterns, speaking style)
- L2 normalization means all vectors lie on a unit hypersphere — cosine similarity equals dot product
- Empirically the sweet spot between expressiveness and computational cost

### Cosine Similarity → Confidence Mapping

```python
# Raw cosine similarity in [-1.0, +1.0]
cosine = dot(master, test_emb) / (norm(master) * norm(test_emb))

# Display confidence: mapped to 0-100% with +20 boost for UX clarity
# cosine 0.20 → 40%  |  0.45 → 65%  |  0.62 → 82%  |  0.80 → 100%
confidence = min(100, max(0, (cosine * 100) + 20))
```

| Raw Cosine | Display % | Label | Match? |
|---|---|---|---|
| >= 0.62 | >= 82% | 🟢 Strong Match | ✅ Yes |
| >= 0.45 | >= 65% | 🟡 Partial Match | ✅ Yes |
| >= 0.25 | >= 45% | 🟠 Weak Match | ❌ No |
| < 0.25 | < 45% | 🔴 No Match | ❌ No |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AUDIO CLASSIFICATION HUB                         │
├──────────────────────────┬──────────────────────────────────────────┤
│       FRONTEND           │              BACKEND                     │
│   (HTML + JS + CSS)      │         (FastAPI + Python)               │
│                          │                                          │
│  index.html              │  ┌───────────────────────────────────┐  │
│  auth.html    ───────────┼─►│      FastAPI (Uvicorn :8000)      │  │
│  onboarding pages        │  └───────────────┬───────────────────┘  │
│  download.html           │                  │                       │
│                          │       ┌──────────▼──────────┐           │
│  js/api.js               │       │     ML PIPELINE      │           │
│  js/recorder.js          │       │  1. preprocess.py    │           │
│  js/processing.js        │       │  2. embedding.py     │           │
│  js/hero-shader.js       │       │     (ECAPA-TDNN)     │           │
│  css/style.css           │       │  3. averaging.py     │           │
│                          │       │  4. injector.py      │           │
│                          │       │  5. builder.py       │           │
└──────────────────────────┤       └──────────┬───────────┘           │
                           │                  │                       │
                           │  ┌───────────────▼────────────────────┐ │
                           │  │         FILE SYSTEM DB              │ │
                           │  │  DataBase/login.csv  (registry)     │ │
                           │  │  DataBase/<user>/embedding.npy      │ │
                           │  │  workspaces/<user>_<id>/dist/*.whl  │ │
                           │  └─────────────────────────────────────┘ │
                           │  ┌─────────────────────────────────────┐ │
                           │  │  SMTP Email (.whl attached)          │ │
                           │  └─────────────────────────────────────┘ │
                           └───────────────────────────────────────────┘
```

---

## ⚙️ Backend — Deep Code Analysis

The backend is built with **FastAPI**, chosen for its async-first design, automatic OpenAPI docs
at `/docs`, Pydantic validation for multipart forms, and `BackgroundTasks` for non-blocking email delivery.

### FastAPI Application (`main.py`)

The entry point registers **7 REST API endpoints** and mounts the frontend static assets at the
same paths the HTML expects (`/css/`, `/js/`), so no separate web server is needed.

```python
# Frontend HTML + Backend API on same origin — no CORS complexity
app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
app.mount("/js",  StaticFiles(directory=str(js_dir)),  name="js")
```

Global error handling ensures all exceptions return clean JSON — the JS `safeJson()` parser always succeeds.

#### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/register` | Create new user account |
| `POST` | `/api/login` | Validate credentials |
| `POST` | `/api/process` | Upload voice samples → run full ML pipeline → build `.whl` |
| `POST` | `/api/process_company` | Multi-person bulk upload → multi-embedding `.whl` |
| `GET` | `/api/download` | Stream the generated `.whl` file |
| `GET` | `/api/status` | Poll whether `.whl` build is ready |
| `POST` | `/api/verify` | Verify a voice sample against stored voiceprint |
| `GET` | `/` and page routes | Serve all frontend HTML pages |

---

### ML Pipeline — 5-Stage Processing

#### Stage 1 — `pipeline/preprocess.py` — Audio Cleaning

Every uploaded audio file goes through a 3-backend loading cascade:

```
torchaudio (soundfile → sox_io)  ──► succeeds for WAV/FLAC/OGG
         ↓ fail
soundfile + resampy               ──► succeeds for WAV/FLAC
         ↓ fail
librosa (requires ffmpeg)         ──► catches MP4/WebM/M4A
```

After loading, audio is:
- **Resampled** to exactly 16,000 Hz (ECAPA-TDNN requirement)
- **Mixed down** to mono
- **Validated** — rejected if < 2 seconds
- **Padded or trimmed** to exactly 3 seconds (48,000 samples)
- **Peak-normalized** to [-1.0, +1.0]

```python
SR       = 16000   # ECAPA-TDNN requires exactly 16kHz
DURATION = 3       # seconds window used for embedding
MIN_SEC  = 2.0     # reject files shorter than this
```

#### Stage 2 — `pipeline/embedding.py` — Voice Vector Extraction

The ECAPA-TDNN model is loaded **once** into a module-level global `_model` (lazy singleton)
to avoid reloading ~100MB on every request.

**Windows Compatibility Fix:** On Windows without Developer Mode, `pathlib.Path.symlink_to()`
raises `[WinError 1314]`. SpeechBrain calls this during model caching. The module monkey-patches it:

```python
# Patch BEFORE any SpeechBrain import
_orig_symlink_to = Path.symlink_to

def _safe_symlink_to(self, target, target_is_directory=False):
    try:
        _orig_symlink_to(self, target, target_is_directory)
    except OSError:
        shutil.copy2(str(target_p), str(self))  # fall back to file copy

Path.symlink_to = _safe_symlink_to
```

Inference:

```python
def get_embedding(audio: np.ndarray) -> np.ndarray:
    tensor = torch.FloatTensor(audio).unsqueeze(0)   # (1, N)
    with torch.no_grad():
        emb = model.encode_batch(tensor)             # (1, 1, 192)
    return emb.squeeze().numpy().astype(np.float32)  # (192,)
```

#### Stage 3 — `pipeline/averaging.py` — Master Voiceprint

Multiple samples produce slightly different vectors (phrasing, noise).
Averaging builds a centroid that is more robust:

```python
def build_master(embeddings: list) -> np.ndarray:
    stacked = np.stack(embeddings, axis=0)   # (N, 192)
    master  = np.mean(stacked, axis=0)       # (192,)
    return master.astype(np.float32)
```

> **Rule of thumb:** More samples = more accurate centroid. 5 is minimum; 20 is recommended maximum.

#### Stage 4 — `pipeline/injector.py` — Embedding Baking

This is what makes the `.whl` work **without any server calls**. The user's 192-float embedding
is literally baked into Python source code:

```python
# core_template.py contains:  EMBEDDING = {{EMBEDDING}}
# The injector replaces the placeholder with actual numbers:
embedding_str = repr(master.tolist())              # "[0.023, -0.114, ...]"
final_code = template_code.replace("{{EMBEDDING}}", embedding_str)
```

When the `.whl` is imported, no database, no network, no model download is needed.

**Company Mode** injects a `dict` of `{person_name: [192-float-list]}` instead, enabling
1:N speaker identification from a single package.

#### Stage 5 — `pipeline/builder.py` — Wheel Packaging

```python
subprocess.run([sys.executable, "-m", "build"], cwd=str(build_dir))
```

Uses Python `build` module (PEP 517/518). Each build gets a UUID-isolated workspace so concurrent
builds never interfere. Workspace lives outside the server directory to prevent `uvicorn --reload`
from triggering on generated files.

---

### Database Layer (`database.py`)

Uses a **flat-file CSV** approach — simple, portable, zero-dependency:

```
DataBase/
├── login.csv                  # name, email, password, username, registered_at, whl_path
├── mohit_jadav/
│   ├── voices/                # raw uploaded audio files
│   └── embedding.npy          # 192-dim master voiceprint
└── harsh_jadav/
    ├── voices/
    └── embedding.npy
```

- `create_user()` — creates user row AND the `DataBase/<username>/` folder atomically
- `save_whl_path()` — updates whl_path column after a successful build
- `get_whl_path()` — lookup used by `/api/download` and `/api/status`

---

### Email Delivery System (`login.py`)

After every successful pipeline run, a **non-blocking background task** sends a welcome email with the `.whl` attached:

```python
background_tasks.add_task(
    send_welcome_email,
    name=user["name"],
    email=email,
    whl_path=whl_path,
)  # Returns API response immediately — email sends asynchronously
```

Email failures are caught and logged but never crash the user-facing request.

---

## 🎨 Frontend — Page-by-Page Walkthrough

The frontend is a **pure HTML + CSS + JavaScript SPA** (no React, no Vue) served directly by FastAPI.

**Tech Stack:**
- **Tailwind CSS** (CDN) for utility classes
- **Three.js** for WebGL voice waveform shaders
- **Apache ECharts** for processing visualization charts
- **Font Awesome 6** for iconography
- **Google Fonts** — Space Grotesk, Inter, JetBrains Mono
- **Custom `css/style.css`** — glassmorphism design system, CSS tokens, micro-animations

### Page 1 — `index.html` — Landing Page

| Element | Implementation |
|---|---|
| **Hero Canvas** | Three.js WebGL shader — animated chromatic waveform sinusoids |
| **Scroll Reveal** | IntersectionObserver with staggered `data-delay` |
| **3-Step How It Works** | Animated ping rings, waveform bars via `@keyframes wfPulse` |
| **Code Window** | Multi-tab snippet (Python / FastAPI / Node / cURL) |
| **Bento Grid** | 4-column masonry feature cards with radial gradient glows |
| **Social Proof Marquee** | CSS infinite scroll strip |
| **CTA** | Start Free → auth.html / View Docs → download.html |

### Page 2 — `auth.html` — Sign In / Sign Up

- **Split-screen** — left: animated canvas + tagline, right: auth card
- **Tab toggle** — Login / Sign Up with animated active state
- **Password strength meter** — 4-segment bar (Too weak → Strong) via real-time regex
- **Session management** — `Session.save()` to `sessionStorage`; redirects based on `whl_ready`

### Page 3 — `onboarding-type.html` — Account Type Selection

- **4-step progress stepper** with animated connectors (Step 1 active)
- **Individual card** → `onboarding-record.html` (single voiceprint)
- **Team/Company card** → `onboarding-company.html` (multi-user folder upload)
- Card selection triggers animated bounce-in checkmark

### Page 4 — `onboarding-record.html` — Voice Capture

**Record Mode (WebRTC):**
- `MediaRecorder API` — browser microphone as `audio/webm` blobs
- Live countdown timer with `requestAnimationFrame`
- 3 concentric animated pulse rings during recording
- Playback bar + Re-record + Next sample controls
- Counter: `0 / 20 captured` in real time

**Upload Mode (Drag & Drop):**
- `dragover` / `drop` events with visual border feedback
- `<input type="file" multiple accept=".wav,.mp3,.flac,.ogg,.m4a">`
- Validates 5–20 files before enabling Process button

### Page 5 — `onboarding-processing.html` — Live Pipeline Visualizer

**Left Panel — Pipeline Steps:**
- 5 animated steps: Loading Audio → Preprocessing → MFCC Extraction → ECapa Embedding → Packaging .whl
- CSS `transform: translateX(4px)` on active step
- Real elapsed timer + gradient progress bar `linear-gradient(90deg, #6366F1, #00D4FF)`

**Right Panel — ECharts Visualizations:**

| Chart | What It Shows |
|---|---|
| **MFCC Heatmap** | 13 Mel-Frequency Cepstral Coefficient tracks across time |
| **Waveform + Energy Envelope** | Amplitude over time with energy overlay |
| **Pitch Contour (F0)** | Fundamental frequency curve across the utterance |
| **192-dim Embedding Bars** | All 192 embedding dimensions visualized |
| **UMAP Scatter Plot** | 2D projection: user voiceprint vs. population cluster |

**Backend Polling (every 3 seconds, max 6 minutes):**

```javascript
setInterval(async () => {
    const data = await apiStatus(user.email);
    if (data.whl_ready) {
        clearInterval(pollTimer);
        forceComplete();   // snap UI to 100%
        showDownloadCTA(); // no auto-redirect — user decides
    }
}, 3000);
```

### Page 6 — `download.html` — SDK Download & Verify

- Download button → `GET /api/download?email=<email>`
- Multi-language code snippets (Python, FastAPI, Node.js, cURL)
- Live **Voice Verify** playground — record test sample, see animated confidence result card

---

## 📦 What the User Gets — The `.whl` Package

After completing registration, the user receives:

```
audioauth-1.0.0-py3-none-any.whl
```

### Package Contents

```
audioauth/
├── __init__.py
├── core.py          ← YOUR VOICEPRINT BAKED IN (192-float Python list)
└── ...
```

`core.py` contains your embedding as a static Python constant:
```python
EMBEDDING = [0.0234, -0.1142, 0.4471, 0.0891, -0.2310, ...]  # 192 floats
```

### How Developers Use It

```bash
pip install audioauth-1.0.0-py3-none-any.whl
```

```python
# 2 lines. That is all.
from audioauth import VoiceAuth

auth = VoiceAuth()
result = auth.verify("sample.wav")  # Returns: True / False
```

**Advanced usage:**
```python
details = auth.verify_detailed("voice.wav")
print(details["confidence"])    # 0.0 to 100.0
print(details["label"])         # "Strong Match" / "Partial Match" / ...
print(details["matched"])       # True / False
print(details["cosine_score"])  # raw cosine similarity

# Company / multi-user mode
auth = VoiceAuth(mode="company")
speaker = auth.identify("voice.wav")   # returns matched person name
```

**FastAPI integration:**
```python
from fastapi import FastAPI, UploadFile
from audioauth import VoiceAuth

app = FastAPI()
auth = VoiceAuth()

@app.post("/check-voice")
async def check_voice(file: UploadFile):
    contents = await file.read()
    return {"authenticated": auth.verify_bytes(contents)}
```

### What Is NOT in the Package

- ❌ No SpeechBrain model weights — embedding already extracted, model not needed
- ❌ No network calls — runs 100% offline
- ❌ No cloud dependency — your voiceprint, your server
- ❌ No GPU requirement — pure NumPy cosine similarity at ~50ms latency

---

## 🔄 Complete User Journey

```
                    REGISTRATION FLOW
    ┌──────────────────────────────────────────────────────┐
    │   1. LANDING PAGE                                    │
    │      Learns about product → Clicks "Start Free"      │
    │                    ↓                                 │
    │   2. AUTH PAGE                                       │
    │      Sign Up → POST /api/register                    │
    │      → Redirected to Type Selection                  │
    │                    ↓                                 │
    │   3. TYPE SELECTION                                   │
    │      Choose: Individual OR Team/Company              │
    │                    ↓                                 │
    │   4. VOICE RECORDING                                 │
    │      Record 5–20 samples OR drag-and-drop files      │
    │      → Click "Process Voice"                         │
    │                    ↓                                 │
    │   5. PIPELINE (~60 seconds, async)                   │
    │      POST /api/process                               │
    │      ├── Stage 1: clean_audio() x N files            │
    │      ├── Stage 2: get_embedding() → N x [192]        │
    │      ├── Stage 3: build_master() → [192]             │
    │      ├── Stage 4: inject_embedding() → core.py       │
    │      └── Stage 5: build_whl() → .whl                 │
    │                    ↓                                 │
    │   6. PROCESSING PAGE (polls /api/status every 3s)    │
    │      MFCC, waveform, pitch, embedding, UMAP charts   │
    │      → Done → Download .whl CTA appears              │
    │                    ↓                                 │
    │   7. DOWNLOAD PAGE                                   │
    │      GET /api/download → .whl streamed to browser    │
    │      + Welcome email with .whl attached              │
    └──────────────────────────────────────────────────────┘

                  DAILY AUTHENTICATION FLOW
    ┌──────────────────────────────────────────────────────┐
    │   pip install audioauth-1.0.0-py3-none-any.whl       │
    │   from audioauth import VoiceAuth                    │
    │   auth = VoiceAuth()                                 │
    │   result = auth.verify("voice.wav")                  │
    │                    ↓                                 │
    │   1. Load [192] from core.py (static constant)       │
    │   2. Load audio → 16kHz numpy array                  │
    │   3. Compute cosine similarity                       │
    │   4. Return True/False + confidence                  │
    │                                                      │
    │   ~50ms latency · 0 network calls · 0 GPU            │
    └──────────────────────────────────────────────────────┘
```

---

## 🏢 Industry Use Cases — Where It Fits

Audio Classification Hub targets both **B2C** (developers, prosumers) and **B2B** (enterprises, SaaS).

### 🏦 Banking & Financial Services
- Phone banking authentication — replace KBA with voice biometrics
- IVR gating — authenticate callers before agent transfer
- Anti-fraud — detect account takeover by verifying caller identity
- PCI-DSS voice channel compliance

### 🏥 Healthcare
- Telehealth patient verification before prescription refills
- EHR access control — voice-lock records for specific clinicians
- HIPAA-compliant (voiceprint on-premise, zero cloud exposure)

### 🏢 Enterprise HR & Access Control
- Remote work time-tracking — employees clock in by voice
- Secure facility access — voice-gated physical security
- Executive document DLP enforcement by speaker verification

### 📞 Call Centers & Customer Experience
- Passive agent-side verification as call connects
- VIP customer detection → priority queue routing
- Callback authentication before resuming sensitive sessions

### 🎓 EdTech & Proctoring
- Online exam authentication throughout the session
- Voice-based lecture attendance check-in
- Adaptive learning gates — unlock advanced content for verified learners

### 🔐 Consumer Apps (B2C)
- Password manager voice unlock — biometric second factor
- Smart home voice commands — prevent spoofing by non-members
- Parental controls — voice-gated content restrictions

### 🏗️ Developer / Platform (API Economy)
- Ship the `.whl` inside your product installer
- Wrap `/api/verify` as a microservice sidecar for any service
- IoT / Edge devices — offline voice auth for Raspberry Pi, embedded systems

---

## 📡 API Reference

### POST `/api/register`

**Request (multipart/form-data):** `name`, `email`, `password` (min 6 chars)

```json
{ "status": "ok", "message": "Account created", "username": "mohit_jadav" }
```

### POST `/api/login`

**Request:** `email`, `password`

```json
{ "status": "ok", "name": "Mohit Jadav", "email": "...", "username": "mohit_jadav", "whl_ready": false }
```

### POST `/api/process`

**Request:** `email`, `files[]` — 5 to 20 audio files (.wav .mp3 .flac .ogg .m4a)

```json
{
  "status": "ok",
  "message": "Voice embedding created and .whl built successfully",
  "build_id": "a3f91c2b",
  "accepted_files": 8,
  "skipped_files": 0
}
```

### POST `/api/process_company`

Bulk multi-person enrollment. Files structured as `PersonName/filename.wav` (5–20 per person).

### GET `/api/status?email=<email>`

```json
{ "status": "ok", "whl_ready": true, "whl_filename": "audioauth-1.0.0-py3-none-any.whl" }
```

### GET `/api/download?email=<email>`

Response: `application/octet-stream` — the `.whl` binary.

### POST `/api/verify`

**Request:** `email`, `file` (single audio)

```json
{
  "status": "ok",
  "confidence": 78.4,
  "cosine_score": 0.5840,
  "label": "Partial Match",
  "matched": true,
  "color": "amber",
  "icon": "fa-circle-half-stroke"
}
```

---

## 📁 Project Structure

```
Full_Working/
│
├── 📂 Backend/
│   └── 📂 your_server/
│       ├── main.py               — FastAPI app, all routes, static serving
│       ├── database.py           — CSV read/write, user management
│       ├── login.py              — auth validation, welcome email via SMTP
│       ├── requirements.txt
│       ├── .env.example          — SMTP config template
│       ├── 📂 pipeline/
│       │   ├── preprocess.py     — audio loading & cleaning (3-backend cascade)
│       │   ├── embedding.py      — ECAPA-TDNN inference + HuggingFace model load
│       │   ├── averaging.py      — N embeddings → 1 master voiceprint
│       │   ├── injector.py       — bake embedding into Python source code
│       │   └── builder.py        — python -m build → .whl package
│       ├── 📂 pretrained_models/
│       │   └── spkrec-ecapa-voxceleb/    — ECAPA-TDNN weights (auto-downloaded)
│       └── 📂 template/          — .whl template with {{EMBEDDING}} placeholder
│
├── 📂 Fronted/
│   ├── index.html                — Landing page
│   ├── auth.html                 — Login / Sign Up
│   ├── onboarding-type.html      — Individual vs. Company selector
│   ├── onboarding-record.html    — Voice recorder + file upload
│   ├── onboarding-company.html   — Bulk multi-person upload
│   ├── onboarding-processing.html — Pipeline visualizer + polling
│   ├── download.html             — SDK download + verify playground
│   ├── 📂 css/style.css          — Full design system (glassmorphism, tokens, animations)
│   └── 📂 js/
│       ├── api.js                — HTTP client + Session management
│       ├── main.js               — Navbar, footer, scroll-reveal
│       ├── recorder.js           — MediaRecorder API, WebRTC capture
│       ├── processing.js         — ECharts: MFCC, waveform, UMAP, embedding
│       └── hero-shader.js        — Three.js WebGL waveform shader
│
├── 📂 DataBase/
│   ├── login.csv                 — User registry (auto-created)
│   └── 📂 <username>/
│       ├── 📂 voices/            — Raw uploaded audio samples
│       └── embedding.npy         — 192-dim master voiceprint
│
├── 📂 workspaces/
│   └── 📂 <username>_<build_id>/
│       └── 📂 build/dist/
│           └── audioauth-*.whl
│
└── 📂 Screenshots/
    └── Screenshot 2026-08-01 190641.png
```

---

## 🚀 Local Setup & Installation

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| pip | latest |
| ffmpeg | optional (for .webm/.mp4 support) |
| SMTP access | Gmail App Password recommended |

### Step 1 — Clone

```bash
git clone https://github.com/mohitjadav/audio-classification-hub.git
cd audio-classification-hub/Full_Working
```

### Step 2 — Backend Setup

```bash
cd Backend/your_server
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### Step 3 — Configure Environment

```bash
cp .env.example .env
```

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

> **Gmail App Password:** Google Account → Security → 2-Step Verification → App Passwords → Generate

### Step 4 — Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

First startup downloads the ECAPA-TDNN model (~100MB):
```
[EMBEDDING] Path.symlink_to patched → fallback to copy on Windows.
[EMBEDDING] Downloading model to: pretrained_models/spkrec-ecapa-voxceleb
[EMBEDDING] Download complete.
[EMBEDDING] ECAPA-TDNN loaded successfully.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Subsequent starts use the cached model:
```
[EMBEDDING] Using cached model at: pretrained_models/spkrec-ecapa-voxceleb
```

### Step 5 — Open

Navigate to **`http://localhost:8000`**

---

## ⚙️ Configuration

| Variable | Default | Description |
|---|---|---|
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP port (TLS) |
| `SMTP_USER` | — | Sender email address |
| `SMTP_PASSWORD` | — | Gmail App Password |

**Audio constants** (`pipeline/preprocess.py`):

| Constant | Default | Description |
|---|---|---|
| `SR` | `16000` | Target sample rate (Hz) |
| `DURATION` | `3` | Seconds of audio per embedding |
| `MIN_SEC` | `2.0` | Minimum audio length accepted |

**Confidence thresholds** (`main.py` — `/api/verify`):

| Label | Threshold | `matched` |
|---|---|---|
| Strong Match | >= 82% | True |
| Partial Match | >= 65% | True |
| Weak Match | >= 45% | False |
| No Match | < 45% | False |

---

## 🔒 Security Considerations

| Area | Current State | Production Recommendation |
|---|---|---|
| Password Storage | Plain text in CSV | Hash with `bcrypt` or `argon2-cffi` |
| Session | `sessionStorage` (browser) | JWT tokens with `python-jose` |
| Database | CSV flat file | PostgreSQL with SQLAlchemy |
| CORS | `allow_origins=["*"]` | Restrict to your domain |
| File Validation | Extension + size checks | Also validate magic bytes |
| SMTP | Credentials in `.env` | Managed email (SendGrid, Postmark) |
| Rate Limiting | None | Add `slowapi` for `/api/process` |
| HTTPS | None (local dev) | Nginx reverse proxy + Let's Encrypt |

---

## 🗺️ Roadmap

- [ ] PostgreSQL + SQLAlchemy — replace CSV database
- [ ] JWT Authentication — stateless session tokens
- [ ] Password hashing — bcrypt
- [ ] Multi-tenancy — org-level API keys for B2B
- [ ] Anti-spoofing — liveness detection (replay attack prevention)
- [ ] Noise augmentation — improve robustness during registration
- [ ] Dashboard — admin panel with user management, verification logs
- [ ] Docker — `Dockerfile` + `docker-compose.yml` for one-command deployment
- [ ] HTTPS / Nginx — production deployment guide
- [ ] Model quantization — INT8 ECAPA-TDNN for faster CPU inference
- [ ] Webhook support — POST verification result to developer callback URL

---

## 👨‍💻 Author

<div align="center">

<br/>

### Mohit Jadav

**Full-Stack AI Engineer &nbsp;·&nbsp; Deep Learning &nbsp;·&nbsp; FastAPI &nbsp;·&nbsp; Voice Biometrics**

<br/>

> *"I don't just build models — I build systems that put intelligence in developers' hands without cloud dependency."*

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-MohitJadav-181717?style=for-the-badge&logo=github)](https://github.com/mohitjadav)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Mohit%20Jadav-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/mohitjadav)

<br/>

**Core Stack:** Python &nbsp;·&nbsp; FastAPI &nbsp;·&nbsp; PyTorch &nbsp;·&nbsp; SpeechBrain &nbsp;·&nbsp; NumPy &nbsp;·&nbsp; HTML/CSS/JS &nbsp;·&nbsp; TailwindCSS &nbsp;·&nbsp; Three.js

**Domains:** Machine Learning &nbsp;·&nbsp; Deep Learning &nbsp;·&nbsp; Audio AI &nbsp;·&nbsp; Web Development &nbsp;·&nbsp; Voice Biometrics &nbsp;·&nbsp; API Design

<br/>

---

*Built with passion for making AI accessible.*

*Audio Classification Hub &nbsp;—&nbsp; © 2026 Mohit Jadav. MIT License.*

</div>