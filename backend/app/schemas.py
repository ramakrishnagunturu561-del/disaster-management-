"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models import (
    IncidentStatus, IncidentType, RiskLevel, 
    ResourceType, ResourceStatus
)


# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Zone schemas
class ZoneBase(BaseSchema):
    name: str
    coordinates: List[List[float]]  # [[lat, lon], ...]
    risk_level: RiskLevel = RiskLevel.LOW
    damage_score: float = Field(ge=0, le=100, default=0)
    survival_probability: float = Field(ge=0, le=100, default=100)
    population: int = Field(ge=0, default=0)


class ZoneCreate(ZoneBase):
    incident_id: UUID


class ZoneResponse(ZoneBase):
    id: UUID
    incident_id: UUID
    priority_score: float
    created_at: datetime
    updated_at: datetime


# Resource schemas
class ResourceBase(BaseSchema):
    type: ResourceType
    name: str
    status: ResourceStatus = ResourceStatus.AVAILABLE
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: int = Field(ge=1, default=1)
    current_load: int = Field(ge=0, default=0)


class ResourceCreate(ResourceBase):
    zone_id: Optional[UUID] = None


class ResourceResponse(ResourceBase):
    id: UUID
    zone_id: Optional[UUID]
    last_updated: datetime
    created_at: datetime


# Incident schemas
class IncidentBase(BaseSchema):
    type: IncidentType
    title: str
    description: Optional[str] = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    severity: int = Field(ge=1, le=10, default=5)


class IncidentCreate(IncidentBase):
    pass


class IncidentResponse(IncidentBase):
    id: UUID
    status: IncidentStatus
    started_at: datetime
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    zones: List[ZoneResponse] = []


# Timeline event schemas
class TimelineEventBase(BaseSchema):
    event_type: str  # incident, alert, action, update
    title: str
    description: Optional[str] = None
    severity: str = "info"  # info, warning, critical
    zone_id: Optional[UUID] = None
    source: str = "manual"


class TimelineEventCreate(TimelineEventBase):
    incident_id: UUID


class TimelineEventResponse(TimelineEventBase):
    id: UUID
    incident_id: UUID
    timestamp: datetime
    created_at: datetime


# Analysis result schemas
class BoundingBox(BaseSchema):
    x: float
    y: float
    width: float
    height: float
    label: str
    confidence: float = Field(ge=0, le=1)


class AnalysisResultBase(BaseSchema):
    analysis_type: str  # image, text, sensor
    results: Dict[str, Any]
    confidence: float = Field(ge=0, le=1, default=0)
    explanation: Optional[str] = None


class AnalysisResultCreate(AnalysisResultBase):
    incident_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    input_data: Optional[Dict[str, Any]] = None
    bounding_boxes: Optional[List[BoundingBox]] = None


class AnalysisResultResponse(AnalysisResultBase):
    id: UUID
    incident_id: Optional[UUID]
    zone_id: Optional[UUID]
    bounding_boxes: Optional[List[BoundingBox]]
    heatmap_url: Optional[str]
    created_at: datetime


# Recommendation schemas
class RecommendationBase(BaseSchema):
    category: str  # rescue, evacuation, surveillance, medical
    priority: RiskLevel = RiskLevel.MEDIUM
    title: str
    description: str
    reasoning: Optional[str] = None


class RecommendationCreate(RecommendationBase):
    incident_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None


class RecommendationResponse(RecommendationBase):
    id: UUID
    incident_id: Optional[UUID]
    zone_id: Optional[UUID]
    status: str  # pending, executed, dismissed
    executed_at: Optional[datetime]
    executed_by: Optional[str]
    created_at: datetime


class RecommendationExecute(BaseSchema):
    executed_by: str


# Sensor data schemas
class SensorDataBase(BaseSchema):
    sensor_type: str  # seismic, temperature, radiation, flood
    sensor_id: str
    value: float
    unit: str
    latitude: float
    longitude: float


class SensorDataCreate(SensorDataBase):
    is_anomaly: bool = False
    anomaly_score: float = 0.0


class SensorDataResponse(SensorDataBase):
    id: UUID
    is_anomaly: bool
    anomaly_score: float
    timestamp: datetime


# Social media schemas
class SocialMediaReportBase(BaseSchema):
    platform: str
    content: str
    author: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SocialMediaReportCreate(SocialMediaReportBase):
    external_id: Optional[str] = None
    sentiment: str = "neutral"
    sentiment_score: float = 0.0
    is_urgent: bool = False
    urgency_score: float = 0.0
    entities: Optional[Dict[str, Any]] = None


class SocialMediaReportResponse(SocialMediaReportBase):
    id: UUID
    external_id: Optional[str]
    sentiment: str
    sentiment_score: float
    is_urgent: bool
    urgency_score: float
    entities: Optional[Dict[str, Any]]
    timestamp: datetime
    created_at: datetime


# Risk assessment schemas
class RiskMetrics(BaseSchema):
    damage_severity: float = Field(ge=0, le=100)
    survival_probability: float = Field(ge=0, le=100)
    threat_level: RiskLevel
    priority_score: float


class ZoneRiskAssessment(BaseSchema):
    zone_id: UUID
    metrics: RiskMetrics
    factors: Dict[str, float]  # breakdown of scoring factors


# Dashboard schemas
class DashboardStats(BaseSchema):
    total_incidents: int
    active_incidents: int
    critical_zones: int
    total_population_at_risk: int
    available_resources: int
    deployed_resources: int
    pending_recommendations: int


class ResourceAllocationRequest(BaseSchema):
    zone_id: UUID
    resource_type: ResourceType
    count: int = Field(ge=1, default=1)


# Image upload schemas
class ImageUploadResponse(BaseSchema):
    image_id: str
    url: str
    status: str
    message: str


# WebSocket message schemas
class WebSocketMessage(BaseSchema):
    type: str  # update, alert, notification
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health check
class HealthCheck(BaseSchema):
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]
