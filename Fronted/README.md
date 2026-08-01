# Audio Classification Hub — Premium Voice Authentication Frontend

> **Your Voice. Your Identity. Zero Compromise.**

A full multi-page, premium, fully-animated frontend for a B2B voice-authentication SaaS platform.
Aesthetic: **cyberpunk-premium + scientific + trustworthy + futuristic** — near-black canvas, a central white-gold light bloom, and a custom **WebGL audio-wave shader** with chromatic aberration.

> ⚙️ **Note on stack**: The original spec targeted Next.js 14 + React Three Fiber + Recharts + shadcn/ui (a build-step toolchain). This deployment environment serves **static HTML/CSS/JS**, so the entire design has been faithfully recreated with **vanilla HTML + Tailwind (CDN) + Three.js (raw WebGL shader) + ECharts (charts) + custom CSS animations** — no build step, runs live anywhere. Every page, section, animation and micro-interaction from the brief is implemented.

---

## ✅ Completed Features

### Global
- **Custom WebGL Hero Shader** (`js/hero-shader.js`) — Three.js `RawShaderMaterial` with multi-band sine waves, chromatic aberration (R/G/B offset), purple→cyan→magenta→gold palette cycling, central brightness bloom, vertical falloff, scroll-based auto-dim, and a WebGL/reduced-motion fallback.
- **Radial white-gold bloom overlay** on every hero.
- **Sticky glassmorphism navbar** — transparent → frosted on scroll, animated 5-bar soundwave logo, mobile hamburger slide-in sheet.
- **Design token system** (`css/style.css`) matching the spec exactly (backgrounds, accent spectrum, bloom, text, borders).
- **Typography** — Space Grotesk (display 800 all-caps), Inter (headings/body), JetBrains Mono (code/metrics).
- **Micro-interactions** — fadeInUp scroll reveals w/ stagger, card hover lift + glow, button glow/active scale, input focus ring, success bounce, error shake, mic pulse rings, marquee, code-copy feedback, `prefers-reduced-motion` support.

### Pages
| Page | File | Highlights |
|------|------|-----------|
| **Landing** | `index.html` | Hero shader + bloom, How-It-Works 3-step flow, "2 Lines of Auth" code showcase, 7-card bento grid, 3-tier pricing (Team = "Most Popular"), infinite social-proof marquee, final CTA, footer |
| **Auth** | `auth.html` | Split layout (blurred shader left / glass card right), Login ⇄ Sign Up pill tabs, password show/hide, 4-segment password strength meter, Google/GitHub ghost buttons |
| **Account Type** | `onboarding-type.html` | 4-step stepper, Individual vs Team/Company selectable cards with checkmark bounce + glow, slide-up Continue button (routes by type) |
| **Voice Recording** | `onboarding-record.html` | Record/Upload tabs, 240px mic circle (idle pulse → recording rings + live mic-level scale → done check), **real Web Audio API + MediaRecorder**, 10s countdown, static waveform playback bar, 3-sample mini-wizard, drag-and-drop upload zone |
| **Company Upload** | `onboarding-company.html` | Dark spreadsheet-style bulk table, add-row, status badges, Import CSV modal overlay with sample import |
| **Processing** | `onboarding-processing.html` | **Showstopper** — left pipeline panel (animated step completion, elapsed timer, progress bar) + 2×2 viz grid: **MFCC heatmap** (canvas, draws column-by-column), **Waveform + Energy** (ECharts), **Pitch Contour F0** (ECharts animated draw), **192-dim Embedding bars** (canvas, staggered, cyan=+/magenta=−), plus full-width **UMAP scatter** (population / similar speakers / your voiceprint) |
| **Download + Docs** | `download.html` | Hero download banner + LangChain-style 3-column docs (sticky left nav, fluid content, sticky right TOC), syntax-highlighted code blocks with copy buttons, info/warning callouts, param tables, method signatures, scroll-spy active nav, prev/next |

---

## 🔗 Functional Entry URIs

| Path | Description | Routes to |
|------|-------------|-----------|
| `index.html` | Landing page | `auth.html`, `download.html`, `#pricing`, `#how` |
| `auth.html` | Login / Sign up | → `onboarding-type.html` on submit/OAuth |
| `onboarding-type.html` | Choose Individual vs Company | → `onboarding-record.html` (individual) / `onboarding-company.html` (company) |
| `onboarding-record.html` | Record/upload 3 voice samples | → `onboarding-processing.html` |
| `onboarding-company.html` | Bulk team enrollment | → `onboarding-processing.html` |
| `onboarding-processing.html` | Live embedding visualization | → `download.html` on completion |
| `download.html` | Package download + API docs | Anchors: `#installation`, `#quickstart`, `#voiceauth`, `#verify`, `#fastapi`, `#core-api`, etc. |

No query parameters required — flow state is held client-side per page.

---

## 📁 Project Structure
```
index.html                     ← Landing
auth.html                      ← Login / Sign up
onboarding-type.html           ← Individual vs Company
onboarding-record.html         ← Voice recording (Individual)
onboarding-company.html        ← Bulk upload (Company)
onboarding-processing.html     ← Visualization showstopper
download.html                  ← Docs + download (LangChain style)
css/
  └── style.css                ← Design tokens + all components/animations
js/
  ├── hero-shader.js           ← Three.js WebGL audio-wave shader
  ├── main.js                  ← Navbar, reveals, copy, footer/nav injectors
  ├── recorder.js              ← Web Audio API mic + record/upload logic
  └── processing.js            ← MFCC / waveform / pitch / embedding / UMAP viz
```

---

## 🧩 Libraries (all via CDN — no build step)
- **Tailwind CSS** (utility styling)
- **Three.js r160** (hero WebGL shader)
- **ECharts 5** (waveform, pitch, UMAP charts)
- **Font Awesome 6.4** (icons)
- **Google Fonts** — Space Grotesk, Inter, JetBrains Mono

---

## 🗄️ Data Models / Storage
This is a **frontend-only demo** — no backend or table storage is wired up. All flow state (recorded samples, selected account type, processing progress) is held in-memory in the browser. The documented `voiceauth` SDK (Python `.whl`, `.npy` embeddings) describes the conceptual backend product, not a live API in this build.

To make it data-driven later, the built-in RESTful Table API could store: `users`, `voice_profiles` (embedding metadata), and `verification_events` (webhook log).

---

## 🚧 Not Yet Implemented / Future Work
- Real audio → embedding inference (requires a Python/PyTorch backend; out of scope for static hosting).
- Actual `.whl` file generation & download endpoint (server-side).
- Persisting users/profiles via the Table API.
- Live OAuth (Google/GitHub) — currently navigates straight into onboarding.
- Node.js native SDK wrapper (documented as roadmap).

## ▶️ Recommended Next Steps
1. Wire `users` / `voice_profiles` tables via the RESTful Table API for persistence.
2. Connect `auth.html` to a real auth provider.
3. Replace the simulated processing pipeline with real backend progress events (SSE/websocket).
4. Add an OG image asset for social sharing.

---

## 🚀 Deployment
To publish this site and get a live URL, open the **Publish tab** — it handles deployment in one click.
