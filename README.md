# 🚨 CrisisMind AI: Agentic Disaster Intelligence & Emergency Decision Support System

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?style=flat&logo=react)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF6F00?style=flat)](https://langchain.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat&logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Transforming fragmented emergency data into explainable, safety-validated, and coordinated disaster response plans.**

CrisisMind AI is an advanced multi-agent disaster intelligence and emergency decision support system. Powered by **LangGraph**, **YOLOv8**, **BERT/Transformers**, **OpenCV**, and **FastAPI**, it continuously ingests real-time sensor streams, satellite/drone imagery, social/emergency reports, and weather telemetry to synthesize actionable evacuation and resource allocation strategies.

---

## 📌 Key Capabilities

- **🤖 Multi-Agent Orchestration**: Autonomous specialized agents (Supervisor, Vision, Emergency NLP, Weather, IoT Sensors, Risk Assessment, Resource Allocator, Evacuation Routing, and Safety Critic).
- **👁️ Computer Vision Damage Detection**: Real-time object and flood/structural damage recognition from aerial imagery using YOLOv8.
- **📄 Emergency Report NLP Analysis**: DistilBERT/BERT NER entity and urgency extraction from distress signals and emergency call logs.
- **🌤️ Live Weather & IoT Telemetry**: Integration with live meteorology APIs (Open-Meteo) and synthetic/live IoT threshold monitoring (water levels, smoke, gas, seismic activity).
- **🛡️ Self-Correction & Replanning**: Iterative safety loop where the **Safety Critic Agent** validates resource limits and route hazards before approving plans.
- **👤 Human-in-the-Loop Governance**: Multi-stage approval framework (`PROPOSED` ➔ `AWAITING_APPROVAL` ➔ `APPROVED` / `MODIFIED` / `REJECTED`).
- **💡 Explainable AI (XAI) & Data Provenance**: Complete tracking of data origins (`REAL`, `USER_PROVIDED`, `SIMULATION`, `DERIVED`) and step-by-step decision justification.

---

## 🏗 System Architecture

```text
                                +-----------------------------+
                                |        CRISISMIND AI        |
                                +--------------+--------------+
                                               |
                                   OPERATIONAL MODE SELECTOR
                                               |
                     +-------------------------+-------------------------+
                     |                                                   |
                     v                                                   v
             SIMULATION MODE                                   LIVE INTELLIGENCE MODE
        (Predefined Scenarios & Data)                   (Live Telemetry, Weather & Images)
                     |                                                   |
                     +-------------------------+-------------------------+
                                               |
                                               v
                                     SUPERVISOR AGENT
                                               |
                       +-----------------------+-----------------------+
                       |                       |                       |
                       v                       v                       v
                 VISION AGENT            EMERGENCY AGENT         WEATHER AGENT
                 (YOLOv8 Aerial)           (BERT NLP)           (Open-Meteo API)
                       |                       |                       |
                       +-----------------------+-----------------------+
                                               |
                                               v
                                          SENSOR AGENT
                                        (IoT Monitoring)
                                               |
                                               v
                                        RISK ASSESSMENT
                                               |
                             +-----------------+-----------------+
                             |                                   |
                             v                                   v
                      RESOURCE AGENT                       ROUTE AGENT
                    (Allocation Engine)                 (Evacuation Paths)
                             |                                   |
                             +-----------------+-----------------+
                                               |
                                               v
                                       RESPONSE PLANNER
                                               |
                                               v
                                         SAFETY CRITIC
                                               |
                                      +--------+--------+
                                      |                 |
                                    PASS               FAIL
                                      |                 |
                                      v                 v
                                HUMAN APPROVAL    TARGETED REPLAN
                                      |                 |
                                      +--------<--------+
                                               |
                                               v
                                     FINAL EXECUTABLE PLAN
```

---

## 📂 Repository Structure

```text
disaster-management-/
├── README.md                     # Root system documentation
├── BACKEND_ARCHITECTURE.md       # Comprehensive backend & agent design specifications
├── PRODUCTION_BUILD.md           # Production deployment & containerization guide
├── yolov8n.pt                    # Pre-trained YOLOv8 computer vision model weights
├── app/                          # Frontend React + TypeScript application
│   ├── src/                      # Source UI components, pages, hooks, and services
│   ├── package.json              # Frontend package dependencies & scripts
│   ├── vite.config.ts            # Vite bundler configuration
│   └── tailwind.config.js        # Design system & styling settings
├── backend/                      # Backend FastAPI + LangGraph services
│   ├── app/
│   │   ├── main.py               # Main FastAPI application entrypoint & API routes
│   │   ├── config.py             # Global application configuration & env loading
│   │   ├── database.py           # Database connections & session handling
│   │   ├── models.py             # ORM database models
│   │   ├── schemas.py            # Pydantic schemas for data validation
│   │   ├── agents/               # Multi-agent implementations
│   │   ├── graph/                # LangGraph StateGraph orchestration
│   │   └── validators/           # Safety critic and validation engines
│   ├── tests/                    # Unit, integration, and agent verification test suite
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Backend container definition
│   └── docker-compose.yml        # Multi-container service setup
└── uploads/                      # Image and file upload storage directory
```

---

## ⚙️ Quick Start Guide

### Prerequisites
- **Node.js**: `v18.x` or higher
- **Python**: `v3.11` or higher
- **Git**

---

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/disaster-management.git
cd disaster-management-
```

---

### 2. Backend Setup
Navigate to the `backend` directory, create a virtual environment, and install dependencies:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Launch the FastAPI application:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- 🌐 **Interactive API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- ⚙️ **ReDoc API Spec**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 3. Frontend Setup
Open a new terminal window and navigate to the `app` directory:

```bash
cd app

# Install dependencies
npm install

# Start development server
npm run dev
```
- 🖥️ **Command Center UI**: [http://localhost:5173](http://localhost:5173)

---

### 4. Running with Docker (Optional)
To spin up all services via Docker:
```bash
cd backend
docker-compose up -d --build
```

---

## 🧪 Testing & Verification

CrisisMind AI features comprehensive automated tests covering unit components, multi-agent workflows, and safety verification loops.

### Run Backend Tests
```bash
# Run pytest phase suites
python -m pytest backend/tests/test_phase1.py backend/tests/test_phase2.py backend/tests/test_phase3.py backend/tests/test_phase5.py

# Run standalone multi-agent graph verification
python backend/tests/run_tests.py
```

### Build & Verify Frontend
```bash
cd app
npm run build
```

| Verification Suite | Test Count | Result |
|---|---|:---:|
| **Phase 1** — Core Agentic Foundation | 10 / 10 | **PASS** |
| **Phase 2** — Operational Intelligence | 5 / 5 | **PASS** |
| **Phase 3** — Safety Critic & Self-Correction | 7 / 7 | **PASS** |
| **Phase 5** — Dual-Mode Operational Suite | 3 / 3 | **PASS** |
| **Multi-Agent Graph End-to-End** | 5 / 5 | **PASS** |
| **Frontend TypeScript & Build** | 0 Errors | **PASS** |

---

## ⚠️ Responsible AI & Safety Disclaimer

CrisisMind AI is designed strictly as an **emergency decision support and simulation tool**. All AI-generated survival predictions, damage assessments, evacuation routes, and resource allocation directives **must be validated by certified human incident commanders** prior to physical deployment.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 👨‍💻 Author & Maintainers

**G. Venkata Ramakrishna**  
*B.Tech — Artificial Intelligence & Machine Learning*  
- **Specializations**: Agentic AI Systems, Multi-Agent Orchestration, Computer Vision, Full-Stack AI Engineering.
