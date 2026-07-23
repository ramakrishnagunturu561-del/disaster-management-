# CrisisMind AI

### Agentic Disaster Intelligence & Emergency Decision Support System

> **From fragmented crisis data to coordinated, explainable action.**

CrisisMind AI is an agentic AI-powered disaster intelligence and emergency decision-support platform designed to transform fragmented crisis information into coordinated, explainable, and safety-validated response plans.

The platform combines a **multi-agent LangGraph architecture**, computer vision, NLP, live weather intelligence, IoT sensor analysis, risk assessment, resource allocation, evacuation planning, safety validation, and human-in-the-loop decision governance.

CrisisMind AI supports both:
- **Simulation Mode** for controlled disaster scenarios and demonstrations
- **Live Intelligence Mode** for real-world data-driven crisis analysis

---

## 🚨 Problem Statement

During floods, earthquakes, fires, cyclones, and other large-scale emergencies, critical information arrives from multiple disconnected sources:

- Drone and satellite imagery
- Live weather services
- IoT sensors
- Emergency reports & call logs
- Field personnel telemetry
- Hospitals and shelters
- Resource inventories
- Road and infrastructure status

Emergency teams must rapidly answer critical questions:
- Which areas are most critical?
- Where are people most at risk?
- Which evacuation routes are safe?
- Which shelters still have capacity?
- How should limited rescue resources be allocated?
- Is the proposed response plan actually safe and feasible?

CrisisMind AI addresses this problem using a coordinated **multi-agent AI system**.

---

## 🏗 System Architecture

```text
                    CRISISMIND AI
                         |
              OPERATIONAL MODE SELECTOR
                         |
          +--------------+--------------+
          |                             |
          v                             v
   SIMULATION MODE              LIVE INTELLIGENCE MODE
          |                             |
 Vijayawada Scenario             Real Location
 Simulated Sensors               Live Weather
 Predefined Resources            Uploaded Images
 Self-Correction Demo            Emergency Reports
          |                      IoT / Resource Data
          +-------------+---------------+
                        |
                        v
               SUPERVISOR AGENT
                        |
            +-----------+-----------+
            |           |           |
            v           v           v
        VISION      EMERGENCY    WEATHER
        AGENT       INTELLIGENCE  AGENT
            |           |           |
            +-----------+-----------+
                        |
                  SENSOR AGENT
                        |
                        v
                 RISK ASSESSMENT
                        |
             +----------+----------+
             |                     |
             v                     v
       RESOURCE AGENT         ROUTE AGENT
             |                     |
             +----------+----------+
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
        HUMAN APPROVAL      TARGETED REPLAN
               |                 |
               +--------<--------+
                        |
                        v
              FINAL RESPONSE PLAN
```

---

## 🤖 Multi-Agent Architecture

CrisisMind AI orchestrates autonomous agents using **LangGraph StateGraph**:

1. **Supervisor Agent (Incident Commander)**: Classifies incident type, evaluates available evidence, determines agent routing, and maintains shared crisis state.
2. **Vision Intelligence Agent**: Uses YOLOv8 and OpenCV to detect damage, objects, and structural hazards from drone/satellite images.
3. **Emergency Intelligence Agent**: Uses Transformers / DistilBERT / BERT NER to extract entities, locations, urgency indicators, and casualties from reports.
4. **Weather Intelligence Agent**: Integrates live meteorological telemetry (precipitation, wind, flood risk) via Open-Meteo API.
5. **Sensor Intelligence Agent**: Monitors IoT streams (water levels, smoke, temperature, gas leaks, seismic data) for threshold violations.
6. **Risk Assessment Agent**: Calculates priority scores, threat levels, and survival-risk metrics across affected zones.
7. **Resource Allocation Agent**: Assigns rescue teams, ambulances, boats, and drones under strict non-over-allocation constraints (`Allocated <= Available`).
8. **Evacuation / Route Agent**: Evaluates road blockages, shelter capacities, travel distances, and safe corridors.
9. **Response Planner Agent**: Synthesizes directives into structured operational proposals.
10. **Safety Critic Agent**: Audits proposals against safety constraints (`RESOURCE_OVERALLOCATED`, `SHELTER_CAPACITY_EXCEEDED`, `ROUTE_BLOCKED`, `STALE_WEATHER`, `UNMET_CRITICAL_RESOURCE_NEED`).

