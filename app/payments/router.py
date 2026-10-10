from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.payments import service
from app.payments.schemas import PaymentResponse

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=list[PaymentResponse])
def list_payments(db: Session = Depends(get_db)):
    return service.list_payments(db)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = service.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment


@router.get("/user/{user_id}", response_model=list[PaymentResponse])
def list_payments_by_user(user_id: int, db: Session = Depends(get_db)):
    return service.list_payments_by_user(db, user_id)
