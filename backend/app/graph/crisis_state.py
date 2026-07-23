"""Typed Shared Crisis State for CrisisMind AI Multi-Agent Architecture."""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AgentHistoryStep(BaseModel):
    agent: str
    action: str
    status: str  # STARTED, COMPLETED, FAILED, WAITING
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    output_summary: Optional[str] = None
    confidence: Optional[float] = None
    errors: Optional[List[str]] = None


class CriticResult(BaseModel):
    passed: bool
    reasons: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CrisisState(BaseModel):
    """Unified Typed Shared State passed across all CrisisMind AI Agents."""

    # Incident Core Metadata
    incident_id: str
    incident_type: str  # flood, earthquake, fire, hurricane, industrial, etc.
    title: str = "Disaster Incident"
    location: Dict[str, float] = Field(default_factory=dict)  # {"latitude": 0.0, "longitude": 0.0}
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Raw / Uploaded Inputs
    drone_image_bytes: Optional[bytes] = None
    emergency_text_reports: List[Dict[str, Any]] = Field(default_factory=list)
    sensor_readings: List[Dict[str, Any]] = Field(default_factory=list)

    # Intelligence Agent Outputs
    vision_analysis: Optional[Dict[str, Any]] = None
    weather_intelligence: Optional[Dict[str, Any]] = None
    sensor_intelligence: Optional[Dict[str, Any]] = None
    emergency_reports: List[Dict[str, Any]] = Field(default_factory=list)
    social_intelligence: List[Dict[str, Any]] = Field(default_factory=list)

    # Risk Assessment
    risk_assessment: Optional[Dict[str, Any]] = None
    priority_zones: List[Dict[str, Any]] = Field(default_factory=list)
    population_exposure: int = 0

    # Operational Planning
    available_resources: Dict[str, int] = Field(default_factory=dict)
    resource_plan: Optional[Dict[str, Any]] = None
    route_analysis: Optional[Dict[str, Any]] = None
    evacuation_plan: Optional[Dict[str, Any]] = None
    response_plan: Optional[Dict[str, Any]] = None

    # Safety & Criticism
    critic_result: Optional[CriticResult] = None

    # Evidence & Trust Metadata
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)

    # Approval & Execution Controls
    approval_status: str = "PROPOSED"  # PROPOSED, UNDER_REVIEW, APPROVED, MODIFIED, REJECTED, EXECUTED, CANCELLED
    execution_status: str = "PENDING"   # PENDING, SIMULATED, EXECUTED, FAILED

    # Workflow Orchestration Traceability
    agent_history: List[AgentHistoryStep] = Field(default_factory=list)
    current_agent: str = "INCIDENT_COMMANDER"
    workflow_status: str = "INITIALIZED"  # RUNNING, COMPLETED, FAILED, NEEDS_APPROVAL
    replan_count: int = 0
    max_replan_limit: int = 3
    is_simulation: bool = True

    def record_step(self, agent: str, action: str, status: str, summary: Optional[str] = None, confidence: Optional[float] = None, errors: Optional[List[str]] = None):
        """Append agent step execution log."""
        self.agent_history.append(AgentHistoryStep(
            agent=agent,
            action=action,
            status=status,
            output_summary=summary,
            confidence=confidence,
            errors=errors
        ))
        self.current_agent = agent
        if confidence is not None:
            self.confidence_scores[agent] = confidence
