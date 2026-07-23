"""NLP service for text analysis and classification."""
import re
from typing import Dict, Any, List, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    pipeline
)

from app.config import get_settings

settings = get_settings()


class NLPService:
    """Service for natural language processing."""
    
    # Emergency keywords for urgency detection
    URGENT_KEYWORDS = [
        "emergency", "help", "trapped", "injured", "dying", "fire", 
        "flood", "collapse", "explosion", "bleeding", "unconscious",
        "heart attack", "can't breathe", "dying", "please help",
        "911", "ambulance", "rescue", "save me", "dying"
    ]
    
    # Location patterns
    LOCATION_PATTERNS = [
        r"\b(at|near|by|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"\b(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd))",
        r"\b(latitude|lat)\s*[:=]?\s*(-?\d+\.?\d*)",
        r"\b(longitude|lon|long)\s*[:=]?\s*(-?\d+\.?\d*)",
    ]
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.classifier = None
        self.ner_pipeline = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    def _load_models(self):
        """Load NLP models."""
        if os.getenv("SKIP_TRANSFORMER_DOWNLOAD", "0") == "1":
            print("Skipping heavy transformer downloads for fast execution mode.")
            return

        try:
            # Load sentiment analysis model
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.cuda.is_available() else -1
            )
            print("Loaded sentiment analysis model")
        except Exception as e:
            print(f"Error loading sentiment model: {e}")
        
        try:
            # Load emergency classification model
            self.classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased",
                device=0 if torch.cuda.is_available() else -1
            )
            print("Loaded text classifier")
        except Exception as e:
            print(f"Error loading classifier: {e}")
        
        try:
            # Load NER pipeline
            self.ner_pipeline = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple",
                device=0 if torch.cuda.is_available() else -1
            )
            print("Loaded NER model")
        except Exception as e:
            print(f"Error loading NER model: {e}")
    
    def analyze_emergency_report(
        self, 
        text: str,
        source: str = "unknown"
    ) -> Dict[str, Any]:
        """Analyze an emergency report or call transcript.
        
        Args:
            text: The report text
            source: Source of the report (call, social_media, etc.)
            
        Returns:
            Analysis results with classification, entities, and urgency
        """
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(cleaned_text)
        
        # Detect urgency
        urgency = self._detect_urgency(cleaned_text)
        
        # Extract entities
        entities = self._extract_entities(cleaned_text)
        
        # Classify emergency type
        emergency_type = self._classify_emergency(cleaned_text)
        
        # Extract location hints
        locations = self._extract_locations(cleaned_text)
        
        # Generate summary
        summary = self._generate_summary(cleaned_text, emergency_type, urgency)
        
        return {
            "text": cleaned_text,
            "sentiment": sentiment["label"],
            "sentiment_score": sentiment["score"],
            "is_urgent": urgency["is_urgent"],
            "urgency_score": urgency["score"],
            "emergency_type": emergency_type["type"],
            "emergency_confidence": emergency_type["confidence"],
            "entities": entities,
            "locations": locations,
            "summary": summary,
            "source": source
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.strip()
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        if self.sentiment_analyzer is None:
            return {"label": "neutral", "score": 0.5}
        
        try:
            result = self.sentiment_analyzer(text[:512])[0]  # Truncate for model
            return {
                "label": result["label"].lower(),
                "score": round(result["score"], 3)
            }
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {"label": "neutral", "score": 0.5}
    
    def _detect_urgency(self, text: str) -> Dict[str, Any]:
        """Detect urgency level in text."""
        text_lower = text.lower()
        
        # Count urgent keywords
        keyword_matches = sum(
            1 for keyword in self.URGENT_KEYWORDS 
            if keyword in text_lower
        )
        
        # Calculate urgency score
        urgency_score = min(keyword_matches / 3, 1.0)  # Normalize to 0-1
        
        # Check for exclamation marks and caps (indicators of urgency)
        if text.count('!') > 1:
            urgency_score += 0.1
        if sum(1 for c in text if c.isupper()) > len(text) * 0.3:
            urgency_score += 0.1
        
        urgency_score = min(urgency_score, 1.0)
        
        return {
            "is_urgent": urgency_score > 0.3,
            "score": round(urgency_score, 3)
        }
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text."""
        if self.ner_pipeline is None:
            return []
        
        try:
            entities = self.ner_pipeline(text[:512])
            return [
                {
                    "text": e["word"],
                    "label": e["entity_group"],
                    "score": round(e["score"], 3)
                }
                for e in entities
            ]
        except Exception as e:
            print(f"NER error: {e}")
            return []
    
    def _classify_emergency(self, text: str) -> Dict[str, Any]:
        """Classify the type of emergency."""
        text_lower = text.lower()
        
        # Keyword-based classification
        emergency_keywords = {
            "medical": ["injured", "hurt", "bleeding", "heart", "breathing", "unconscious", "pain"],
            "fire": ["fire", "burning", "smoke", "flames"],
            "structural": ["collapse", "building", "structure", "trapped", "under rubble"],
            "flood": ["flood", "water", "drowning", "submerged"],
            "earthquake": ["earthquake", "quake", "tremor", "shaking"],
            "violence": ["shooting", "gun", "attacker", "violent", "hostage"],
        }
        
        scores = {}
        for emergency_type, keywords in emergency_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[emergency_type] = score
        
        # Get highest scoring type
        if max(scores.values()) > 0:
            emergency_type = max(scores, key=scores.get)
            confidence = min(scores[emergency_type] / 2, 1.0)
        else:
            emergency_type = "unknown"
            confidence = 0.0
        
        return {
            "type": emergency_type,
            "confidence": round(confidence, 3)
        }
    
    def _extract_locations(self, text: str) -> List[Dict[str, Any]]:
        """Extract location mentions from text."""
        locations = []
        
        for pattern in self.LOCATION_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                locations.append({
                    "text": match.group(0),
                    "type": "address" if "Street" in match.group(0) or "St" in match.group(0) else "location"
                })
        
        return locations
    
    def _generate_summary(
        self, 
        text: str, 
        emergency_type: Dict[str, Any],
        urgency: Dict[str, Any]
    ) -> str:
        """Generate a brief summary of the report."""
        urgency_text = "URGENT: " if urgency["is_urgent"] else ""
        type_text = emergency_type["type"].upper() if emergency_type["type"] != "unknown" else "EMERGENCY"
        
        # Truncate text for summary
        summary_text = text[:150] + "..." if len(text) > 150 else text
        
        return f"{urgency_text}{type_text} - {summary_text}"
    
    def batch_analyze(
        self, 
        texts: List[str],
        source: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """Analyze multiple texts in batch."""
        return [
            self.analyze_emergency_report(text, source)
            for text in texts
        ]


# Singleton instance
_nlp_service: Optional[NLPService] = None


def get_nlp_service() -> NLPService:
    """Get or create NLP service singleton."""
    global _nlp_service
    if _nlp_service is None:
        _nlp_service = NLPService()
    return _nlp_service
