from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.database.session import get_db
from app.database.models import User, Transaction, TransactionType, TransactionStatus, TransactionSource
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionListResponse
from app.dependencies import get_current_user
from app.auth.permissions import is_finance

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_finance(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance users can create transactions"
        )
    
    transaction = Transaction(
        transaction_type=transaction_data.transaction_type,
        vendor_id=transaction_data.vendor_id,
        vendor_name=transaction_data.vendor_name,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        transaction_date=transaction_data.transaction_date,
        description=transaction_data.description,
        department=transaction_data.department,
        cost_center=transaction_data.cost_center,
        gl_account=transaction_data.gl_account,
        approver=transaction_data.approver,
        approval_date=transaction_data.approval_date,
        reference_number=transaction_data.reference_number,
        invoice_number=transaction_data.invoice_number,
        po_number=transaction_data.po_number,
        payment_method=transaction_data.payment_method,
        bank_account=transaction_data.bank_account,
        source=TransactionSource.MANUAL,
        created_by=current_user.id,
        metadata=transaction_data.metadata
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return TransactionResponse.model_validate(transaction)

@router.get("", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    vendor_id: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    transaction_type: Optional[TransactionType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)
    
    if is_finance(current_user.role):
        query = query.filter(Transaction.created_by == current_user.id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if vendor_id:
        query = query.filter(Transaction.vendor_id == vendor_id)
    if min_amount:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount:
        query = query.filter(Transaction.amount <= max_amount)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    total = query.count()
    
    transactions = query.order_by(desc(Transaction.created_at)) \
        .offset((page - 1) * limit) \
        .limit(limit) \
        .all()
    
    return TransactionListResponse(
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
        total=total,
        page=page,
        limit=limit
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if is_finance(current_user.role) and transaction.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return TransactionResponse.model_validate(transaction)