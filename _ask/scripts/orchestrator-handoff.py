#!/usr/bin/env python3
"""Verify the current runtime parent before authorized implementation work."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from datetime import datetime, timezone


ROOT = Path(os.environ.get('ASK_ROOT') or Path(__file__).resolve().parents[2]).resolve()
_SPEC = importlib.util.spec_from_file_location(
    'ask_runtime_decisions', ROOT / '_ask/scripts/model-decisions.py')
_DECISIONS = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_DECISIONS)


def observation_file(work_id: str) -> Path:
    work = _DECISIONS.work_file(work_id).parent
    path = work / 'traceability' / 'model-state' / 'orchestrator-handoff.json'
    for component in (work / 'traceability', work / 'traceability' / 'model-state', path):
        if component.is_symlink():
            raise ValueError('refuse symlinked model handoff state path')
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('model handoff state escapes repository')
    return path


def load_observation(work_id: str) -> dict:
    path = observation_file(work_id)
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {}
    if not isinstance(value, dict):
        raise ValueError('invalid model handoff observation')
    return value


def save_observation(work_id: str, value: dict) -> None:
    path = observation_file(work_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                     prefix='.handoff-', delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, ensure_ascii=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def manual_request(runtime: str, model: str, config: dict) -> dict:
    handoff = config.get('handoff') or {}
    command = handoff.get('manual_action') or f"use {runtime}'s active model selector"
    return {
        'status': 'manual_handoff',
        'request': f"{runtime.capitalize()}: {command.format(model=model)}; then resume this implementation.",
    }


def preflight(work_id: str, entry: str = 'implementation') -> dict:
    if entry in {'continue', 'plan', 'integration', 'terminal'}:
        return {'status': 'skipped', 'reason': f'{entry} entry does not start implementation'}
    if entry != 'implementation':
        raise ValueError(f'unsupported entry: {entry}')

    shown = _DECISIONS.show(work_id)
    runtime = shown['runtime']
    if not shown['confirmed']:
        return {'status': 'skipped', 'reason': 'legacy-configured model plan is unconfirmed'}
    model = _DECISIONS.resolve_implementor(work_id, runtime)
    config = _DECISIONS.runtime_config(_DECISIONS._MODELS.bindings_dir(ROOT), runtime)
    try:
        identity = _DECISIONS.runtime_request(runtime, 'identity')
    except ValueError:
        saved = load_observation(work_id)
        if (saved.get('status') == 'manually-observed'
                and saved.get('runtime') == runtime
                and saved.get('target_model') == model
                and saved.get('observed_model') == model
                and isinstance(saved.get('provenance'), str) and saved['provenance'].strip()):
            return {'status': 'ready', 'model': model, 'source': 'manual-observation',
                    'provenance': saved['provenance']}
        return manual_request(runtime, model, config)

    current = identity.get('model')
    if isinstance(current, str) and current == model:
        return {'status': 'ready', 'model': model, 'source': 'current-session-identity'}
    if isinstance(current, str) and current:
        try:
            result = _DECISIONS.runtime_request(runtime, 'switch', model=model)
        except ValueError:
            result = {}
        if result.get('supported') is True:
            try:
                verified = _DECISIONS.runtime_request(runtime, 'identity')
            except ValueError as exc:
                return {'status': 'blocked', 'reason': str(exc), 'model': model}
            if verified.get('model') == model:
                return {'status': 'ready', 'model': model, 'source': 'verified-current-session-switch'}
            return {'status': 'blocked', 'reason': 'current-session identity did not match after switch',
                    'model': model}

    saved = load_observation(work_id)
    if (not current and saved.get('status') == 'manually-observed'
            and saved.get('runtime') == runtime
            and saved.get('target_model') == model
            and saved.get('observed_model') == model
            and isinstance(saved.get('provenance'), str) and saved['provenance'].strip()):
        return {'status': 'ready', 'model': model, 'source': 'manual-observation',
                'provenance': saved['provenance']}
    return manual_request(runtime, model, config)


def record_observation(work_id: str, observed_model: str, provenance: str) -> dict:
    _path, _bind, _defaults, _consumer, work = _DECISIONS.load_inputs(work_id)
    plan = work.get('model_plan') or {}
    runtime = work.get('runtime') or plan.get('runtime')
    if plan.get('status') != 'confirmed' or not runtime or plan.get('runtime') != runtime:
        raise ValueError('no confirmed model plan is available for implementation')
    target = _DECISIONS.resolve_implementor(work_id, runtime)
    if observed_model != target:
        raise ValueError(f'observed model does not match selected implementor {target}')
    if not isinstance(provenance, str) or not provenance.strip():
        raise ValueError('manual observation requires provenance')
    observation = {
        'status': 'manually-observed',
        'runtime': runtime,
        'target_model': target,
        'observed_model': observed_model,
        'provenance': provenance.strip(),
        'recorded_at': datetime.now(timezone.utc).isoformat(),
    }
    save_observation(work_id, observation)
    return observation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('preflight')
    check.add_argument('--work-id', required=True)
    check.add_argument('--entry', default='implementation')
    resume = sub.add_parser('resume')
    resume.add_argument('--work-id', required=True)
    resume.add_argument('--observed-model', required=True)
    resume.add_argument('--provenance', required=True)
    args = parser.parse_args()
    if args.command == 'preflight':
        result = preflight(args.work_id, args.entry)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['status'] in {'ready', 'skipped'} else 2
    result = record_observation(args.work_id, args.observed_model, args.provenance)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f'orchestrator-handoff: {exc}', file=sys.stderr)
        raise SystemExit(2)