---

## 🔄 Self-Correction & Replanning Loop

Instead of failing silently or restarting execution from scratch, CrisisMind AI runs a feedback self-correction loop:

```text
Plan v1 ---> Safety Critic (FAIL: SHELTER_CAPACITY_EXCEEDED)
                 |
                 v
        Targeted Replanning (Route & Resource Agents)
                 |
                 v
Plan v2 ---> Safety Critic (PASS) ---> Awaiting Human Approval
```

---

## 👤 Human-in-the-Loop Governance

Decisions follow strict operational states:

```text
PROPOSED ---> AWAITING_HUMAN_APPROVAL ---> APPROVED / MODIFIED / REJECTED
```

- **Approve**: Authorize emergency deployment.
- **Modify**: Issue commander-level modifications to re-evaluate state.
- **Reject**: Reject proposed response plan with justification.
- **Human Override**: Override unresolved warnings with explicit logged reasoning.

---

## 🔍 Explainable AI & Provenance Tracking

- **Explainable AI (XAI)**: Breaks down decision reasoning into **Facts**, **Derived Metrics**, **Decision Rationale**, **Assumptions**, and **Warnings**.
- **Data Provenance**: Every output is tagged with transparent provenance categories:
  - `REAL` (Open-Meteo Weather, Field Data)
  - `USER_PROVIDED` (Uploaded Drone Images, Reports)
  - `SIMULATION` (Predefined Telemetry)
  - `DERIVED` (Risk Scores, Priorities)

---

## 🛠 Technology Stack

### Frontend (`/app`)
- **Core**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS, Radix UI, Lucide Icons
- **Mapping & Charts**: Leaflet, Recharts

### Backend (`/backend`)
- **Framework**: Python 3.14+, FastAPI, Pydantic v2
- **Agentic Orchestration**: LangGraph, LangChain Core
- **Computer Vision & NLP**: YOLOv8, OpenCV, HuggingFace Transformers, DistilBERT
- **Database & Services**: SQLAlchemy, AsyncPG, WebSockets, Open-Meteo API

---

## ⚙️ Installation & Setup Guide

### 1. Clone Repository
```bash
git clone <repository_url>
cd disaster-management-
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
```
- **Windows**: `.\venv\Scripts\Activate.ps1`
- **Linux/Mac**: `source venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

Start backend API:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup
In a new terminal:
```bash
cd app
npm install
npm run dev
```
- **Command Center Dashboard**: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Verification & Testing

Run full backend unit and integration test suite:
```bash
python -m pytest backend/tests/test_phase1.py backend/tests/test_phase2.py backend/tests/test_phase3.py backend/tests/test_phase5.py
```

Run standalone multi-agent verification:
```bash
python backend/tests/run_tests.py
```

Build production frontend:
```bash
cd app
npm run build
```

| Verification Suite | Test Count | Result |
|---|---|:---:|
| Phase 1 — Core Agentic Foundation | 10 / 10 | **PASS** |
| Phase 2 — Operational Intelligence | 5 / 5 | **PASS** |
| Phase 3 — Safety Critic & Self-Correction | 7 / 7 | **PASS** |
| Phase 5 — Dual-Mode Operational Suite | 3 / 3 | **PASS** |
| Multi-Agent Graph End-to-End Suite | 5 / 5 | **PASS** |
| Frontend TypeScript & Vite Build | 0 Errors | **PASS** |

---

## ⚠️ Safety & Responsible Use Disclaimer

CrisisMind AI is designed as a **decision-support, simulation, and research prototype**. It is not an independently authorized emergency dispatch authority. All AI-generated survival estimates, risk scores, evacuation routes, and resource allocations must be validated by authorized human incident commanders before operational deployment.

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**G. Venkata Ramakrishna**  
B.Tech — Artificial Intelligence & Machine Learning  
*Focus Areas*: Agentic AI, Multi-Agent Systems, Computer Vision, Full-Stack AI Applications
