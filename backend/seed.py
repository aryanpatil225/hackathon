import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from models import Rule, AuditLog


def seed_database(db: Session):
    """Seed the database with sample rules for MSME_Loan_v1."""
    
    # Clear existing rules and audit logs
    db.query(Rule).delete()
    db.query(AuditLog).delete()
    db.commit()
    
    product = "MSME_Loan_v1"
    rules_created = 0
    
    # Eligibility Rules
    eligibility_rules = [
        {
            "name": "Min income self-employed Tier2/3",
            "priority": 1,
            "conditions": [
                {"field": "employmentType", "operator": "==", "value": "self_employed"},
                {"field": "cityTier", "operator": "in", "value": ["Tier2", "Tier3"]},
                {"field": "monthlyIncome", "operator": ">=", "value": 12000},
                {"field": "creditScore", "operator": ">=", "value": 650},
            ],
            "decision": "APPROVE",
        },
        {
            "name": "Min income salaried any tier",
            "priority": 2,
            "conditions": [
                {"field": "employmentType", "operator": "==", "value": "salaried"},
                {"field": "monthlyIncome", "operator": ">=", "value": 15000},
                {"field": "creditScore", "operator": ">=", "value": 600},
            ],
            "decision": "APPROVE",
        },
        {
            "name": "Below minimum credit score",
            "priority": 3,
            "conditions": [
                {"field": "creditScore", "operator": "<", "value": 550},
            ],
            "decision": "REJECT",
        },
    ]
    
    for rule_data in eligibility_rules:
        rule = Rule(
            ruleId=str(uuid.uuid4()),
            product=product,
            category="Eligibility",
            name=rule_data["name"],
            priority=rule_data["priority"],
            conditions=rule_data["conditions"],
            decision=rule_data["decision"],
            status="live",
            version=1,
            createdBy="system",
            approvedBy="system",
        )
        db.add(rule)
        rules_created += 1
    
    # Approval Rules
    approval_rules = [
        {
            "name": "High loan amount manual review",
            "priority": 1,
            "conditions": [
                {"field": "loanAmount", "operator": ">", "value": 500000},
            ],
            "decision": "MANUAL_REVIEW",
        },
        {
            "name": "Standard auto-approve",
            "priority": 2,
            "conditions": [
                {"field": "loanAmount", "operator": "<=", "value": 500000},
                {"field": "creditScore", "operator": ">=", "value": 650},
            ],
            "decision": "APPROVE",
        },
    ]
    
    for rule_data in approval_rules:
        rule = Rule(
            ruleId=str(uuid.uuid4()),
            product=product,
            category="Approval",
            name=rule_data["name"],
            priority=rule_data["priority"],
            conditions=rule_data["conditions"],
            decision=rule_data["decision"],
            status="live",
            version=1,
            createdBy="system",
            approvedBy="system",
        )
        db.add(rule)
        rules_created += 1
    
    # Pricing Rules
    pricing_rules = [
        {
            "name": "Prime rate",
            "priority": 1,
            "conditions": [
                {"field": "creditScore", "operator": ">=", "value": 750},
            ],
            "decision": "APPROVE",
            "interestRate": 10.5,
        },
        {
            "name": "Standard rate",
            "priority": 2,
            "conditions": [
                {"field": "creditScore", "operator": ">=", "value": 650},
            ],
            "decision": "APPROVE",
            "interestRate": 13.5,
        },
        {
            "name": "Risk-based higher rate",
            "priority": 3,
            "conditions": [
                {"field": "creditScore", "operator": ">=", "value": 550},
            ],
            "decision": "APPROVE",
            "interestRate": 17.0,
        },
    ]
    
    for rule_data in pricing_rules:
        rule = Rule(
            ruleId=str(uuid.uuid4()),
            product=product,
            category="Pricing",
            name=rule_data["name"],
            priority=rule_data["priority"],
            conditions=rule_data["conditions"],
            decision=rule_data["decision"],
            interestRate=rule_data.get("interestRate"),
            status="live",
            version=1,
            createdBy="system",
            approvedBy="system",
        )
        db.add(rule)
        rules_created += 1
    
    # Verification Rules
    verification_rules = [
        {
            "name": "Self-employed extra verification",
            "priority": 1,
            "conditions": [
                {"field": "employmentType", "operator": "==", "value": "self_employed"},
            ],
            "decision": "MANUAL_REVIEW",
            "requiredDocuments": ["Bank statements - 6 months", "GST returns", "Business proof"],
        },
        {
            "name": "Salaried standard verification",
            "priority": 2,
            "conditions": [
                {"field": "employmentType", "operator": "==", "value": "salaried"},
            ],
            "decision": "APPROVE",
            "requiredDocuments": ["Salary slips - 3 months", "Form 16"],
        },
    ]
    
    for rule_data in verification_rules:
        rule = Rule(
            ruleId=str(uuid.uuid4()),
            product=product,
            category="Verification",
            name=rule_data["name"],
            priority=rule_data["priority"],
            conditions=rule_data["conditions"],
            decision=rule_data["decision"],
            requiredDocuments=rule_data.get("requiredDocuments"),
            status="live",
            version=1,
            createdBy="system",
            approvedBy="system",
        )
        db.add(rule)
        rules_created += 1
    
    # Documentation Rules
    documentation_rules = [
        {
            "name": "Standard KYC docs",
            "priority": 1,
            "conditions": [
                {"field": "loanAmount", "operator": ">", "value": 0},
            ],
            "decision": "APPROVE",
            "requiredDocuments": ["PAN Card", "Aadhaar Card", "Address Proof"],
        },
    ]
    
    for rule_data in documentation_rules:
        rule = Rule(
            ruleId=str(uuid.uuid4()),
            product=product,
            category="Documentation",
            name=rule_data["name"],
            priority=rule_data["priority"],
            conditions=rule_data["conditions"],
            decision=rule_data["decision"],
            requiredDocuments=rule_data.get("requiredDocuments"),
            status="live",
            version=1,
            createdBy="system",
            approvedBy="system",
        )
        db.add(rule)
        rules_created += 1
    
    db.commit()
    return rules_created
