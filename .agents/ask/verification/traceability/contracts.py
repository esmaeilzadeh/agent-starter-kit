"""Small JSON contracts and precise violations; no inference from prose."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any

TYPES = {'unit', 'integration', 'e2e'}
POLICY = '_ask/policies/delegation.md'
EXEMPTIONS = {'documentation-only', 'generated-projections', 'non-behavioral-config'}

@dataclass(frozen=True)
class Violation:
    code: str
    criterion_id: str | None = None
    test_id: str | None = None
    required_type: str | None = None
    field: str | None = None

    def json(self):
        return {k:v for k,v in asdict(self).items() if v is not None}

class Invalid(ValueError):
    pass

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict:
    try:
        doc=json.loads(path.read_text())
    except (OSError,ValueError) as exc:
        raise Invalid(f'migration_required: missing/invalid JSON {path}: {exc}') from exc
    if not isinstance(doc,dict):
        raise Invalid(f'{path}: expected object')
    return doc

def text(value):
    return isinstance(value,str) and bool(value.strip())

def string_list(value,nonempty=True):
    return (isinstance(value,list) and (bool(value) or not nonempty)
            and all(text(x) for x in value) and len(value)==len(set(value)))

def safe_path(value):
    return text(value) and not Path(value).is_absolute() and '..' not in Path(value).parts and value!='.'

def slug(value):
    return isinstance(value,str) and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]*',value) is not None

def indexed(value,field,errors,key='id'):
    if not isinstance(value,list):
        errors.append(Violation('invalid_list',field=field));return {}
    out={}
    for item in value:
        if not isinstance(item,dict) or not text(item.get(key)):
            errors.append(Violation('missing_id',field=field));continue
        name=item[key]
        if name in out: errors.append(Violation('duplicate_id',field=f'{field}.{name}'))
        out[name]=item
    return out

def scenario(value):
    return (isinstance(value,dict) and text(value.get('given')) and text(value.get('when'))
            and string_list(value.get('then')))
