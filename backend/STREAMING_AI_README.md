# Streaming and AI Scaffolding Layer

This directory contains the streaming and AI scaffolding implementation for the Audit Analytics Platform.

## Architecture Overview

### 1. Streaming Layer (`backend/streaming/`)
- **Kafka Configuration**: Topic definitions and producer/consumer configurations
- **Kafka Producer**: Publishes transaction events for real-time analysis
- **Kafka Consumer**: Consumes events and routes to appropriate handlers
- **Event Handlers**: Process different types of events (transactions, analysis, cases)

### 2. LLM Service Layer (`backend/llm_service/`)
- **LLM Interface**: Abstract base classes for provider-agnostic LLM access
- **Gemini Provider**: Google Gemini integration (primary provider)
- **Grok Provider**: xAI Grok integration (fallback provider)
- **LLM Service**: Manages provider selection, fallback, and request routing

### 3. Agent Layer (`backend/agents/`)
- **Base Agent**: Abstract base class for all agents
- **Data Preparation Agent**: Cleans and prepares transaction data
- **Anomaly Detection Agent**: Detects anomalies and unusual patterns
- **Pattern Analysis Agent**: Analyzes transaction patterns and trends
- **Rule Validation Agent**: Validates against business rules and compliance
- **Risk Scoring Agent**: Calculates comprehensive risk scores
- **Explanation Generation Agent**: Generates human-readable explanations
- **Agent Orchestrator**: Manages agent pipelines and execution flow

## Integration Points

### Transaction Service Integration
The `TransactionService` in `backend/services/transaction_service.py` has been updated to:
1. Publish transaction events to Kafka after creation
2. Include transaction metadata for AI analysis
3. Log publishing status for monitoring

### Main Application Integration
The main application (`backend/main.py`) now:
1. Initializes streaming services on startup
2. Initializes AI services (LLM providers and agents)
3. Provides system info endpoint with AI/streaming status
4. Properly shuts down streaming connections on shutdown

## Configuration

### Environment Variables
```bash
# Gemini AI (Primary Provider)
GEMINI_API_KEY=your_gemini_api_key_here

# Grok AI (Fallback Provider)  
GROK_API_KEY=your_grok_api_key_here

# Kafka Configuration (if different from defaults)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### Kafka Topics
8 topics are configured for different event types:
1. `transactions.incoming` - New transaction events
2. `transactions.validated` - Validated transaction events
3. `analysis.requests` - Analysis request events
4. `analysis.results` - Analysis result events
5. `cases.flagged` - Flagged case events
6. `cases.reviewed` - Reviewed case events
7. `notifications.alerts` - Notification events
8. `audit.events` - Audit trail events

## Testing

Run the streaming and AI test:
```bash
cd backend
python test_streaming_ai.py
```

## Agent Pipelines

Three pre-configured pipelines are available:

### 1. Default Pipeline (6 agents)
```
data_preparation → anomaly_detection → pattern_analysis → rule_validation → risk_scoring → explanation_generation
```

### 2. Fast Pipeline (3 agents)
```
data_preparation → anomaly_detection → risk_scoring
```

### 3. Compliance Pipeline (4 agents)
```
data_preparation → rule_validation → risk_scoring → explanation_generation
```

## Usage Examples

### Publishing a Transaction Event
```python
from streaming.kafka_producer import producer

transaction_data = {
    "transaction_id": "tx_123",
    "amount": 15000.00,
    "vendor_id": "vendor_456"
}

producer.publish_transaction_created(transaction_data)
```

### Using the LLM Service
```python
from llm_service import llm_service, LLMRequest

request = LLMRequest(
    prompt="Analyze this transaction for fraud risk",
    context={"transaction": transaction_data},
    agent_name="fraud_detection"
)

response = llm_service.generate(request)
print(response.content)
```

### Executing an Agent Pipeline
```python
from agents.agent_orchestrator import agent_orchestrator

results = agent_orchestrator.execute_pipeline(
    transaction_data=transaction_data,
    context=additional_context,
    pipeline_name="default_pipeline"
)
```

## Next Steps

1. **Implement actual Kafka connectivity** - Currently using placeholder implementations
2. **Add actual LLM API calls** - Currently using placeholder responses
3. **Implement agent business logic** - Currently using placeholder analysis
4. **Add monitoring and metrics** - Track agent performance and accuracy
5. **Implement caching** - Cache LLM responses and analysis results
6. **Add retry logic** - Handle transient failures in AI services
7. **Implement batch processing** - Process transactions in batches for efficiency

## Notes

- The system is designed to be provider-agnostic for LLM services
- Kafka integration allows for real-time processing and event-driven architecture
- Agent pipeline design enables flexible analysis workflows
- All components are modular and can be extended or replaced independently