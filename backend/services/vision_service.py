"""Computer Vision service for damage detection."""
import os
import io
import base64
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import cv2
import torch
from ultralytics import YOLO

from app.config import get_settings
from app.schemas import BoundingBox

settings = get_settings()


class VisionService:
    """Service for image analysis and damage detection."""
    
    # Damage detection classes
    DAMAGE_CLASSES = {
        0: "Building Damage",
        1: "Structural Collapse",
        2: "Debris",
        3: "Fire",
        4: "Flood Water",
        5: "Road Damage",
        6: "Bridge Damage",
    }
    
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_model()
    
    def _load_model(self):
        """Load the YOLO model for damage detection."""
        try:
            # Try to load custom trained model
            model_path = settings.YOLO_MODEL_PATH
            if os.path.exists(model_path):
                self.model = YOLO(model_path)
                print(f"Loaded custom YOLO model from {model_path}")
            else:
                # Fall back to pre-trained COCO model
                self.model = YOLO("yolov8n.pt")
                print("Loaded default YOLOv8n model")
            
            self.model.to(self.device)
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Preprocess image for model inference."""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Convert to numpy array
        img_array = np.array(image)
        
        return img_array
    
    def detect_damage(
        self, 
        image_data: bytes,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45
    ) -> Dict[str, Any]:
        """Detect damage in an image.
        
        Args:
            image_data: Raw image bytes
            confidence_threshold: Minimum confidence for detections
            iou_threshold: IoU threshold for NMS
            
        Returns:
            Dictionary with detections, damage score, and heatmap
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Preprocess image
        img_array = self.preprocess_image(image_data)
        
        # Run inference
        results = self.model(
            img_array,
            conf=confidence_threshold,
            iou=iou_threshold,
            device=self.device
        )
        
        # Parse results
        detections = []
        damage_score = 0.0
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Get class name
                    class_name = self.DAMAGE_CLASSES.get(
                        class_id, 
                        f"Class {class_id}"
                    )
                    
                    detection = BoundingBox(
                        x=float(x1),
                        y=float(y1),
                        width=float(x2 - x1),
                        height=float(y2 - y1),
                        label=class_name,
                        confidence=confidence
                    )
                    detections.append(detection)
                    
                    # Accumulate damage score
                    damage_score += confidence * 100
        
        # Normalize damage score (cap at 100)
        damage_score = min(damage_score / max(len(detections), 1), 100)
        
        # Generate heatmap
        heatmap = self._generate_heatmap(img_array, detections)
        
        # Generate explanation
        explanation = self._generate_explanation(detections, damage_score)
        
        return {
            "detections": detections,
            "damage_score": round(damage_score, 2),
            "heatmap": heatmap,
            "confidence": round(
                np.mean([d.confidence for d in detections]) if detections else 0, 
                2
            ),
            "explanation": explanation,
            "image_size": {
                "width": img_array.shape[1],
                "height": img_array.shape[0]
            }
        }
    
    def _generate_heatmap(
        self, 
        image: np.ndarray, 
        detections: List[BoundingBox]
    ) -> str:
        """Generate a heatmap overlay for detected damage.
        
        Returns:
            Base64 encoded heatmap image
        """
        # Create blank heatmap
        heatmap = np.zeros((image.shape[0], image.shape[1]), dtype=np.float32)
        
        # Add Gaussian blobs for each detection
        for det in detections:
            center_x = int(det.x + det.width / 2)
            center_y = int(det.y + det.height / 2)
            radius = int(max(det.width, det.height) / 2)
            
            # Create Gaussian
            y, x = np.ogrid[:image.shape[0], :image.shape[1]]
            gaussian = np.exp(
                -((x - center_x)**2 + (y - center_y)**2) / (2 * radius**2)
            )
            heatmap += gaussian * det.confidence
        
        # Normalize
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        # Convert to colormap
        heatmap_colored = cv2.applyColorMap(
            (heatmap * 255).astype(np.uint8), 
            cv2.COLORMAP_JET
        )
        
        # Blend with original image
        alpha = 0.6
        overlay = cv2.addWeighted(
            image[:, :, ::-1],  # BGR to RGB
            1 - alpha, 
            heatmap_colored, 
            alpha, 
            0
        )
        
        # Encode to base64
        _, buffer = cv2.imencode('.png', overlay)
        heatmap_b64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/png;base64,{heatmap_b64}"
    
    def _generate_explanation(
        self, 
        detections: List[BoundingBox], 
        damage_score: float
    ) -> str:
        """Generate human-readable explanation of the analysis."""
        if not detections:
            return "No significant damage detected in the analyzed image."
        
        # Count by damage type
        damage_counts = {}
        for det in detections:
            damage_counts[det.label] = damage_counts.get(det.label, 0) + 1
        
        # Build explanation
        damage_types = ", ".join([
            f"{count} {damage_type}(s)" 
            for damage_type, count in damage_counts.items()
        ])
        
        severity = (
            "critical" if damage_score > 75 else
            "severe" if damage_score > 50 else
            "moderate" if damage_score > 25 else
            "minor"
        )
        
        explanation = (
            f"AI analysis detected {len(detections)} damage regions with "
            f"{severity} severity ({damage_score:.1f}%). "
            f"Primary findings: {damage_types}. "
        )
        
        # Add recommendations based on damage type
        if "Structural Collapse" in damage_counts:
            explanation += "Structural collapse detected - immediate rescue response recommended. "
        if "Fire" in damage_counts:
            explanation += "Fire detected - fire suppression units should be deployed. "
        if "Flood Water" in damage_counts:
            explanation += "Flooding detected - evacuation may be necessary. "
        
        return explanation
    
    def segment_damage(
        self, 
        image_data: bytes,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Perform semantic segmentation for precise damage mapping."""
        # This would use a segmentation model like U-Net
        # For now, return placeholder
        return {
            "segmentation_mask": None,
            "damage_areas": [],
            "total_damage_area": 0
        }


# Singleton instance
_vision_service: Optional[VisionService] = None


def get_vision_service() -> VisionService:
    """Get or create vision service singleton."""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service
