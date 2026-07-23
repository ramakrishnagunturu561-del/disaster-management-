"""SQLAlchemy database models."""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, 
    Text, ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.database import Base


class IncidentStatus(str, PyEnum):
    ACTIVE = "active"
    CONTAINED = "contained"
    RESOLVED = "resolved"


class IncidentType(str, PyEnum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    HURRICANE = "hurricane"
    TERRORISM = "terrorism"
    INDUSTRIAL = "industrial"


class RiskLevel(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceType(str, PyEnum):
    AMBULANCE = "ambulance"
    RESCUE_TEAM = "rescue_team"
    DRONE = "drone"
    FIRE_TRUCK = "fire_truck"


class ResourceStatus(str, PyEnum):
    AVAILABLE = "available"
    DEPLOYED = "deployed"
    MAINTENANCE = "maintenance"


class Incident(Base):
    """Disaster incident model."""
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(SQLEnum(IncidentType), nullable=False)
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.ACTIVE)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Location (lat, lon)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Severity 1-10
    severity = Column(Integer, default=5)
    
    # Metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    zones = relationship("Zone", back_populates="incident", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="incident", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_incident_status', 'status'),
        Index('idx_incident_type', 'type'),
        Index('idx_incident_location', 'latitude', 'longitude'),
    )


class Zone(Base):
    """Geographic zone within an incident area."""
    __tablename__ = "zones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    name = Column(String(100), nullable=False)
    
    # Polygon coordinates (list of [lat, lon] pairs)
    coordinates = Column(JSON, nullable=False)
    
    # Risk assessment
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW)
    damage_score = Column(Float, default=0.0)  # 0-100
    survival_probability = Column(Float, default=100.0)  # 0-100
    population = Column(Integer, default=0)
    
    # Priority for response (calculated)
    priority_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", back_populates="zones")
    resources = relationship("Resource", back_populates="zone")
    
    __table_args__ = (
        Index('idx_zone_incident', 'incident_id'),
        Index('idx_zone_risk', 'risk_level'),
    )


class Resource(Base):
    """Emergency response resource."""
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(SQLEnum(ResourceType), nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(SQLEnum(ResourceStatus), default=ResourceStatus.AVAILABLE)
    
    # Current location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Capacity
    capacity = Column(Integer, default=1)
    current_load = Column(Integer, default=0)
    
    # Assignment
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    zone = relationship("Zone", back_populates="resources")
    
    __table_args__ = (
        Index('idx_resource_status', 'status'),
        Index('idx_resource_type', 'type'),
        Index('idx_resource_zone', 'zone_id'),
    )


class TimelineEvent(Base):
    """Chronological event in incident timeline."""
    __tablename__ = "timeline_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    
    event_type = Column(String(50), nullable=False)  # incident, alert, action, update
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="info")  # info, warning, critical
    
    # Optional zone reference
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True)
    
    # Source (sensor, social_media, manual, ai)
    source = Column(String(50), default="manual")
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", back_populates="timeline_events")
    
    __table_args__ = (
        Index('idx_timeline_incident', 'incident_id'),
        Index('idx_timeline_timestamp', 'timestamp'),
    )


class AnalysisResult(Base):
    """AI analysis results for images/text."""
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True)
    
    analysis_type = Column(String(50), nullable=False)  # image, text, sensor
    input_data = Column(JSON)  # Original input
    results = Column(JSON)  # Analysis output
    
    # Bounding boxes for image analysis
    bounding_boxes = Column(JSON, nullable=True)
    heatmap_url = Column(String(500), nullable=True)
    
    # Confidence score
    confidence = Column(Float, default=0.0)
    
    # Explanation
    explanation = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_analysis_incident', 'incident_id'),
        Index('idx_analysis_type', 'analysis_type'),
    )


class Recommendation(Base):
    """AI-generated recommendations."""
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True)
    
    category = Column(String(50), nullable=False)  # rescue, evacuation, surveillance, medical
    priority = Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM)
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    reasoning = Column(Text)  # AI explanation
    
    status = Column(String(20), default="pending")  # pending, executed, dismissed
    
    executed_at = Column(DateTime, nullable=True)
    executed_by = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_rec_incident', 'incident_id'),
        Index('idx_rec_status', 'status'),
        Index('idx_rec_priority', 'priority'),
    )


class SensorData(Base):
    """IoT sensor readings."""
    __tablename__ = "sensor_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_type = Column(String(50), nullable=False)  # seismic, temperature, radiation, flood
    sensor_id = Column(String(100), nullable=False)
    
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_sensor_type', 'sensor_type'),
        Index('idx_sensor_time', 'timestamp'),
        Index('idx_sensor_location', 'latitude', 'longitude'),
    )


class SocialMediaReport(Base):
    """Social media posts analyzed for intelligence."""
    __tablename__ = "social_media_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(50), nullable=False)
    external_id = Column(String(200), nullable=True)
    
    content = Column(Text, nullable=False)
    author = Column(String(100), nullable=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    sentiment = Column(String(20), default="neutral")  # negative, neutral, positive
    sentiment_score = Column(Float, default=0.0)
    
    is_urgent = Column(Boolean, default=False)
    urgency_score = Column(Float, default=0.0)
    
    # Extracted entities
    entities = Column(JSON, nullable=True)  # locations, organizations, etc.
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_social_platform', 'platform'),
        Index('idx_social_urgent', 'is_urgent'),
        Index('idx_social_sentiment', 'sentiment'),
    )


class WorkflowRun(Base):
    """Execution state of a multi-agent CrisisMind graph run."""
    __tablename__ = "workflow_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    status = Column(String(50), default="RUNNING")  # RUNNING, COMPLETED, FAILED, NEEDS_APPROVAL
    current_agent = Column(String(100), default="INCIDENT_COMMANDER")
    replan_count = Column(Integer, default=0)
    state_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentExecution(Base):
    """Audit log for individual agent steps."""
    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=True)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # STARTED, COMPLETED, FAILED, SKIPPED
    summary = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    errors = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class DecisionApproval(Base):
    """Human-in-the-loop commander approval audit record."""
    __tablename__ = "decision_approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=True)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    approval_status = Column(String(50), nullable=False)  # PROPOSED, APPROVED, MODIFIED, REJECTED
    approved_by = Column(String(100), nullable=True)
    modifications = Column(JSON, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """System-wide security and operational audit trail."""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

