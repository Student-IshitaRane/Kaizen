import pandas as pd
import os
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging
from core.constants import DatasetType
from models.vendor import Vendor
from models.purchase_ledger import PurchaseLedger
from models.sales_ledger import SalesLedger
from models.general_ledger import GeneralLedger
from models.bank_transaction import BankTransaction
from services.agent_orchestrator import AgentOrchestrator
from services.analysis_result_service import AnalysisResultService
from core.config import settings

logger = logging.getLogger(__name__)

class DatasetIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.agent_orchestrator = AgentOrchestrator(db)
        self.analysis_result_service = AnalysisResultService(db)
    
    def ingest_dataset(self, file_path: str, dataset_type: DatasetType) -> Tuple[int, int, List[str]]:
        """Ingest dataset from file and insert into appropriate table"""
        
        try:
            # Read file based on extension
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            # Process based on dataset type
            if dataset_type == DatasetType.VENDOR_MASTER:
                return self._ingest_vendor_master(df)
            elif dataset_type == DatasetType.PURCHASE_LEDGER:
                return self._ingest_purchase_ledger(df)
            elif dataset_type == DatasetType.SALES_LEDGER:
                return self._ingest_sales_ledger(df)
            elif dataset_type == DatasetType.GENERAL_LEDGER:
                return self._ingest_general_ledger(df)
            elif dataset_type == DatasetType.BANK_TRANSACTIONS:
                return self._ingest_bank_transactions(df)
            else:
                raise ValueError(f"Unknown dataset type: {dataset_type}")
                
        except Exception as e:
            raise Exception(f"Failed to ingest dataset: {str(e)}")
    
    def _ingest_vendor_master(self, df: pd.DataFrame) -> Tuple[int, int, List[str]]:
        """Ingest vendor master data"""
        inserted = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                vendor = Vendor(
                    id=uuid.uuid4(),
                    vendor_code=str(row.get('vendor_code', '')).strip(),
                    vendor_name=str(row.get('vendor_name', '')).strip(),
                    gst_number=str(row.get('gst_number', '')).strip() if pd.notna(row.get('gst_number')) else None,
                    bank_account=str(row.get('bank_account', '')).strip() if pd.notna(row.get('bank_account')) else None,
                    contact_person=str(row.get('contact_person', '')).strip() if pd.notna(row.get('contact_person')) else None,
                    email=str(row.get('email', '')).strip() if pd.notna(row.get('email')) else None,
                    phone=str(row.get('phone', '')).strip() if pd.notna(row.get('phone')) else None,
                    address=str(row.get('address', '')).strip() if pd.notna(row.get('address')) else None,
                    city=str(row.get('city', '')).strip() if pd.notna(row.get('city')) else None,
                    country=str(row.get('country', '')).strip() if pd.notna(row.get('country')) else None,
                    tax_id=str(row.get('tax_id', '')).strip() if pd.notna(row.get('tax_id')) else None,
                    payment_terms=str(row.get('payment_terms', '')).strip() if pd.notna(row.get('payment_terms')) else None
                )
                
                self.db.add(vendor)
                inserted += 1
                
            except Exception as e:
                errors.append(f"Row {_}: {str(e)}")
        
        self.db.commit()
        return inserted, len(df) - inserted, errors
    
    def _ingest_purchase_ledger(self, df: pd.DataFrame) -> Tuple[int, int, List[str]]:
        """Ingest purchase ledger data"""
        inserted = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # Parse date fields
                invoice_date = self._parse_date(row.get('invoice_date'))
                posting_date = self._parse_date(row.get('posting_date')) if pd.notna(row.get('posting_date')) else None
                approval_date = self._parse_date(row.get('approval_date')) if pd.notna(row.get('approval_date')) else None
                
                purchase = PurchaseLedger(
                    id=uuid.uuid4(),
                    invoice_id=str(row.get('invoice_id', '')).strip(),
                    vendor_id=uuid.UUID(str(row.get('vendor_id', ''))),
                    amount=float(row.get('amount', 0)),
                    invoice_date=invoice_date,
                    department=str(row.get('department', '')).strip() if pd.notna(row.get('department')) else None,
                    approver_id=uuid.UUID(str(row.get('approver_id', ''))) if pd.notna(row.get('approver_id')) else None,
                    description=str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                    currency=str(row.get('currency', 'USD')).strip(),
                    posting_date=posting_date,
                    cost_center=str(row.get('cost_center', '')).strip() if pd.notna(row.get('cost_center')) else None,
                    gl_account=str(row.get('gl_account', '')).strip() if pd.notna(row.get('gl_account')) else None,
                    approval_date=approval_date,
                    reference_number=str(row.get('reference_number', '')).strip() if pd.notna(row.get('reference_number')) else None,
                    po_number=str(row.get('po_number', '')).strip() if pd.notna(row.get('po_number')) else None,
                    payment_method=str(row.get('payment_method', '')).strip() if pd.notna(row.get('payment_method')) else None,
                    bank_account=str(row.get('bank_account', '')).strip() if pd.notna(row.get('bank_account')) else None
                )
                
                self.db.add(purchase)
                inserted += 1
                
            except Exception as e:
                errors.append(f"Row {_}: {str(e)}")
        
        self.db.commit()
        return inserted, len(df) - inserted, errors
    
    def _ingest_sales_ledger(self, df: pd.DataFrame) -> Tuple[int, int, List[str]]:
        """Ingest sales ledger data"""
        inserted = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                transaction_date = self._parse_date(row.get('transaction_date'))
                
                sales = SalesLedger(
                    id=uuid.uuid4(),
                    transaction_id=str(row.get('transaction_id', '')).strip(),
                    customer_name=str(row.get('customer_name', '')).strip(),
                    amount=float(row.get('amount', 0)),
                    transaction_date=transaction_date,
                    department=str(row.get('department', '')).strip() if pd.notna(row.get('department')) else None,
                    description=str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                    currency=str(row.get('currency', 'USD')).strip(),
                    invoice_number=str(row.get('invoice_number', '')).strip() if pd.notna(row.get('invoice_number')) else None,
                    payment_terms=str(row.get('payment_terms', '')).strip() if pd.notna(row.get('payment_terms')) else None,
                    sales_person=str(row.get('sales_person', '')).strip() if pd.notna(row.get('sales_person')) else None,
                    product_category=str(row.get('product_category', '')).strip() if pd.notna(row.get('product_category')) else None,
                    quantity=float(row.get('quantity', 0)) if pd.notna(row.get('quantity')) else None,
                    unit_price=float(row.get('unit_price', 0)) if pd.notna(row.get('unit_price')) else None,
                    tax_amount=float(row.get('tax_amount', 0)) if pd.notna(row.get('tax_amount')) else None,
                    total_amount=float(row.get('total_amount', 0)) if pd.notna(row.get('total_amount')) else None
                )
                
                self.db.add(sales)
                inserted += 1
                
            except Exception as e:
                errors.append(f"Row {_}: {str(e)}")
        
        self.db.commit()
        return inserted, len(df) - inserted, errors
    
    def _ingest_general_ledger(self, df: pd.DataFrame) -> Tuple[int, int, List[str]]:
        """Ingest general ledger data"""
        inserted = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                entry_date = self._parse_date(row.get('entry_date'))
                posting_date = self._parse_date(row.get('posting_date')) if pd.notna(row.get('posting_date')) else None
                
                gl_entry = GeneralLedger(
                    id=uuid.uuid4(),
                    entry_id=str(row.get('entry_id', '')).strip(),
                    account_name=str(row.get('account_name', '')).strip(),
                    debit_amount=float(row.get('debit_amount', 0)),
                    credit_amount=float(row.get('credit_amount', 0)),
                    entry_date=entry_date,
                    description=str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                    gl_account=str(row.get('gl_account', '')).strip() if pd.notna(row.get('gl_account')) else None,
                    posting_date=posting_date,
                    fiscal_year=int(row.get('fiscal_year', 0)) if pd.notna(row.get('fiscal_year')) else None,
                    fiscal_period=int(row.get('fiscal_period', 0)) if pd.notna(row.get('fiscal_period')) else None,
                    document_number=str(row.get('document_number', '')).strip() if pd.notna(row.get('document_number')) else None,
                    document_type=str(row.get('document_type', '')).strip() if pd.notna(row.get('document_type')) else None,
                    cost_center=str(row.get('cost_center', '')).strip() if pd.notna(row.get('cost_center')) else None,
                    profit_center=str(row.get('profit_center', '')).strip() if pd.notna(row.get('profit_center')) else None,
                    currency=str(row.get('currency', 'USD')).strip(),
                    transaction_type=str(row.get('transaction_type', '')).strip() if pd.notna(row.get('transaction_type')) else None
                )
                
                self.db.add(gl_entry)
                inserted += 1
                
            except Exception as e:
                errors.append(f"Row {_}: {str(e)}")
        
        self.db.commit()
        return inserted, len(df) - inserted, errors
    
    def _ingest_bank_transactions(self, df: pd.DataFrame) -> Tuple[int, int, List[str]]:
        """Ingest bank transactions data"""
        inserted = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                transaction_date = self._parse_date(row.get('transaction_date'))
                value_date = self._parse_date(row.get('value_date')) if pd.notna(row.get('value_date')) else None
                
                vendor_id = None
                if pd.notna(row.get('vendor_id')):
                    vendor_id = uuid.UUID(str(row.get('vendor_id')))
                
                bank_txn = BankTransaction(
                    id=uuid.uuid4(),
                    transaction_id=str(row.get('transaction_id', '')).strip(),
                    account_number=str(row.get('account_number', '')).strip(),
                    vendor_id=vendor_id,
                    amount=float(row.get('amount', 0)),
                    transaction_date=transaction_date,
                    transaction_type=str(row.get('transaction_type', '')).strip(),
                    reference=str(row.get('reference', '')).strip() if pd.notna(row.get('reference')) else None,
                    value_date=value_date,
                    currency=str(row.get('currency', 'USD')).strip(),
                    description=str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                    counterparty_name=str(row.get('counterparty_name', '')).strip() if pd.notna(row.get('counterparty_name')) else None,
                    counterparty_account=str(row.get('counterparty_account', '')).strip() if pd.notna(row.get('counterparty_account')) else None,
                    balance_after=float(row.get('balance_after', 0)) if pd.notna(row.get('balance_after')) else None,
                    bank_name=str(row.get('bank_name', '')).strip() if pd.notna(row.get('bank_name')) else None,
                    branch_code=str(row.get('branch_code', '')).strip() if pd.notna(row.get('branch_code')) else None,
                    payment_method=str(row.get('payment_method', '')).strip() if pd.notna(row.get('payment_method')) else None
                )
                
                self.db.add(bank_txn)
                inserted += 1
                
            except Exception as e:
                errors.append(f"Row {_}: {str(e)}")
        
        self.db.commit()
        return inserted, len(df) - inserted, errors
    
    def _parse_date(self, date_value) -> datetime.date:
        """Parse date from various formats"""
        if pd.isna(date_value):
            raise ValueError("Date value is required")
        
        if isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, str):
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Could not parse date: {date_value}")
        else:
            raise ValueError(f"Unsupported date type: {type(date_value)}")
    
    def preprocess_historical_data(self, dataset_type: DatasetType, 
                                  file_path: str,
                                  enable_analysis: bool = False) -> Dict[str, Any]:
        """
        Preprocess historical dataset for future analysis
        
        Args:
            dataset_type: Type of dataset
            file_path: Path to dataset file
            enable_analysis: Whether to run analysis on historical data
            
        Returns:
            Preprocessing results
        """
        try:
            # Read dataset
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            logger.info(f"Preprocessing {dataset_type.value} dataset with {len(df)} rows")
            
            # Basic preprocessing
            preprocessed_data = self._basic_preprocessing(df, dataset_type)
            
            # Run analysis if enabled
            analysis_results = None
            if enable_analysis and dataset_type == DatasetType.PURCHASE_LEDGER:
                analysis_results = self._analyze_historical_purchases(df)
            
            # Prepare response
            response = {
                "dataset_type": dataset_type.value,
                "rows_processed": len(df),
                "preprocessing_summary": preprocessed_data,
                "analysis_enabled": enable_analysis,
                "analysis_results": analysis_results,
                "metadata": {
                    "preprocessing_timestamp": datetime.utcnow().isoformat(),
                    "file_path": file_path,
                    "columns": list(df.columns)
                }
            }
            
            logger.info(f"Preprocessing completed for {dataset_type.value}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to preprocess historical data: {str(e)}")
            raise Exception(f"Preprocessing failed: {str(e)}")
    
    def _basic_preprocessing(self, df: pd.DataFrame, dataset_type: DatasetType) -> Dict[str, Any]:
        """Perform basic data preprocessing"""
        preprocessing_summary = {
            "original_rows": len(df),
            "original_columns": len(df.columns),
            "missing_values": {},
            "data_types": {},
            "cleaning_actions": []
        }
        
        # Check for missing values
        missing_counts = df.isnull().sum()
        preprocessing_summary["missing_values"] = missing_counts[missing_counts > 0].to_dict()
        
        # Record data types
        preprocessing_summary["data_types"] = df.dtypes.astype(str).to_dict()
        
        # Basic cleaning actions
        if dataset_type == DatasetType.PURCHASE_LEDGER:
            # Ensure required columns exist
            required_cols = ["invoice_id", "vendor_id", "amount", "invoice_date"]
            missing_required = [col for col in required_cols if col not in df.columns]
            
            if missing_required:
                preprocessing_summary["cleaning_actions"].append(
                    f"Missing required columns: {missing_required}"
                )
            
            # Clean amount column
            if "amount" in df.columns:
                # Convert to numeric, handle errors
                df["amount"] = pd.to_numeric(df["amount"], errors='coerce')
                invalid_amounts = df["amount"].isnull().sum()
                if invalid_amounts > 0:
                    preprocessing_summary["cleaning_actions"].append(
                        f"Fixed {invalid_amounts} invalid amount values"
                    )
            
            # Clean date columns
            date_columns = ["invoice_date", "posting_date", "approval_date"]
            for date_col in date_columns:
                if date_col in df.columns:
                    try:
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                        invalid_dates = df[date_col].isnull().sum()
                        if invalid_dates > 0:
                            preprocessing_summary["cleaning_actions"].append(
                                f"Fixed {invalid_dates} invalid {date_col} values"
                            )
                    except Exception:
                        preprocessing_summary["cleaning_actions"].append(
                            f"Failed to parse {date_col} column"
                        )
        
        elif dataset_type == DatasetType.VENDOR_MASTER:
            # Clean vendor data
            if "vendor_code" in df.columns:
                df["vendor_code"] = df["vendor_code"].astype(str).str.strip().str.upper()
                preprocessing_summary["cleaning_actions"].append(
                    "Standardized vendor codes"
                )
        
        preprocessing_summary["cleaned_rows"] = len(df.dropna(subset=["invoice_id", "vendor_id"] if "invoice_id" in df.columns else []))
        
        return preprocessing_summary
    
    def _analyze_historical_purchases(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze historical purchase data for patterns"""
        try:
            if len(df) > settings.BATCH_ANALYSIS_LIMIT:
                logger.warning(f"Dataset too large for analysis ({len(df)} rows), sampling first {settings.BATCH_ANALYSIS_LIMIT} rows")
                df = df.head(settings.BATCH_ANALYSIS_LIMIT)
            
            analysis_results = {
                "transactions_analyzed": 0,
                "flagged_cases_created": 0,
                "risk_distribution": {},
                "processing_summary": []
            }
            
            # Sample transactions for analysis
            sample_size = min(100, len(df))
            sample_df = df.sample(n=sample_size, random_state=42)
            
            for idx, row in sample_df.iterrows():
                try:
                    # Convert row to transaction data
                    transaction_data = self._row_to_transaction_data(row)
                    
                    # Run analysis pipeline
                    pipeline_results = self.agent_orchestrator.execute_pipeline(
                        transaction_data=transaction_data,
                        pipeline_name="fast_pipeline",  # Use fast pipeline for historical data
                        immediate_analysis=True
                    )
                    
                    if pipeline_results.get("status") != "skipped":
                        analysis_results["transactions_analyzed"] += 1
                        
                        # Create flagged case if needed
                        analysis_results_data = pipeline_results.get("analysis_results", {})
                        
                        flagged_case = self.analysis_result_service.create_flagged_case_from_analysis(
                            transaction_data=transaction_data,
                            analysis_results=analysis_results_data,
                            pipeline_results=pipeline_results
                        )
                        
                        if flagged_case:
                            analysis_results["flagged_cases_created"] += 1
                        
                        # Track risk distribution
                        risk_level = analysis_results_data.get("risk_scoring", {}).get("risk_level", "unknown")
                        analysis_results["risk_distribution"][risk_level] = analysis_results["risk_distribution"].get(risk_level, 0) + 1
                
                except Exception as e:
                    logger.warning(f"Failed to analyze row {idx}: {e}")
                    continue
            
            # Add processing summary
            analysis_results["processing_summary"] = [
                f"Analyzed {analysis_results['transactions_analyzed']} sample transactions",
                f"Created {analysis_results['flagged_cases_created']} flagged cases",
                f"Risk distribution: {analysis_results['risk_distribution']}"
            ]
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Failed to analyze historical purchases: {e}")
            return None
    
    def _row_to_transaction_data(self, row) -> Dict[str, Any]:
        """Convert DataFrame row to transaction data format"""
        transaction_data = {}
        
        # Map common fields
        field_mapping = {
            "invoice_id": ["invoice_id", "invoice_number", "inv_id"],
            "vendor_id": ["vendor_id", "vendor_code", "supplier_id"],
            "amount": ["amount", "total", "invoice_amount"],
            "invoice_date": ["invoice_date", "date", "invoice_dt"],
            "department": ["department", "dept", "cost_center"],
            "description": ["description", "notes", "remarks"],
            "currency": ["currency", "curr"],
            "approver_id": ["approver_id", "approver", "approved_by"],
            "posting_date": ["posting_date", "posting_dt"],
            "cost_center": ["cost_center", "cc"],
            "gl_account": ["gl_account", "account"],
            "reference_number": ["reference_number", "ref", "reference"],
            "po_number": ["po_number", "po", "purchase_order"]
        }
        
        for standard_field, possible_names in field_mapping.items():
            for name in possible_names:
                if name in row and pd.notna(row[name]):
                    transaction_data[standard_field] = row[name]
                    break
        
        # Convert dates to string format
        date_fields = ["invoice_date", "posting_date", "approval_date"]
        for field in date_fields:
            if field in transaction_data and isinstance(transaction_data[field], (pd.Timestamp, datetime)):
                transaction_data[field] = transaction_data[field].isoformat()
        
        return transaction_data
    
    def get_dataset_statistics(self, dataset_type: DatasetType) -> Dict[str, Any]:
        """Get statistics for a dataset type"""
        try:
            if dataset_type == DatasetType.PURCHASE_LEDGER:
                model = PurchaseLedger
            elif dataset_type == DatasetType.VENDOR_MASTER:
                model = Vendor
            elif dataset_type == DatasetType.SALES_LEDGER:
                model = SalesLedger
            elif dataset_type == DatasetType.GENERAL_LEDGER:
                model = GeneralLedger
            elif dataset_type == DatasetType.BANK_TRANSACTIONS:
                model = BankTransaction
            else:
                return {"error": f"Unknown dataset type: {dataset_type}"}
            
            # Get basic statistics
            total_count = self.db.query(model).count()
            
            # Get date range for time-based datasets
            date_range = {}
            if hasattr(model, 'created_at'):
                oldest = self.db.query(model.created_at).order_by(model.created_at.asc()).first()
                newest = self.db.query(model.created_at).order_by(model.created_at.desc()).first()
                
                if oldest and newest:
                    date_range = {
                        "oldest": oldest[0].isoformat() if oldest[0] else None,
                        "newest": newest[0].isoformat() if newest[0] else None
                    }
            
            # Get amount statistics for financial datasets
            amount_stats = {}
            if hasattr(model, 'amount'):
                from sqlalchemy import func
                
                result = self.db.query(
                    func.count(model.amount),
                    func.sum(model.amount),
                    func.avg(model.amount),
                    func.min(model.amount),
                    func.max(model.amount)
                ).first()
                
                if result:
                    amount_stats = {
                        "count": result[0] or 0,
                        "total": float(result[1] or 0),
                        "average": float(result[2] or 0),
                        "min": float(result[3] or 0),
                        "max": float(result[4] or 0)
                    }
            
            return {
                "dataset_type": dataset_type.value,
                "total_records": total_count,
                "date_range": date_range,
                "amount_statistics": amount_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get dataset statistics: {e}")
            return {
                "dataset_type": dataset_type.value,
                "error": str(e)
            }