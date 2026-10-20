"""Impact decision API scaffold."""
class ImpactError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

def _graph(graph):
    return graph

def record_decision(decision, capture=None):
    return {"status": "incomplete", "propagation_stopped": False}

def assess_impact(graph, changed, decisions=None, capture=None):
    return {"status": "incomplete", "items": {}}
