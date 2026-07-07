from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Rule
from schemas import EvaluateRequest, EvaluateResponse, CategoryResult
from rule_engine import find_matching_rule

router = APIRouter(prefix="/api", tags=["evaluate"])

CATEGORIES = ["Eligibility", "Approval", "Verification", "Documentation", "Pricing"]


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_rules(request: EvaluateRequest, db: Session = Depends(get_db)):
    """
    Evaluate applicant data against all live rules.
    For each category, find the first matching rule and apply its decision/action.
    """
    results = {}
    has_reject = False
    has_manual_review = False
    
    for category in CATEGORIES:
        # Fetch all live rules for this product+category, sorted by priority
        rules = db.query(Rule).filter(
            Rule.product == request.product,
            Rule.category == category,
            Rule.status == "live",
        ).order_by(Rule.priority).all()
        
        # Convert rules to dict for rule_engine
        rules_data = [
            {
                "ruleId": rule.ruleId,
                "name": rule.name,
                "conditions": rule.conditions,
                "decision": rule.decision,
                "interestRate": rule.interestRate,
                "requiredDocuments": rule.requiredDocuments,
            }
            for rule in rules
        ]
        
        # Find matching rule
        matched_rule = find_matching_rule(request.applicantData, rules_data)
        
        if matched_rule:
            decision = matched_rule["decision"]
            matched_rule_id = matched_rule["ruleId"]
            matched_rule_name = matched_rule["name"]
            interest_rate = matched_rule.get("interestRate")
            required_docs = matched_rule.get("requiredDocuments")
        else:
            # Default fallback
            decision = "MANUAL_REVIEW"
            matched_rule_id = None
            matched_rule_name = "No matching rule - default fallback"
            interest_rate = None
            required_docs = None
        
        results[category] = CategoryResult(
            decision=decision,
            matchedRuleId=matched_rule_id,
            matchedRuleName=matched_rule_name,
            interestRate=interest_rate,
            requiredDocuments=required_docs,
        )
        
        # Track for overall decision
        if decision == "REJECT":
            has_reject = True
        elif decision == "MANUAL_REVIEW":
            has_manual_review = True
    
    # Derive overall decision
    if has_reject:
        overall_decision = "REJECT"
    elif has_manual_review:
        overall_decision = "MANUAL_REVIEW"
    else:
        overall_decision = "APPROVE"
    
    return EvaluateResponse(
        product=request.product,
        results=results,
        overallDecision=overall_decision,
    )
