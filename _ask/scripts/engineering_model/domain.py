"""Pure semantic command boundary; filesystem publication belongs to actions."""
from copy import deepcopy


def apply_batch(document, commands, *, timestamp=None):
    """Return a structured refusal for unsupported or malformed commands.

    Operations are added in behavior-tested slices; this boundary never mutates
    the caller's document, including when a proposal is refused.
    """
    return {"valid": False, "model": deepcopy(document), "diagnostics": [
        {"code": "EM002_COMMAND", "path": "$.commands", "message": "unsupported command batch"}], "effects": []}
