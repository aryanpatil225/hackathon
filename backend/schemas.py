from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class Condition(BaseModel):
    field: str
    operator: str  # ">=", "<=", ">", "<", "==", "!=", "in", "not_in"
    value: Any


class RuleCreate(BaseModel):
    product: str
    category: str
    name: str
    priority: int
    conditions: List[Condition]
    decision: str
    interestRate: Optional[float] = None
    requiredDocuments: Optional[List[str]] = None
    notes: Optional[str] = None


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    priority: Optional[int] = None
    conditions: Optional[List[Condition]] = None
    decision: Optional[str] = None
    interestRate: Optional[float] = None
    requiredDocuments: Optional[List[str]] = None
    notes: Optional[str] = None


class PublishRule(BaseModel):
    approvedBy: str


class RuleResponse(BaseModel):
    ruleId: str
    product: str
    category: str
    name: str
    priority: int
    conditions: List[Condition]
    decision: str
    interestRate: Optional[float]
    requiredDocuments: Optional[List[str]]
    notes: Optional[str]
    status: str
    version: int
    createdBy: str
    approvedBy: Optional[str]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    ruleId: str
    action: str
    changedBy: str
    timestamp: datetime
    previousVersion: Optional[int]
    newVersion: Optional[int]

    class Config:
        from_attributes = True


class CategoryResult(BaseModel):
    decision: str
    matchedRuleId: Optional[str]
    matchedRuleName: str
    interestRate: Optional[float] = None
    requiredDocuments: Optional[List[str]] = None


class EvaluateRequest(BaseModel):
    product: str
    applicantData: Dict[str, Any]


class EvaluateResponse(BaseModel):
    product: str
    results: Dict[str, CategoryResult]
    overallDecision: str


class SeedResponse(BaseModel):
    message: str
    rules_created: int
