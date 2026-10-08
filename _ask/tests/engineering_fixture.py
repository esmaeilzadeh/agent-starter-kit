"""Isolated Engineering Model fixtures; never modify a checked-in pilot."""


def decision_model():
    return {
        "schema": "ask-engineering-model/v1", "work_id": "pilot", "revision": 1,
        "nodes": [
            {"id": "purpose", "type": "intent", "title": "Purpose", "lifecycle": "active"},
            {"id": "choice", "type": "decision", "title": "Choose", "lifecycle": "open",
             "options": [{"id": "one", "label": "First"}, {"id": "two", "label": "Second"}],
             "history": []},
        ],
        "edges": [{"type": "contains", "source": "purpose", "target": "choice"}],
    }
