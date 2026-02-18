"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "Disaster DSS API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/disaster_dss"
    DATABASE_URL_SYNC: str = "postgresql://user:password@localhost:5432/disaster_dss"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PREFIX: str = "disaster_dss"
    
    # AI Model Paths
    MODEL_PATH: str = "./models/weights"
    YOLO_MODEL_PATH: str = "./models/weights/yolov8-disaster.pt"
    BERT_MODEL_PATH: str = "./models/weights/bert-emergency"
    
    # External APIs
    SATELLITE_API_KEY: Optional[str] = None
    SOCIAL_MEDIA_API_KEY: Optional[str] = None
    
    # Risk Scoring
    RISK_THRESHOLD_LOW: float = 0.3
    RISK_THRESHOLD_MEDIUM: float = 0.5
    RISK_THRESHOLD_HIGH: float = 0.7
    RISK_THRESHOLD_CRITICAL: float = 0.9
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "./uploads"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
