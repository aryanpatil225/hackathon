import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Rule, AuditLog
from schemas import RuleCreate, RuleUpdate, RuleResponse, PublishRule, AuditLogResponse

router = APIRouter(prefix="/api/rules", tags=["rules"])

# Allowed operators for validation
ALLOWED_OPERATORS = [">=", "<=", ">", "<", "==", "!=", "in", "not_in"]
ALLOWED_CATEGORIES = ["Eligibility", "Approval", "Verification", "Documentation", "Pricing"]
ALLOWED_DECISIONS = ["APPROVE", "REJECT", "MANUAL_REVIEW"]


@router.post("", response_model=RuleResponse)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """Create a new rule as status 'draft'."""
    
    # Validate operators
    for condition in rule.conditions:
        if condition.operator not in ALLOWED_OPERATORS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operator '{condition.operator}'. Allowed: {ALLOWED_OPERATORS}"
            )
    
    # Validate category
    if rule.category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{rule.category}'. Allowed: {ALLOWED_CATEGORIES}"
        )
    
    # Validate decision
    if rule.decision not in ALLOWED_DECISIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision '{rule.decision}'. Allowed: {ALLOWED_DECISIONS}"
        )
    
    # Create rule
    new_rule = Rule(
        ruleId=str(uuid.uuid4()),
        product=rule.product,
        category=rule.category,
        name=rule.name,
        priority=rule.priority,
        conditions=[cond.model_dump() for cond in rule.conditions],
        decision=rule.decision,
        interestRate=rule.interestRate,
        requiredDocuments=rule.requiredDocuments,
        notes=rule.notes,
        status="draft",
        version=1,
        createdBy="maker",  # In a real app, use authenticated user
    )
    
    db.add(new_rule)
    
    # Audit log
    audit = AuditLog(
        ruleId=new_rule.ruleId,
        action="created",
        changedBy="maker",
        newVersion=1,
    )
    db.add(audit)
    
    db.commit()
    db.refresh(new_rule)
    return new_rule


@router.get("", response_model=List[RuleResponse])
def list_rules(
    product: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List/filter rules by product, category, or status."""
    query = db.query(Rule)
    
    if product:
        query = query.filter(Rule.product == product)
    if category:
        query = query.filter(Rule.category == category)
    if status:
        query = query.filter(Rule.status == status)
    
    return query.order_by(Rule.priority).all()


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: str, db: Session = Depends(get_db)):
    """Get a single rule."""
    rule = db.query(Rule).filter(Rule.ruleId == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: str,
    update: RuleUpdate,
    db: Session = Depends(get_db),
):
    """Update a draft rule. Cannot update live rules."""
    rule = db.query(Rule).filter(Rule.ruleId == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    if rule.status == "live":
        raise HTTPException(
            status_code=400,
            detail="Cannot edit a live rule. Clone into a draft version instead."
        )
    
    # Validate operators if conditions are being updated
    if update.conditions:
        for condition in update.conditions:
            if condition.operator not in ALLOWED_OPERATORS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid operator '{condition.operator}'. Allowed: {ALLOWED_OPERATORS}"
                )
    
    # Validate decision if being updated
    if update.decision and update.decision not in ALLOWED_DECISIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision '{update.decision}'. Allowed: {ALLOWED_DECISIONS}"
        )
    
    # Update fields
    if update.name is not None:
        rule.name = update.name
    if update.priority is not None:
        rule.priority = update.priority
    if update.conditions is not None:
        rule.conditions = [cond.model_dump() for cond in update.conditions]
    if update.decision is not None:
        rule.decision = update.decision
    if update.interestRate is not None:
        rule.interestRate = update.interestRate
    if update.requiredDocuments is not None:
        rule.requiredDocuments = update.requiredDocuments
    if update.notes is not None:
        rule.notes = update.notes
    
    rule.version += 1
    rule.updatedAt = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        ruleId=rule_id,
        action="updated",
        changedBy="maker",
        previousVersion=rule.version - 1,
        newVersion=rule.version,
    )
    db.add(audit)
    
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/{rule_id}/publish", response_model=RuleResponse)
def publish_rule(
    rule_id: str,
    publish_data: PublishRule,
    db: Session = Depends(get_db),
):
    """Publish a draft rule (move to live)."""
    rule = db.query(Rule).filter(Rule.ruleId == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    if rule.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft rules can be published"
        )
    
    # Archive previous live rule with same name+category if exists
    previous_live = db.query(Rule).filter(
        Rule.product == rule.product,
        Rule.category == rule.category,
        Rule.name == rule.name,
        Rule.status == "live",
    ).first()
    
    if previous_live:
        previous_live.status = "archived"
        audit = AuditLog(
            ruleId=previous_live.ruleId,
            action="archived",
            changedBy=publish_data.approvedBy,
            newVersion=previous_live.version,
        )
        db.add(audit)
    
    # Publish the new rule
    rule.status = "live"
    rule.approvedBy = publish_data.approvedBy
    rule.updatedAt = datetime.utcnow()
    
    audit = AuditLog(
        ruleId=rule_id,
        action="published",
        changedBy=publish_data.approvedBy,
        newVersion=rule.version,
    )
    db.add(audit)
    
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/{rule_id}/versions", response_model=List[AuditLogResponse])
def get_rule_versions(rule_id: str, db: Session = Depends(get_db)):
    """Get version history for a rule."""
    audits = db.query(AuditLog).filter(AuditLog.ruleId == rule_id).order_by(
        AuditLog.timestamp.desc()
    ).all()
    return audits
