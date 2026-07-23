"""Sensor Intelligence Agent for IoT Telemetry Anomaly Detection."""
import logging
from typing import Dict, Any, List
from app.graph.crisis_state import CrisisState

logger = logging.getLogger(__name__)


class SensorAgent:
    """Agent responsible for analyzing IoT sensor streams, threshold violations, and anomalies."""

    def __init__(self):
        self.name = "SENSOR_AGENT"
        # Threshold definitions
        self.THRESHOLDS = {
            "water_level": {"unit": "m", "warning": 3.0, "critical": 4.5},
            "seismic": {"unit": "magnitude", "warning": 4.5, "critical": 6.0},
            "temperature": {"unit": "C", "warning": 55.0, "critical": 80.0},
            "smoke_density": {"unit": "%", "warning": 40.0, "critical": 75.0},
            "gas_leak": {"unit": "ppm", "warning": 200.0, "critical": 500.0}
        }

    async def run(self, state: CrisisState) -> CrisisState:
        """Evaluate incoming IoT sensor readings."""
        state.record_step(
            agent=self.name,
            action="PROCESS_SENSOR_TELEMETRY",
            status="STARTED",
            summary=f"Analyzing {len(state.sensor_readings)} sensor data feeds"
        )

        anomalies = []
        critical_violations = []

        for sensor in state.sensor_readings:
            stype = sensor.get("sensor_type")
            val = sensor.get("value", 0.0)
            sid = sensor.get("sensor_id", "SENS_UNKNOWN")

            rules = self.THRESHOLDS.get(stype)
            if rules:
                if val >= rules["critical"]:
                    critical_violations.append({
                        "sensor_id": sid,
                        "sensor_type": stype,
                        "value": val,
                        "unit": rules["unit"],
                        "severity": "CRITICAL",
                        "anomaly_score": 0.95
                    })
                elif val >= rules["warning"]:
                    anomalies.append({
                        "sensor_id": sid,
                        "sensor_type": stype,
                        "value": val,
                        "unit": rules["unit"],
                        "severity": "WARNING",
                        "anomaly_score": 0.65
                    })

        state.sensor_intelligence = {
            "total_sensors_monitored": len(state.sensor_readings),
            "critical_violations": critical_violations,
            "warnings": anomalies,
            "anomaly_count": len(anomalies) + len(critical_violations),
            "status": "HEALTHY" if not critical_violations else "CRITICAL_ALERT"
        }

        if critical_violations:
            state.evidence.append({
                "source": "IOT_SENSOR_AGENT",
                "type": "SENSOR_CRITICAL_THRESHOLD",
                "detail": f"Sensor {critical_violations[0]['sensor_id']} ({critical_violations[0]['sensor_type']}) hit CRITICAL level {critical_violations[0]['value']}{critical_violations[0]['unit']}",
                "confidence": 0.99
            })

        state.record_step(
            agent=self.name,
            action="PROCESS_SENSOR_TELEMETRY",
            status="COMPLETED",
            summary=f"Sensor evaluation complete: {len(critical_violations)} critical violations, {len(anomalies)} warnings.",
            confidence=0.95
        )

        return state
