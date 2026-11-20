#!/usr/bin/env python3
"""Save and resolve a workstream's single Grill model decision."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile


ROOT = Path(os.environ.get('ASK_ROOT') or Path(__file__).resolve().parents[2]).resolve()
_SPEC = importlib.util.spec_from_file_location(
    'ask_runtime_models', ROOT / '_ask/scripts/sync-runtime-agents.py')
_MODELS = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_MODELS)


def work_file(work_id: str) -> Path:
    if work_id in {'.', '..'} or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', work_id):
        raise ValueError('invalid work id')
    root = ROOT / 'work'
    directory = root / work_id
    path = directory / 'models.yaml'
    if root.is_symlink() or directory.is_symlink() or path.is_symlink():
        raise ValueError('refuse symlinked work model path')
    if path.exists() and not path.is_file():
        raise ValueError('work model path is not a regular file')
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError('work id escapes work directory')
    return resolved


def load_inputs(work_id: str):
    bind = _MODELS.bindings_dir(ROOT)
    defaults = _MODELS.load_yaml(bind / 'models.defaults.yaml')
    consumer_path = ROOT / '.agents/ask.local/bindings/models.yaml'
    if not consumer_path.is_file():
        consumer_path = ROOT / '_ask/bindings/models.yaml'
    consumer = _MODELS.load_yaml(consumer_path)
    path = work_file(work_id)
    work = _MODELS.load_yaml(path)
    return path, bind, defaults, consumer, work


def yaml_scalar(value) -> str:
    if isinstance(value, str):
        if (re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value)
                and value.lower() not in {'true', 'false', 'null', 'yes', 'no', 'on', 'off', '~'}
                and not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)', value)):
            return value
    return json.dumps(value, ensure_ascii=False)


def dump_yaml(value, indent: int = 0) -> str:
    prefix = ' ' * indent
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if not isinstance(key, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', key):
                raise ValueError(f'invalid model record key: {key!r}')
            if isinstance(item, (dict, list)) and item:
                lines.append(f'{prefix}{key}:')
                lines.append(dump_yaml(item, indent + 2).rstrip('\n'))
            else:
                lines.append(f'{prefix}{key}: {yaml_scalar(item)}')
        return '\n'.join(lines) + '\n'
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)) and item:
                lines.append(f'{prefix}-')
                lines.append(dump_yaml(item, indent + 2).rstrip('\n'))
            else:
                lines.append(f'{prefix}- {yaml_scalar(item)}')
        return '\n'.join(lines) + '\n'
    return f'{prefix}{yaml_scalar(value)}\n'


def runtime_config(bind: Path, runtime: str) -> dict:
    if runtime not in _MODELS.RUNTIMES:
        raise ValueError(f'unsupported model runtime: {runtime}')
    cfg = _MODELS.load_yaml(bind / 'runtimes' / f'{runtime}.yaml')
    if not cfg:
        raise ValueError(f'unsupported model runtime: {runtime}')
    return cfg


def model_table(runtime: str, risk: str, defaults: dict, runtime_cfg: dict,
                consumer: dict, work: dict, env: dict, submitted: set[str] | None = None):
    submitted = submitted or set()
    resolved = {}
    for stage in _MODELS.STAGES:
        model = _MODELS.validate_model(
            _MODELS.resolve_slug(stage, runtime, defaults, runtime_cfg, consumer, work, env),
            runtime, stage,
        )
        configured = _MODELS.value_from_overlay(work, stage, runtime)
        if stage in submitted or (configured is not _MODELS.MISSING
                                  and not _MODELS.is_role_or_pool(configured)):
            source = 'exact-override'
        elif configured is not _MODELS.MISSING:
            source = 'configured-role'
        elif env.get(_MODELS.env_stage_key(stage) + '_' + runtime.upper()) is not None:
            source = 'environment'
        elif env.get(_MODELS.env_stage_key(stage)) is not None:
            source = 'environment'
        elif _MODELS.value_from_overlay(consumer, stage, runtime) is not _MODELS.MISSING:
            source = 'project-config'
        else:
            source = 'default'
        resolved[stage] = {
            'role': (defaults.get('stages') or {}).get(stage),
            'model': model,
            'source': source,
        }
    return resolved


def write_record(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                     prefix='.models-', delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(dump_yaml(record))
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def save(work_id: str, decision: dict) -> dict:
    if not isinstance(decision, dict):
        raise ValueError('model decision must be an object')
    runtime = decision.get('runtime')
    if not isinstance(runtime, str):
        raise ValueError('model decision requires a runtime')
    submission = decision.get('submission')
    if submission not in {'confirm', 'change'}:
        raise ValueError('submission must be confirm or change')
    policy = decision.get('implementation_policy')
    if policy not in {'latest-accessible', 'exact'}:
        raise ValueError('implementation_policy must be latest-accessible or exact')
    overrides = decision.get('overrides', {})
    if not isinstance(overrides, dict):
        raise ValueError('overrides must be a stage-to-model mapping')

    path, bind, defaults, consumer, work = load_inputs(work_id)
    cfg = runtime_config(bind, runtime)
    stages = set(_MODELS.STAGES)
    if set(overrides) - stages:
        raise ValueError('override names an unknown stage')
    for stage, model in overrides.items():
        _MODELS.validate_model(model, runtime, stage)

    risk = str(decision.get('risk') or work.get('risk') or os.environ.get('ASK_RISK') or 'LOW').upper()
    if risk not in {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}:
        raise ValueError(f'invalid workstream risk: {risk}')
    env = dict(os.environ)
    env['ASK_RISK'] = risk
    runtime_overlay = work.get(runtime)
    if not isinstance(runtime_overlay, dict):
        runtime_overlay = {}
    runtime_overlay.update(overrides)
    work[runtime] = runtime_overlay

    table = model_table(runtime, risk, defaults, cfg, consumer, work, env, set(overrides))
    if policy == 'exact' and '06-implement' not in overrides:
        runtime_overlay['06-implement'] = table['06-implement']['model']
        table['06-implement']['source'] = 'exact-policy'

    record = dict(work)
    record['risk'] = risk
    record['runtime'] = runtime
    record['model_plan'] = {
        'status': 'confirmed',
        'source': 'grill',
        'submission': submission,
        'runtime': runtime,
        'risk': risk,
        'implementation_policy': policy,
        'selections': table,
        'review_relationship': {
            'review_stage': '07-review',
            'implementation_stage': '06-implement',
            'review_model': table['07-review']['model'],
            'implementation_model': table['06-implement']['model'],
        },
    }
    write_record(path, record)
    return record['model_plan']


def show(work_id: str, runtime: str | None = None) -> dict:
    _path, bind, defaults, consumer, work = load_inputs(work_id)
    runtime = runtime or work.get('runtime') or os.environ.get('ASK_MODEL_RUNTIME') or 'codex'
    cfg = runtime_config(bind, runtime)
    risk = str(work.get('risk') or os.environ.get('ASK_RISK') or 'LOW').upper()
    env = dict(os.environ)
    env['ASK_RISK'] = risk
    selections = model_table(runtime, risk, defaults, cfg, consumer, work, env)
    saved = work.get('model_plan') or {}
    confirmed = saved.get('status') == 'confirmed'
    policy = saved.get('implementation_policy') if confirmed else 'legacy-configured'
    return {
        'runtime': runtime,
        'risk': risk,
        'confirmed': confirmed,
        'implementation_policy': policy,
        'policy_confirmed': confirmed,
        'selections': selections,
        'review_relationship': {
            'review_stage': '07-review',
            'implementation_stage': '06-implement',
            'review_model': selections['07-review']['model'],
            'implementation_model': selections['06-implement']['model'],
        },
    }


def resolve(work_id: str, stage: str, runtime: str | None = None) -> str:
    path, bind, defaults, consumer, work = load_inputs(work_id)
    del path
    runtime = runtime or work.get('runtime') or os.environ.get('ASK_MODEL_RUNTIME') or 'codex'
    stage = '01-grill' if stage == 'continuation' else stage
    if stage not in _MODELS.STAGES:
        raise ValueError(f'unknown model stage: {stage}')
    cfg = runtime_config(bind, runtime)
    env = dict(os.environ)
    env['ASK_RISK'] = str(work.get('risk') or env.get('ASK_RISK') or 'LOW')
    return _MODELS.validate_model(
        _MODELS.resolve_slug(stage, runtime, defaults, cfg, consumer, work, env),
        runtime, stage,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    for command in ('save', 'submit', 'show', 'resolve'):
        sub = subparsers.add_parser(command)
        sub.add_argument('--work-id', required=True)
        if command in {'save', 'submit'}:
            sub.add_argument('--runtime')
            sub.add_argument('--risk')
            sub.add_argument('--implementation-policy')
            sub.add_argument('--override', action='append', default=[])
        if command in {'show', 'resolve'}:
            sub.add_argument('--runtime')
        if command == 'resolve':
            sub.add_argument('--stage', required=True)
    args = parser.parse_args()
    if args.command in {'save', 'submit'}:
        import sys
        raw = sys.stdin.read()
        decision = json.loads(raw) if raw.strip() else {}
        if args.runtime:
            decision['runtime'] = args.runtime
        if args.risk:
            decision['risk'] = args.risk
        if args.implementation_policy:
            decision['implementation_policy'] = args.implementation_policy
        if args.override:
            decision.setdefault('overrides', {}).update(
                dict(item.split('=', 1) for item in args.override))
        decision.setdefault('submission', 'confirm')
        plan = save(args.work_id, decision)
        print(json.dumps(plan, ensure_ascii=False))
    elif args.command == 'show':
        print(json.dumps(show(args.work_id, args.runtime), ensure_ascii=False))
    else:
        print(resolve(args.work_id, args.stage, args.runtime))
    return 0


if __name__ == '__main__':
    import sys
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'model-decisions: {exc}', file=sys.stderr)
        raise SystemExit(2)
