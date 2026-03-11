from fastapi import APIRouter
from app.api.v1 import auth, upload, transactions, cases

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(upload.router)
router.include_router(transactions.router)
router.include_router(cases.router)