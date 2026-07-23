"""Main FastAPI application."""
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
import uvicorn

from app.config import get_settings
from app.database import get_db, async_engine, Base
from app import models, schemas
from services.vision_service import get_vision_service
from services.nlp_service import get_nlp_service
from services.risk_service import get_risk_service
from services.recommendation_service import get_recommendation_service
from app.graph.crisis_state import CrisisState
from app.graph.crisis_graph import get_crisis_workflow
from app.llm.provider import get_llm_provider

# In-memory storage for active crisis states during workflow runs
active_crisis_states: dict = {}

settings = get_settings()


# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting up Disaster DSS API...")
    
    # Create database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created")
    yield
    
    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Driven Disaster & Homeland Security Decision Support System API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/", response_model=schemas.HealthCheck)
async def root():
    """Root endpoint with API info."""
    return schemas.HealthCheck(
        status="operational",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        services={
            "database": "connected",
            "ai_models": "loaded"
        }
    )


@app.get("/health", response_model=schemas.HealthCheck)
async def health_check():
    """Health check endpoint."""
    return schemas.HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        services={"api": "running"}
    )


# ============================================================================
# Incident Endpoints
# ============================================================================

@app.get("/api/v1/incidents", response_model=List[schemas.IncidentResponse])
async def list_incidents(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all incidents with optional filtering."""
    query = select(models.Incident)
    
    if status:
        query = query.where(models.Incident.status == status)
    
    query = query.order_by(desc(models.Incident.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return incidents


@app.post("/api/v1/incidents", response_model=schemas.IncidentResponse)
async def create_incident(
    incident: schemas.IncidentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new incident."""
    db_incident = models.Incident(
        type=incident.type,
        title=incident.title,
        description=incident.description,
        latitude=incident.latitude,
        longitude=incident.longitude,
        severity=incident.severity,
        status=models.IncidentStatus.ACTIVE,
        started_at=datetime.utcnow()
    )
    
    db.add(db_incident)
    await db.commit()
    await db.refresh(db_incident)
    
    # Create initial timeline event
    timeline_event = models.TimelineEvent(
        incident_id=db_incident.id,
        event_type="incident",
        title=f"{incident.type.value.upper()} Detected",
        description=incident.description or f"Severity: {incident.severity}/10",
        severity="critical" if incident.severity >= 7 else "warning",
        source="system"
    )
    db.add(timeline_event)
    await db.commit()
    
    return db_incident


@app.get("/api/v1/incidents/{incident_id}", response_model=schemas.IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific incident by ID."""
    result = await db.execute(
        select(models.Incident).where(models.Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident


# ============================================================================
# Zone Endpoints
# ============================================================================

@app.get("/api/v1/zones", response_model=List[schemas.ZoneResponse])
async def list_zones(
    incident_id: Optional[uuid.UUID] = None,
    risk_level: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List zones with optional filtering."""
    query = select(models.Zone)
    
    if incident_id:
        query = query.where(models.Zone.incident_id == incident_id)
    if risk_level:
        query = query.where(models.Zone.risk_level == risk_level)
    
    result = await db.execute(query)
    return result.scalars().all()


@app.post("/api/v1/zones", response_model=schemas.ZoneResponse)
async def create_zone(
    zone: schemas.ZoneCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new zone."""
    db_zone = models.Zone(
        incident_id=zone.incident_id,
        name=zone.name,
        coordinates=zone.coordinates,
        risk_level=zone.risk_level,
        damage_score=zone.damage_score,
        survival_probability=zone.survival_probability,
        population=zone.population,
        priority_score=0.0
    )
    
    db.add(db_zone)
    await db.commit()
    await db.refresh(db_zone)
    
    return db_zone


# ============================================================================
# Resource Endpoints
# ============================================================================

@app.get("/api/v1/resources", response_model=List[schemas.ResourceResponse])
async def list_resources(
    status: Optional[str] = None,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all resources with optional filtering."""
    query = select(models.Resource)
    
    if status:
        query = query.where(models.Resource.status == status)
    if type:
        query = query.where(models.Resource.type == type)
    
    result = await db.execute(query)
    return result.scalars().all()


@app.post("/api/v1/resources", response_model=schemas.ResourceResponse)
async def create_resource(
    resource: schemas.ResourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new resource."""
    db_resource = models.Resource(
        type=resource.type,
        name=resource.name,
        status=resource.status,
        latitude=resource.latitude,
        longitude=resource.longitude,
        capacity=resource.capacity,
        current_load=resource.current_load,
        zone_id=resource.zone_id
    )
    
    db.add(db_resource)
    await db.commit()
    await db.refresh(db_resource)
    
    return db_resource


@app.post("/api/v1/resources/{resource_id}/assign")
async def assign_resource(
    resource_id: uuid.UUID,
    zone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Assign a resource to a zone."""
    result = await db.execute(
        select(models.Resource).where(models.Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    resource.zone_id = zone_id
    resource.status = models.ResourceStatus.DEPLOYED
    resource.last_updated = datetime.utcnow()
    
    await db.commit()
    
    return {"status": "assigned", "resource_id": resource_id, "zone_id": zone_id}


# ============================================================================
# Analysis Endpoints
# ============================================================================

@app.post("/api/v1/analyze/image", response_model=schemas.AnalysisResultResponse)
async def analyze_image(
    file: UploadFile = File(...),
    incident_id: Optional[uuid.UUID] = None,
    zone_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """Analyze an image for damage detection."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG allowed.")
    
    # Read image data
    image_data = await file.read()
    
    if len(image_data) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size is 100MB.")
    
    # Save uploaded file
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as f:
        f.write(image_data)
    
    # Run AI analysis
    vision_service = get_vision_service()
    
    try:
        analysis_result = vision_service.detect_damage(image_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    # Save to database
    db_analysis = models.AnalysisResult(
        incident_id=incident_id,
        zone_id=zone_id,
        analysis_type="image",
        input_data={"filename": file.filename, "size": len(image_data)},
        results={
            "damage_score": analysis_result["damage_score"],
            "confidence": analysis_result["confidence"],
            "detection_count": len(analysis_result["detections"])
        },
        bounding_boxes=[d.model_dump() for d in analysis_result["detections"]],
        confidence=analysis_result["confidence"],
        explanation=analysis_result["explanation"]
    )
    
    db.add(db_analysis)
    await db.commit()
    await db.refresh(db_analysis)
    
    # Return response
    return schemas.AnalysisResultResponse(
        id=db_analysis.id,
        incident_id=db_analysis.incident_id,
        zone_id=db_analysis.zone_id,
        analysis_type="image",
        results=db_analysis.results,
        confidence=db_analysis.confidence,
        explanation=db_analysis.explanation,
        bounding_boxes=analysis_result["detections"],
        heatmap_url=analysis_result.get("heatmap"),
        created_at=db_analysis.created_at
    )


@app.post("/api/v1/analyze/text", response_model=schemas.AnalysisResultResponse)
async def analyze_text(
    text: str,
    source: str = "manual",
    incident_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """Analyze text (emergency report, social media post)."""
    nlp_service = get_nlp_service()
    
    try:
        analysis = nlp_service.analyze_emergency_report(text, source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    # Save to database
    db_analysis = models.AnalysisResult(
        incident_id=incident_id,
        analysis_type="text",
        input_data={"text": text[:500], "source": source},
        results=analysis,
        confidence=analysis.get("urgency_score", 0),
        explanation=analysis.get("summary", "")
    )
    
    db.add(db_analysis)
    await db.commit()
    await db.refresh(db_analysis)
    
    return schemas.AnalysisResultResponse(
        id=db_analysis.id,
        incident_id=db_analysis.incident_id,
        zone_id=None,
        analysis_type="text",
        results=analysis,
        confidence=db_analysis.confidence,
        explanation=db_analysis.explanation,
        bounding_boxes=None,
        heatmap_url=None,
        created_at=db_analysis.created_at
    )


# ============================================================================
# Risk Assessment Endpoints
# ============================================================================

@app.get("/api/v1/risk/zone/{zone_id}", response_model=schemas.ZoneRiskAssessment)
async def assess_zone_risk(
    zone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Calculate risk assessment for a specific zone."""
    # Get zone data
    result = await db.execute(
        select(models.Zone).where(models.Zone.id == zone_id)
    )
    zone = result.scalar_one_or_none()
    
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Get incident data
    incident_result = await db.execute(
        select(models.Incident).where(models.Incident.id == zone.incident_id)
    )
    incident = incident_result.scalar_one_or_none()
    
    # Get sensor data for zone
    sensor_result = await db.execute(
        select(models.SensorData).where(
            and_(
                models.SensorData.latitude.between(
                    min(c[0] for c in zone.coordinates) - 0.01,
                    max(c[0] for c in zone.coordinates) + 0.01
                ),
                models.SensorData.longitude.between(
                    min(c[1] for c in zone.coordinates) - 0.01,
                    max(c[1] for c in zone.coordinates) + 0.01
                )
            )
        )
    )
    sensors = sensor_result.scalars().all()
    
    # Get analysis results
    analysis_result = await db.execute(
        select(models.AnalysisResult).where(models.AnalysisResult.zone_id == zone_id)
    )
    analyses = analysis_result.scalars().all()
    
    # Calculate risk
    risk_service = get_risk_service()
    
    zone_data = {
        "id": zone.id,
        "name": zone.name,
        "population": zone.population,
        "damage_score": zone.damage_score,
        "coordinates": zone.coordinates
    }
    
    incident_data = {
        "id": incident.id if incident else None,
        "started_at": incident.started_at if incident else None,
        "severity": incident.severity if incident else 5
    }
    
    sensor_data_list = [
        {
            "sensor_type": s.sensor_type,
            "value": s.value,
            "is_anomaly": s.is_anomaly,
            "anomaly_score": s.anomaly_score
        }
        for s in sensors
    ]
    
    analysis_list = [
        {
            "analysis_type": a.analysis_type,
            "results": a.results,
            "confidence": a.confidence
        }
        for a in analyses
    ]
    
    assessment = risk_service.calculate_zone_risk(
        zone_data, incident_data, sensor_data_list, analysis_list
    )
    
    return assessment


# ============================================================================
# Recommendation Endpoints
# ============================================================================

@app.get("/api/v1/recommendations", response_model=List[schemas.RecommendationResponse])
async def list_recommendations(
    incident_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List recommendations with optional filtering."""
    query = select(models.Recommendation)
    
    if incident_id:
        query = query.where(models.Recommendation.incident_id == incident_id)
    if status:
        query = query.where(models.Recommendation.status == status)
    
    query = query.order_by(desc(models.Recommendation.created_at))
    
    result = await db.execute(query)
    return result.scalars().all()


@app.post("/api/v1/recommendations/generate/{zone_id}")
async def generate_recommendations(
    zone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Generate AI recommendations for a zone."""
    # Get zone
    zone_result = await db.execute(
        select(models.Zone).where(models.Zone.id == zone_id)
    )
    zone = zone_result.scalar_one_or_none()
    
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Get available resources
    resource_result = await db.execute(
        select(models.Resource).where(models.Resource.status == models.ResourceStatus.AVAILABLE)
    )
    resources = resource_result.scalars().all()
    
    available_resources = {}
    for r in resources:
        available_resources[r.type.value] = available_resources.get(r.type.value, 0) + 1
    
    # Get risk metrics
    risk_service = get_risk_service()
    zone_data = {
        "id": zone.id,
        "name": zone.name,
        "population": zone.population,
        "damage_score": zone.damage_score
    }
    
    risk_metrics = {
        "threat_level": zone.risk_level.value if hasattr(zone.risk_level, 'value') else zone.risk_level,
        "damage_severity": zone.damage_score,
        "survival_probability": zone.survival_probability
    }
    
    # Generate recommendations
    rec_service = get_recommendation_service()
    recommendations = rec_service.generate_recommendations(
        zone_data, risk_metrics, available_resources
    )
    
    # Save to database
    saved_recs = []
    for rec in recommendations:
        db_rec = models.Recommendation(
            incident_id=zone.incident_id,
            zone_id=zone_id,
            category=rec["category"],
            priority=models.RiskLevel(rec["priority"]),
            title=rec["title"],
            description=rec["description"],
            reasoning=rec["reasoning"],
            status="pending"
        )
        db.add(db_rec)
        saved_recs.append(db_rec)
    
    await db.commit()
    
    for rec in saved_recs:
        await db.refresh(rec)
    
    return {
        "zone_id": zone_id,
        "recommendations_count": len(recommendations),
        "recommendations": recommendations
    }


@app.post("/api/v1/recommendations/{recommendation_id}/execute")
async def execute_recommendation(
    recommendation_id: uuid.UUID,
    execute_data: schemas.RecommendationExecute,
    db: AsyncSession = Depends(get_db)
):
    """Mark a recommendation as executed."""
    result = await db.execute(
        select(models.Recommendation).where(models.Recommendation.id == recommendation_id)
    )
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.status = "executed"
    recommendation.executed_at = datetime.utcnow()
    recommendation.executed_by = execute_data.executed_by
    
    await db.commit()
    
    return {"status": "executed", "recommendation_id": recommendation_id}


# ============================================================================
# Timeline Endpoints
# ============================================================================

@app.get("/api/v1/timeline/{incident_id}", response_model=List[schemas.TimelineEventResponse])
async def get_timeline(
    incident_id: uuid.UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get timeline events for an incident."""
    result = await db.execute(
        select(models.TimelineEvent)
        .where(models.TimelineEvent.incident_id == incident_id)
        .order_by(desc(models.TimelineEvent.timestamp))
        .limit(limit)
    )
    
    return result.scalars().all()


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@app.get("/api/v1/dashboard/stats", response_model=schemas.DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    # Count incidents
    incident_result = await db.execute(select(models.Incident))
    total_incidents = len(incident_result.scalars().all())
    
    active_result = await db.execute(
        select(models.Incident).where(models.Incident.status == models.IncidentStatus.ACTIVE)
    )
    active_incidents = len(active_result.scalars().all())
    
    # Count critical zones
    critical_zones_result = await db.execute(
        select(models.Zone).where(models.Zone.risk_level == models.RiskLevel.CRITICAL)
    )
    critical_zones = len(critical_zones_result.scalars().all())
    
    # Calculate population at risk
    high_risk_zones_result = await db.execute(
        select(models.Zone).where(
            models.Zone.risk_level.in_([models.RiskLevel.CRITICAL, models.RiskLevel.HIGH])
        )
    )
    high_risk_zones = high_risk_zones_result.scalars().all()
    population_at_risk = sum(z.population for z in high_risk_zones)
    
    # Count resources
    available_resources_result = await db.execute(
        select(models.Resource).where(models.Resource.status == models.ResourceStatus.AVAILABLE)
    )
    available_resources = len(available_resources_result.scalars().all())
    
    deployed_resources_result = await db.execute(
        select(models.Resource).where(models.Resource.status == models.ResourceStatus.DEPLOYED)
    )
    deployed_resources = len(deployed_resources_result.scalars().all())
    
    # Count pending recommendations
    pending_rec_result = await db.execute(
        select(models.Recommendation).where(models.Recommendation.status == "pending")
    )
    pending_recommendations = len(pending_rec_result.scalars().all())
    
    return schemas.DashboardStats(
        total_incidents=total_incidents,
        active_incidents=active_incidents,
        critical_zones=critical_zones,
        total_population_at_risk=population_at_risk,
        available_resources=available_resources,
        deployed_resources=deployed_resources,
        pending_recommendations=pending_recommendations
    )


@app.get("/api/v1/dashboard/map")
async def get_map_data(
    incident_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all data needed for the map view."""
    # Get zones
    zones_query = select(models.Zone)
    if incident_id:
        zones_query = zones_query.where(models.Zone.incident_id == incident_id)
    
    zones_result = await db.execute(zones_query)
    zones = zones_result.scalars().all()
    
    # Get resources
    resources_result = await db.execute(select(models.Resource))
    resources = resources_result.scalars().all()
    
    # Get incidents
    incidents_result = await db.execute(
        select(models.Incident).where(models.Incident.status == models.IncidentStatus.ACTIVE)
    )
    incidents = incidents_result.scalars().all()
    
    return {
        "zones": [
            {
                "id": str(z.id),
                "name": z.name,
                "coordinates": z.coordinates,
                "risk_level": z.risk_level.value if hasattr(z.risk_level, 'value') else z.risk_level,
                "damage_score": z.damage_score,
                "survival_probability": z.survival_probability,
                "population": z.population
            }
            for z in zones
        ],
        "resources": [
            {
                "id": str(r.id),
                "type": r.type.value if hasattr(r.type, 'value') else r.type,
                "name": r.name,
                "status": r.status.value if hasattr(r.status, 'value') else r.status,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "zone_id": str(r.zone_id) if r.zone_id else None
            }
            for r in resources
        ],
        "incidents": [
            {
                "id": str(i.id),
                "type": i.type.value if hasattr(i.type, 'value') else i.type,
                "title": i.title,
                "latitude": i.latitude,
                "longitude": i.longitude,
                "severity": i.severity
            }
            for i in incidents
        ]
    }


# ============================================================================
# CrisisMind Multi-Agent Agentic AI Endpoints
# ============================================================================

@app.get("/api/v1/agents/health")
async def agents_health():
    """Health check for multi-agent platform and local LLM connectivity."""
    llm = get_llm_provider()
    llm_status = await llm.check_health()
    return {
        "status": "operational",
        "agents": [
            "INCIDENT_COMMANDER", "VISION_AGENT", "EMERGENCY_INTELLIGENCE_AGENT",
            "WEATHER_AGENT", "SENSOR_AGENT", "RISK_AGENT", "RESOURCE_AGENT",
            "ROUTE_AGENT", "RESPONSE_PLANNER", "CRITIC_AGENT", "MONITORING_AGENT"
        ],
        "llm": llm_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/incidents/{incident_id}/run-agent-workflow")
async def run_agent_workflow(
    incident_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Trigger the autonomous multi-agent CrisisMind workflow."""
    # Find incident
    try:
        inc_uuid = uuid.UUID(incident_id)
        result = await db.execute(select(models.Incident).where(models.Incident.id == inc_uuid))
        db_inc = result.scalar_one_or_none()
    except Exception:
        db_inc = None

    inc_type = db_inc.type.value if db_inc and hasattr(db_inc.type, 'value') else "flood"
    inc_title = db_inc.title if db_inc else "Vijayawada Urban Flood Emergency"

    # Initialize CrisisState
    state = CrisisState(
        incident_id=incident_id,
        incident_type=inc_type,
        title=inc_title,
        location={"latitude": db_inc.latitude if db_inc else 16.5062, "longitude": db_inc.longitude if db_inc else 80.6480},
        emergency_text_reports=[
            {"text": "Severe flooding reported near Downtown. 3 residents trapped in residential ground floor.", "source": "911_call"},
            {"text": "Bridge Structural Damage reported on Highway 16 near Industrial corridor.", "source": "field_report"}
        ],
        sensor_readings=[
            {"sensor_id": "SENS-WATER-01", "sensor_type": "water_level", "value": 4.8, "is_anomaly": True, "anomaly_score": 0.9},
            {"sensor_id": "SENS-TEMP-02", "sensor_type": "temperature", "value": 31.5, "is_anomaly": False, "anomaly_score": 0.1}
        ]
    )

    workflow = get_crisis_workflow()
    final_state = await workflow.execute(state)

    # Save state in memory
    active_crisis_states[incident_id] = final_state

    # Broadcast update via WebSocket
    await manager.broadcast({
        "type": "agent_workflow_complete",
        "incident_id": incident_id,
        "workflow_status": final_state.workflow_status,
        "replan_count": final_state.replan_count,
        "current_agent": final_state.current_agent,
        "timestamp": datetime.utcnow().isoformat()
    })

    return final_state.model_dump()


@app.get("/api/v1/incidents/{incident_id}/agent-status")
async def get_agent_status(incident_id: str):
    """Retrieve active agent state and trace logs for an incident."""
    if incident_id in active_crisis_states:
        return active_crisis_states[incident_id].model_dump()
    
    # Return initial default state if not yet triggered
    state = CrisisState(incident_id=incident_id, incident_type="flood", title="Active Emergency")
    return state.model_dump()


@app.post("/api/v1/incidents/{incident_id}/approve")
async def approve_response_plan(incident_id: str, approved_by: str = Query("Incident Commander")):
    """Commander approval of the proposed response plan."""
    if incident_id not in active_crisis_states:
        raise HTTPException(status_code=404, detail="No active plan found for this incident. Run agent workflow first.")

    state: CrisisState = active_crisis_states[incident_id]
    state.approval_status = "APPROVED"
    state.execution_status = "SIMULATED"
    state.workflow_status = "COMPLETED"

    state.record_step(
        agent="HUMAN_COMMANDER",
        action="APPROVE_PLAN",
        status="COMPLETED",
        summary=f"Plan officially APPROVED by {approved_by}. Tactical execution initiated (Simulated Mode).",
        confidence=1.0
    )

    await manager.broadcast({
        "type": "plan_approved",
        "incident_id": incident_id,
        "approved_by": approved_by,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "status": "APPROVED",
        "incident_id": incident_id,
        "approved_by": approved_by,
        "execution_mode": "SIMULATED",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/incidents/{incident_id}/reject")
async def reject_response_plan(incident_id: str, reason: str = Query("Commander requested revision")):
    """Commander rejection of response plan."""
    if incident_id not in active_crisis_states:
        raise HTTPException(status_code=404, detail="No active plan found for this incident.")

    state: CrisisState = active_crisis_states[incident_id]
    state.approval_status = "REJECTED"
    state.workflow_status = "REJECTED"

    state.record_step(
        agent="HUMAN_COMMANDER",
        action="REJECT_PLAN",
        status="FAILED",
        summary=f"Plan REJECTED by Incident Commander. Reason: {reason}",
        confidence=1.0,
        errors=[reason]
    )

    return {"status": "REJECTED", "incident_id": incident_id, "reason": reason}


@app.post("/api/v1/incidents/{incident_id}/modify")
async def modify_response_plan(incident_id: str, modifications: dict):
    """Commander modifications to response plan."""
    if incident_id not in active_crisis_states:
        raise HTTPException(status_code=404, detail="No active plan found for this incident.")

    state: CrisisState = active_crisis_states[incident_id]
    state.approval_status = "MODIFIED"
    if state.response_plan:
        state.response_plan["commander_modifications"] = modifications

    state.record_step(
        agent="HUMAN_COMMANDER",
        action="MODIFY_PLAN",
        status="COMPLETED",
        summary=f"Plan MODIFIED by Incident Commander with {len(modifications)} adjustments.",
        confidence=1.0
    )

    return {"status": "MODIFIED", "incident_id": incident_id, "modifications": modifications}


# ============================================================================
# WebSocket for Real-time Updates
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Echo back or process
            await websocket.send_json({
                "type": "ack",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
