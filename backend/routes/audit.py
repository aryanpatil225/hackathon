from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import AuditLog
from schemas import AuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(db: Session = Depends(get_db)):
    """Get all audit log entries, newest first."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return logs
