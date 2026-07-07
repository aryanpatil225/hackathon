import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from database import Base


class Rule(Base):
    __tablename__ = "rules"

    ruleId = Column(String, primary_key=True, index=True)
    product = Column(String, index=True)
    category = Column(String, index=True)  # Eligibility, Approval, Verification, Documentation, Pricing
    name = Column(String)
    priority = Column(Integer)
    conditions = Column(JSON)  # List of {field, operator, value}
    decision = Column(String)  # APPROVE, REJECT, MANUAL_REVIEW
    interestRate = Column(Float, nullable=True)
    requiredDocuments = Column(JSON, nullable=True)  # List of strings
    notes = Column(Text, nullable=True)
    status = Column(String)  # draft, live, archived
    version = Column(Integer, default=1)
    createdBy = Column(String)
    approvedBy = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Rule {self.ruleId}>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    ruleId = Column(String, index=True)
    action = Column(String)  # created, updated, published, archived
    changedBy = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    previousVersion = Column(Integer, nullable=True)
    newVersion = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.id}>"
