"""
Flat rule evaluator: pure function, no DB dependency.
Each rule is a list of conditions joined by AND.
Multiple rules are evaluated in priority order; first match wins.
"""


def evaluate_condition(applicant_data: dict, condition: dict) -> bool:
    """
    Evaluate a single condition against applicant data.
    
    Condition format: {"field": str, "operator": str, "value": Any}
    Operators: ">=", "<=", ">", "<", "==", "!=", "in", "not_in"
    """
    field = condition.get("field")
    operator = condition.get("operator")
    value = condition.get("value")
    
    if field not in applicant_data:
        return False
    
    applicant_value = applicant_data[field]
    
    if operator == ">=":
        return applicant_value >= value
    elif operator == "<=":
        return applicant_value <= value
    elif operator == ">":
        return applicant_value > value
    elif operator == "<":
        return applicant_value < value
    elif operator == "==":
        return applicant_value == value
    elif operator == "!=":
        return applicant_value != value
    elif operator == "in":
        return applicant_value in value
    elif operator == "not_in":
        return applicant_value not in value
    else:
        raise ValueError(f"Unknown operator: {operator}")


def evaluate_rule(applicant_data: dict, rule_conditions: list) -> bool:
    """
    Evaluate all conditions in a rule (AND logic).
    All conditions must be true for the rule to match.
    """
    if not rule_conditions:
        return True
    
    for condition in rule_conditions:
        if not evaluate_condition(applicant_data, condition):
            return False
    
    return True


def find_matching_rule(applicant_data: dict, rules: list) -> dict | None:
    """
    Find the first (highest priority) matching rule.
    Rules are assumed to be already sorted by priority (ascending).
    Returns the matched rule or None.
    """
    for rule in rules:
        if evaluate_rule(applicant_data, rule.get("conditions", [])):
            return rule
    return None
