import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./audit_analytics.db")
    
    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # AI/LLM Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GROK_API_KEY: Optional[str] = os.getenv("GROK_API_KEY")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    LLM_CACHE_ENABLED: bool = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"
    
    # Streaming/Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_CLIENT_ID: str = os.getenv("KAFKA_CLIENT_ID", "audit-analytics-platform")
    KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID", "audit-analytics-group")
    KAFKA_AUTO_OFFSET_RESET: str = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")
    KAFKA_ENABLE_AUTO_COMMIT: bool = os.getenv("KAFKA_ENABLE_AUTO_COMMIT", "false").lower() == "true"
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "3600"))
    
    # Agent Configuration
    AGENT_PIPELINE: str = os.getenv("AGENT_PIPELINE", "default_pipeline")
    AGENT_CONFIDENCE_THRESHOLD: float = float(os.getenv("AGENT_CONFIDENCE_THRESHOLD", "0.7"))
    RISK_SCORE_THRESHOLD_HIGH: int = int(os.getenv("RISK_SCORE_THRESHOLD_HIGH", "70"))
    RISK_SCORE_THRESHOLD_MEDIUM: int = int(os.getenv("RISK_SCORE_THRESHOLD_MEDIUM", "40"))
    RISK_SCORE_THRESHOLD_LOW: int = int(os.getenv("RISK_SCORE_THRESHOLD_LOW", "20"))
    
    # Audit Analysis Configuration
    APPROVAL_THRESHOLD_DEFAULT: float = float(os.getenv("APPROVAL_THRESHOLD_DEFAULT", "10000"))
    DORMANT_VENDOR_DAYS: int = int(os.getenv("DORMANT_VENDOR_DAYS", "90"))
    RAPID_REPEAT_WINDOW_HOURS: int = int(os.getenv("RAPID_REPEAT_WINDOW_HOURS", "24"))
    NEAR_DUPLICATE_DATE_WINDOW_DAYS: int = int(os.getenv("NEAR_DUPLICATE_DATE_WINDOW_DAYS", "7"))
    ENABLE_IMMEDIATE_ANALYSIS: bool = os.getenv("ENABLE_IMMEDIATE_ANALYSIS", "true").lower() == "true"
    ENABLE_LLM_EXPLANATIONS: bool = os.getenv("ENABLE_LLM_EXPLANATIONS", "true").lower() == "true"
    FLAG_THRESHOLD_MEDIUM: int = int(os.getenv("FLAG_THRESHOLD_MEDIUM", "40"))
    FLAG_THRESHOLD_HIGH: int = int(os.getenv("FLAG_THRESHOLD_HIGH", "70"))
    BATCH_ANALYSIS_LIMIT: int = int(os.getenv("BATCH_ANALYSIS_LIMIT", "1000"))
    
    # File Upload Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "104857600"))
    
    # Application Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.lower() == "testing"
    
    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY)
    
    @property
    def has_grok(self) -> bool:
        return bool(self.GROK_API_KEY)
    
    @property
    def has_any_llm(self) -> bool:
        return self.has_gemini or self.has_grok

settings = Settings()