# Consumer AI Simulation — Backend API

FastAPI backend service powering the Consumer AI Over-Reliance behavioral simulation study.

---

## 1. Prerequisites

* **Python 3.12**
* **Conda** (Miniconda or Anaconda installed)

---

## 2. Environment Setup

### Using Conda (Recommended)

1. Open your terminal (PowerShell, Command Prompt, or Anaconda Prompt).
2. Create the dedicated Conda environment:
   ```bash
   conda create -n consumer-ai python=3.12 -y
   ```
3. Activate the environment:
   ```bash
   conda activate consumer-ai
   ```
4. Navigate to this directory and install dependencies:
   ```bash
   cd "{your-path}\backend"
   pip install -r requirements.txt
   ```

*(Alternatively, you can create directly from `environment.yml`: `conda env create -f environment.yml`)*

---

## 3. Configuration

An optional `.env` file can be created from the template:
```bash
cp .env.example .env
```

Default configuration in `app/core/config.py`:
* **Port:** `8000`
* **API Prefix:** `/api/v1`
* **CORS Origins:** `http://localhost:5173`

---

## 4. Running the Server

### With Conda Activated
```bash
conda activate consumer-ai
uvicorn app.main:app --reload --port 8000
```

### Or Single-Command Quick Start
Without manually changing terminal environments:
```bash
conda run -n consumer-ai --cwd "{your-path}\backend" uvicorn app.main:app --reload --port 8000
```

---

## 5. API Endpoints & Verification

Once running, access the interactive API docs:
* **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Check:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

### Core Routes:
* `GET /api/v1/health`: Service health status.
* `GET /api/v1/session/init`: Initializes participant session, randomly assigns condition (`control`, `human_free`, `ai_free`, `ai_structured`), and generates counterbalanced steer schedule.
* `GET /api/v1/trial/{trial_id}`: Returns trial stimuli products, Supplement Facts, and scenario text.
* `POST /api/v1/decision`: Records chosen product, open justification, and 0–100 confidence rating.

---

## 6. Directory Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes.py          # Active API endpoints
│   ├── core/
│   │   └── config.py          # Settings and CORS configuration
│   ├── data/
│   │   └── trials.py          # Trial stimuli data (Set A: Sleep & Recovery)
│   ├── models/
│   │   └── schemas.py         # Pydantic data models
│   └── main.py                # FastAPI entry point
├── .env.example
├── environment.yml
├── requirements.txt
└── README.md
```
