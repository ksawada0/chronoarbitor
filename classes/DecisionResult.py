#!/usr/bin/env python3

class DecisionResult:
    """Dataclass to represent decision results"""
    def __init__(self, decision, justification):
        self.decision = decision
        self.justification = justification