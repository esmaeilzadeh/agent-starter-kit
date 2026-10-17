"""Qualified product and execution identities for v2 definitions."""


def product_identity(work_id, node_id):
    return {"work_id": work_id, "node_id": node_id}


def execution_identity(node):
    value = node.get("execution") if isinstance(node, dict) else None
    if not isinstance(value, dict) or set(value) != {"work_id", "task_id"}:
        return None
    if any(not isinstance(value[key], str) or not value[key].strip() for key in value):
        return None
    return value["work_id"], value["task_id"]


def identity_diagnostics(nodes, paths):
    errors = []
    aliases = {}
    for node_id, node in nodes.items():
        if node.get("type") != "task" or "execution" not in node:
            continue
        path = f"{paths[node_id]}.execution"
        identity = execution_identity(node)
        if identity is None:
            errors.append({"code": "EM001_EXECUTION_ID", "path": path,
                           "message": "execution needs nonempty work_id and task_id", "ids": [node_id]})
            continue
        if identity in aliases:
            errors.append({"code": "EM001_DUPLICATE_EXECUTION", "path": path,
                           "message": "execution task may have only one product alias",
                           "ids": [aliases[identity], node_id]})
        else:
            aliases[identity] = node_id
    return errors
