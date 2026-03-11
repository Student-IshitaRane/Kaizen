from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from decimal import Decimal
from database import get_db
from models.user import User
from schemas.purchase_ledger import PurchaseTransactionCreate, PurchaseTransactionResponse
from auth.security import get_current_user, require_role
from core.constants import UserRole
from services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("", response_model=PurchaseTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: PurchaseTransactionCreate,
    current_user: User = Depends(require_role(UserRole.FINANCE)),
    db: Session = Depends(get_db)
):
    """Create a new purchase transaction (Finance users only)"""
    
    try:
        transaction_service = TransactionService(db)
        
        transaction = transaction_service.create_purchase_transaction(
            invoice_id=transaction_data.invoice_id,
            vendor_id=transaction_data.vendor_id,
            amount=transaction_data.amount,
            invoice_date=transaction_data.invoice_date,
            created_by=str(current_user.id),
            department=transaction_data.department,
            approver_id=transaction_data.approver_id,
            description=transaction_data.description,
            currency=transaction_data.currency,
            posting_date=transaction_data.posting_date,
            cost_center=transaction_data.cost_center,
            gl_account=transaction_data.gl_account,
            approval_date=transaction_data.approval_date,
            reference_number=transaction_data.reference_number,
            po_number=transaction_data.po_number,
            payment_method=transaction_data.payment_method,
            bank_account=transaction_data.bank_account
        )
        
        return PurchaseTransactionResponse.from_orm(transaction)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transaction: {str(e)}"
        )

@router.get("", response_model=dict)
def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    vendor_id: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List transactions with filtering"""
    
    try:
        transaction_service = TransactionService(db)
        
        # For finance users, only show their transactions
        user_id = str(current_user.id) if current_user.role == UserRole.FINANCE else None
        
        result = transaction_service.get_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            vendor_id=vendor_id,
            min_amount=min_amount,
            max_amount=max_amount,
            department=department,
            page=page,
            limit=limit
        )
        
        return {
            "transactions": [
                PurchaseTransactionResponse.from_orm(t) for t in result["transactions"]
            ],
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transactions: {str(e)}"
        )

@router.get("/{transaction_id}", response_model=PurchaseTransactionResponse)
def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction by ID"""
    
    try:
        transaction_service = TransactionService(db)
        transaction = transaction_service.get_transaction_by_id(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Check permissions
        if current_user.role == UserRole.FINANCE:
            if transaction.approver_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        return PurchaseTransactionResponse.from_orm(transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transaction: {str(e)}"
        )

@router.get("/vendor/{vendor_id}/summary")
def get_vendor_transaction_summary(
    vendor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction summary for a vendor"""
    
    try:
        transaction_service = TransactionService(db)
        summary = transaction_service.get_vendor_transaction_summary(vendor_id)
        
        return summary
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vendor summary: {str(e)}"
        )