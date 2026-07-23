"""Vision Intelligence Agent wrapping YOLOv8 and OpenCV services."""
import logging
from typing import Dict, Any, Optional
from app.graph.crisis_state import CrisisState
from services.vision_service import get_vision_service

logger = logging.getLogger(__name__)


class VisionAgent:
    """Agent responsible for aerial/drone/satellite disaster imagery damage detection."""

    def __init__(self):
        self.name = "VISION_AGENT"
        self.vision_service = get_vision_service()

    async def run(self, state: CrisisState) -> CrisisState:
        """Run computer vision detection on uploaded imagery."""
        state.record_step(
            agent=self.name,
            action="ANALYZE_IMAGE",
            status="STARTED",
            summary="Checking for available drone/satellite imagery"
        )

        if not state.drone_image_bytes:
            # Explicitly log UNAVAILABLE result without fabricating fake data
            state.vision_analysis = {
                "status": "UNAVAILABLE",
                "message": "No drone or satellite image payload provided for analysis.",
                "damage_severity": 0.0,
                "flood_extent": 0.0,
                "blocked_routes": [],
                "detections": [],
                "confidence": 0.0
            }
            state.warnings.append("Vision Agent: Live imagery payload unavailable for current state run.")
            state.record_step(
                agent=self.name,
                action="ANALYZE_IMAGE",
                status="SKIPPED",
                summary="No image data provided for computer vision processing",
                confidence=0.0
            )
            return state

        try:
            results = self.vision_service.detect_damage(state.drone_image_bytes)
            
            # Map detections to structured state
            detections_list = [
                {
                    "label": box.label,
                    "confidence": box.confidence,
                    "bounding_box": [box.x, box.y, box.width, box.height]
                }
                for box in results.get("detections", [])
            ]

            state.vision_analysis = {
                "status": "REAL_MODEL_RESULT",
                "damage_severity": results.get("damage_score", 0.0),
                "confidence": results.get("confidence", 0.0),
                "detections": detections_list,
                "explanation": results.get("explanation", ""),
                "heatmap_url": results.get("heatmap"),
                "image_size": results.get("image_size")
            }

            state.evidence.append({
                "source": "VISION_AGENT_YOLOV8",
                "type": "IMAGE_DETECTION",
                "detail": results.get("explanation"),
                "confidence": results.get("confidence", 0.0)
            })

            state.record_step(
                agent=self.name,
                action="ANALYZE_IMAGE",
                status="COMPLETED",
                summary=results.get("explanation"),
                confidence=results.get("confidence", 0.0)
            )
        except Exception as e:
            logger.error(f"Vision Agent error: {e}")
            state.vision_analysis = {
                "status": "ERROR",
                "message": f"Vision analysis encountered error: {str(e)}",
                "confidence": 0.0
            }
            state.record_step(
                agent=self.name,
                action="ANALYZE_IMAGE",
                status="FAILED",
                summary=f"Vision model error: {str(e)}",
                confidence=0.0,
                errors=[str(e)]
            )

        return state
