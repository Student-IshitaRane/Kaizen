from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Kafka configuration from environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_CLIENT_ID = os.getenv("KAFKA_CLIENT_ID", "audit-analytics-platform")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "audit-analytics-group")
KAFKA_AUTO_OFFSET_RESET = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")
KAFKA_ENABLE_AUTO_COMMIT = os.getenv("KAFKA_ENABLE_AUTO_COMMIT", "false").lower() == "true"

KAFKA_CONFIG = {
    "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
    "client_id": KAFKA_CLIENT_ID,
}

PRODUCER_CONFIG = {
    **KAFKA_CONFIG,
    "acks": "all",
    "retries": 3,
    "compression_type": "snappy",
    "max_in_flight_requests_per_connection": 5,
    "enable_idempotence": True,
}

CONSUMER_CONFIG = {
    **KAFKA_CONFIG,
    "auto_offset_reset": KAFKA_AUTO_OFFSET_RESET,
    "enable_auto_commit": KAFKA_ENABLE_AUTO_COMMIT,
    "max_poll_records": 100,
    "session_timeout_ms": 30000,
}

TOPICS = {
    "TRANSACTIONS_INCOMING": "transactions.incoming",
    "TRANSACTIONS_VALIDATED": "transactions.validated",
    "ANALYSIS_REQUESTS": "analysis.requests",
    "ANALYSIS_RESULTS": "analysis.results",
    "CASES_FLAGGED": "cases.flagged",
    "CASES_REVIEWED": "cases.reviewed",
    "NOTIFICATIONS_ALERTS": "notifications.alerts",
    "AUDIT_EVENTS": "audit.events",
}

TOPIC_CONFIGS: Dict[str, Dict[str, Any]] = {
    TOPICS["TRANSACTIONS_INCOMING"]: {
        "num_partitions": 3,
        "replication_factor": 1,
        "retention_ms": 604800000,  # 7 days
    },
    TOPICS["TRANSACTIONS_VALIDATED"]: {
        "num_partitions": 3,
        "replication_factor": 1,
        "retention_ms": 2592000000,  # 30 days
    },
    TOPICS["ANALYSIS_REQUESTS"]: {
        "num_partitions": 2,
        "replication_factor": 1,
        "retention_ms": 259200000,  # 3 days
    },
    TOPICS["ANALYSIS_RESULTS"]: {
        "num_partitions": 3,
        "replication_factor": 1,
        "retention_ms": 2592000000,  # 30 days
    },
    TOPICS["CASES_FLAGGED"]: {
        "num_partitions": 2,
        "replication_factor": 1,
        "retention_ms": 7776000000,  # 90 days
    },
    TOPICS["CASES_REVIEWED"]: {
        "num_partitions": 2,
        "replication_factor": 1,
        "retention_ms": 31536000000,  # 365 days
    },
    TOPICS["NOTIFICATIONS_ALERTS"]: {
        "num_partitions": 1,
        "replication_factor": 1,
        "retention_ms": 604800000,  # 7 days
    },
    TOPICS["AUDIT_EVENTS"]: {
        "num_partitions": 2,
        "replication_factor": 1,
        "retention_ms": 220752000000,  # 7 years
    },
}