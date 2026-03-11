import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.session import get_db
from streaming.kafka_consumer import consumer_manager
from streaming.event_handlers import TransactionEventHandler
from services.agent_orchestrator import AgentOrchestrator
from services.analysis_result_service import AnalysisResultService
from core.config import settings

logger = logging.getLogger(__name__)


class AnalysisConsumer:
    """Kafka consumer for transaction analysis events"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.agent_orchestrator = None
        self.analysis_result_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize analysis services"""
        try:
            if not self.db:
                from app.database.session import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            self.agent_orchestrator = AgentOrchestrator(self.db)
            self.analysis_result_service = AnalysisResultService(self.db)
            
            logger.info("Analysis services initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize analysis services: {e}")
            raise
    
    def consume_transaction_events(self):
        """Consume transaction events from Kafka"""
        logger.info("Starting transaction analysis consumer...")
        
        try:
            # Subscribe to transaction topics
            topics = ["transactions.created", "transactions.updated"]
            consumer.subscribe(topics)
            
            logger.info(f"Subscribed to topics: {topics}")
            
            # Start consuming messages
            while True:
                try:
                    msg = consumer.poll(timeout=1.0)
                    
                    if msg is None:
                        continue
                    
                    if msg.error():
                        logger.error(f"Consumer error: {msg.error()}")
                        continue
                    
                    # Process message
                    self._process_message(msg)
                    
                    # Commit offset
                    consumer.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Continue processing other messages
        
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        except Exception as e:
            logger.error(f"Consumer failed: {e}")
        finally:
            consumer.close()
    
    def _process_message(self, msg):
        """Process a single Kafka message"""
        try:
            # Parse message
            message_data = json.loads(msg.value().decode('utf-8'))
            topic = msg.topic()
            offset = msg.offset()
            partition = msg.partition()
            
            logger.info(f"Received message from topic {topic}, partition {partition}, offset {offset}")
            
            # Route to appropriate handler
            if topic == "transactions.created":
                self._handle_transaction_created(message_data)
            elif topic == "transactions.updated":
                self._handle_transaction_updated(message_data)
            else:
                logger.warning(f"Unhandled topic: {topic}")
            
            logger.info(f"Successfully processed message from {topic}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {e}")
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
    
    def _handle_transaction_created(self, message_data: Dict[str, Any]):
        """Handle transaction created event"""
        try:
            # Extract transaction data
            transaction_data = message_data.get("data", {})
            metadata = message_data.get("metadata", {})
            
            logger.info(f"Processing transaction created event: {transaction_data.get('invoice_id')}")
            
            # Run analysis pipeline
            pipeline_results = self.agent_orchestrator.execute_pipeline(
                transaction_data=transaction_data,
                pipeline_name="default_pipeline",
                immediate_analysis=settings.ENABLE_IMMEDIATE_ANALYSIS
            )
            
            # Check if analysis was performed
            if pipeline_results.get("status") == "skipped":
                logger.info(f"Analysis skipped for transaction {transaction_data.get('invoice_id')}")
                return
            
            # Create flagged case if needed
            analysis_results = pipeline_results.get("analysis_results", {})
            
            flagged_case = self.analysis_result_service.create_flagged_case_from_analysis(
                transaction_data=transaction_data,
                analysis_results=analysis_results,
                pipeline_results=pipeline_results
            )
            
            # Log results
            if flagged_case:
                logger.info(f"Created flagged case {flagged_case.id} for transaction {transaction_data.get('invoice_id')}")
            else:
                logger.info(f"No flagged case needed for transaction {transaction_data.get('invoice_id')}")
            
            # Publish analysis completed event
            self._publish_analysis_completed(
                transaction_data=transaction_data,
                pipeline_results=pipeline_results,
                flagged_case=flagged_case
            )
            
        except Exception as e:
            logger.error(f"Failed to handle transaction created event: {e}")
    
    def _handle_transaction_updated(self, message_data: Dict[str, Any]):
        """Handle transaction updated event"""
        try:
            # Extract transaction data
            transaction_data = message_data.get("data", {})
            metadata = message_data.get("metadata", {})
            
            logger.info(f"Processing transaction updated event: {transaction_data.get('invoice_id')}")
            
            # For now, just log the update
            # TODO: Implement re-analysis logic if needed
            logger.info(f"Transaction updated: {transaction_data.get('invoice_id')}")
            
        except Exception as e:
            logger.error(f"Failed to handle transaction updated event: {e}")
    
    def _publish_analysis_completed(self, 
                                   transaction_data: Dict[str, Any],
                                   pipeline_results: Dict[str, Any],
                                   flagged_case: Optional[Any] = None):
        """Publish analysis completed event"""
        try:
            from streaming.kafka_producer import producer
            
            event_data = {
                "transaction_id": transaction_data.get("invoice_id"),
                "vendor_id": transaction_data.get("vendor_id"),
                "analysis_status": pipeline_results.get("overall_status"),
                "processing_time_ms": pipeline_results.get("processing_time_ms", 0),
                "risk_score": pipeline_results.get("analysis_summary", {}).get("risk_score", 0),
                "risk_level": pipeline_results.get("analysis_summary", {}).get("risk_level", "unknown"),
                "flagged_case_created": flagged_case is not None,
                "flagged_case_id": flagged_case.id if flagged_case else None,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "pipeline_id": pipeline_results.get("pipeline_id"),
                    "pipeline_name": pipeline_results.get("pipeline_name")
                }
            }
            
            producer.publish_analysis_completed(event_data)
            logger.info(f"Published analysis completed event for {transaction_data.get('invoice_id')}")
            
        except Exception as e:
            logger.error(f"Failed to publish analysis completed event: {e}")
    
    def process_single_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single transaction (for testing or manual triggering)
        
        Args:
            transaction_data: Transaction data to analyze
            
        Returns:
            Analysis results
        """
        try:
            if not self.db:
                from app.database.session import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            # Run analysis pipeline
            pipeline_results = self.agent_orchestrator.execute_pipeline(
                transaction_data=transaction_data,
                pipeline_name="default_pipeline",
                immediate_analysis=True  # Force analysis
            )
            
            # Create flagged case if needed
            analysis_results = pipeline_results.get("analysis_results", {})
            
            flagged_case = self.analysis_result_service.create_flagged_case_from_analysis(
                transaction_data=transaction_data,
                analysis_results=analysis_results,
                pipeline_results=pipeline_results
            )
            
            # Prepare response
            response = {
                "transaction_id": transaction_data.get("invoice_id"),
                "pipeline_status": pipeline_results.get("overall_status"),
                "processing_time_ms": pipeline_results.get("processing_time_ms", 0),
                "risk_score": analysis_results.get("risk_scoring", {}).get("overall_risk_score", 0),
                "risk_level": analysis_results.get("risk_scoring", {}).get("risk_level", "unknown"),
                "flagged_case_created": flagged_case is not None,
                "flagged_case_id": flagged_case.id if flagged_case else None,
                "analysis_summary": pipeline_results.get("analysis_summary", {}),
                "pipeline_id": pipeline_results.get("pipeline_id")
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process single transaction: {e}")
            return {
                "error": str(e),
                "transaction_id": transaction_data.get("invoice_id", "unknown"),
                "status": "failed"
            }


# Singleton instance
analysis_consumer = None

def get_analysis_consumer(db_session: Optional[Session] = None) -> AnalysisConsumer:
    """Get or create analysis consumer instance"""
    global analysis_consumer
    
    if analysis_consumer is None:
        analysis_consumer = AnalysisConsumer(db_session)
    
    return analysis_consumer


def start_analysis_consumer():
    """Start the analysis consumer (to be called from main application)"""
    try:
        consumer_instance = get_analysis_consumer()
        consumer_instance.consume_transaction_events()
    except Exception as e:
        logger.error(f"Failed to start analysis consumer: {e}")


def process_transaction_immediately(transaction_data: Dict[str, Any], 
                                   db_session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Process a transaction immediately (for API calls or testing)
    
    Args:
        transaction_data: Transaction data to analyze
        db_session: Optional database session
        
    Returns:
        Analysis results
    """
    try:
        consumer_instance = get_analysis_consumer(db_session)
        return consumer_instance.process_single_transaction(transaction_data)
    except Exception as e:
        logger.error(f"Failed to process transaction immediately: {e}")
        return {
            "error": str(e),
            "transaction_id": transaction_data.get("invoice_id", "unknown"),
            "status": "failed"
        }
# Temporary fix for missing consumer - create a dummy consumer
# This allows the application to start even if Kafka is not configured
class DummyConsumer:
    def subscribe(self, topics):
        pass
    
    def poll(self, timeout=1.0):
        return None
    
    def commit(self, message=None):
        pass
    
    def close(self):
        pass

# Create dummy consumer
consumer = DummyConsumer()