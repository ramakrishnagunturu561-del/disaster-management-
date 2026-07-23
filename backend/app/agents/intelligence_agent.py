"""Emergency Intelligence Agent wrapping Transformer NLP service."""
import logging
from typing import Dict, Any, List
from app.graph.crisis_state import CrisisState
from services.nlp_service import get_nlp_service

logger = logging.getLogger(__name__)


class EmergencyIntelligenceAgent:
    """Agent responsible for analyzing textual crisis communications, 911 transcripts, and field reports."""

    def __init__(self):
        self.name = "EMERGENCY_INTELLIGENCE_AGENT"
        self.nlp_service = get_nlp_service()

    async def run(self, state: CrisisState) -> CrisisState:
        """Process all incoming text reports and social messages."""
        state.record_step(
            agent=self.name,
            action="ANALYZE_TEXT_REPORTS",
            status="STARTED",
            summary=f"Processing {len(state.emergency_text_reports)} text reports"
        )

        analyzed_reports = []
        high_urgency_count = 0

        for report in state.emergency_text_reports:
            text = report.get("text", "")
            source = report.get("source", "field_report")
            
            if not text:
                continue

            try:
                nlp_res = self.nlp_service.analyze_emergency_report(text, source=source)
                analyzed_reports.append(nlp_res)

                if nlp_res.get("is_urgent"):
                    high_urgency_count += 1

                # Append evidence record
                state.evidence.append({
                    "source": f"NLP_BERT_{source.upper()}",
                    "type": "TEXT_ANALYSIS",
                    "detail": nlp_res.get("summary"),
                    "urgency_score": nlp_res.get("urgency_score", 0.0),
                    "emergency_type": nlp_res.get("emergency_type")
                })
            except Exception as e:
                logger.error(f"Error processing text report: {e}")

        state.emergency_reports = analyzed_reports

        summary_msg = f"Analyzed {len(analyzed_reports)} reports. Identified {high_urgency_count} high-urgency reports."
        
        # Social media reports unverified warning policy
        if any(r.get("source") == "social_media" for r in analyzed_reports):
            state.warnings.append("Social media intelligence included. Unverified reports tagged pending corroboration.")

        state.record_step(
            agent=self.name,
            action="ANALYZE_TEXT_REPORTS",
            status="COMPLETED",
            summary=summary_msg,
            confidence=0.88 if analyzed_reports else 0.5
        )

        return state
