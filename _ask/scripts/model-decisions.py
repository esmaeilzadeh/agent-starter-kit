#!/usr/bin/env python3
"""Save and resolve a workstream's single Grill model decision."""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
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
        reserved = {
            'true', 'false', 'null', 'yes', 'no', 'on', 'off', '~',
            '.nan', 'nan', '.inf', 'inf', '+.inf', '-.inf', '+inf', '-inf',
            '.infinity', 'infinity', '+.infinity', '-.infinity',
        }
        if (re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]*', value)
                and value.lower() not in reserved):
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


def effective_risk(work: dict, consumer: dict, env: dict,
                   submitted: str | None = None) -> str:
    value = (submitted or work.get('risk') or consumer.get('risk')
             or env.get('ASK_RISK') or 'LOW')
    risk = str(value).upper()
    if risk not in {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}:
        raise ValueError(f'invalid workstream risk: {risk}')
    return risk


def runtime_request(runtime: str, action: str, **fields) -> dict:
    adapter = os.environ.get('ASK_MODEL_RUNTIME_ADAPTER')
    if not adapter:
        raise ValueError(f'{runtime} runtime adapter is unavailable')
    command = shlex.split(adapter)
    if not command:
        raise ValueError(f'{runtime} runtime adapter is unavailable')
    request = {'action': action, 'runtime': runtime, **fields}
    try:
        result = subprocess.run(command, input=json.dumps(request), text=True,
                                capture_output=True, check=False, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f'{runtime} {action} evidence unavailable: {exc}') from exc
    if result.returncode:
        raise ValueError(f'{runtime} {action} evidence unavailable: adapter exited {result.returncode}')
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f'{runtime} {action} evidence unavailable: invalid adapter response') from exc
    if not isinstance(response, dict):
        raise ValueError(f'{runtime} {action} evidence unavailable: expected an object')
    return response


def capability(runtime: str) -> dict:
    report = {'runtime': runtime, 'catalog': 'unknown', 'identity': 'unknown',
              'switch': 'unknown', 'evidence': []}
    runtime_config(_MODELS.bindings_dir(ROOT), runtime)
    try:
        catalog = runtime_request(runtime, 'catalog')
        models = catalog.get('models')
        if catalog.get('supported') is False:
            report['catalog'] = 'unsupported'
        elif (catalog.get('authenticated') is True and catalog.get('access_verified') is True
              and isinstance(models, list) and all(isinstance(item, str) for item in models)):
            report['catalog'] = 'supported'
        report['evidence'].append({'action': 'catalog', 'status': report['catalog'],
                                   'source': 'current-session-adapter'})
    except ValueError:
        pass
    try:
        identity = runtime_request(runtime, 'identity')
        if isinstance(identity.get('model'), str) and identity['model']:
            report['identity'] = 'supported'
        elif identity.get('supported') is False:
            report['identity'] = 'unsupported'
        if identity.get('switch_supported') is True:
            report['switch'] = 'supported'
        elif identity.get('switch_supported') is False:
            report['switch'] = 'unsupported'
        report['evidence'].append({'action': 'identity', 'status': report['identity'],
                                   'switch': report['switch'],
                                   'source': 'current-session-adapter'})
    except ValueError:
        pass
    return report


def resolve_implementor(work_id: str, runtime: str | None = None) -> str:
    _path, bind, defaults, consumer, work = load_inputs(work_id)
    runtime = runtime or work.get('runtime') or os.environ.get('ASK_MODEL_RUNTIME') or 'codex'
    cfg = runtime_config(bind, runtime)
    plan = work.get('model_plan') or {}
    if plan.get('status') != 'confirmed' or plan.get('runtime') != runtime:
        return resolve(work_id, '06-implement', runtime)

    configured = _MODELS.value_from_overlay(work, '06-implement', runtime)
    if configured is not _MODELS.MISSING and not _MODELS.is_role_or_pool(configured):
        return _MODELS.validate_model(configured, runtime, '06-implement')
    if plan.get('implementation_policy') == 'exact':
        selection = (plan.get('selections') or {}).get('06-implement') or {}
        return _MODELS.validate_model(selection.get('model'), runtime, '06-implement')
    if plan.get('implementation_policy') != 'latest-accessible':
        raise ValueError('confirmed model plan has no implementation policy')

    catalog = runtime_request(runtime, 'catalog')
    if catalog.get('authenticated') is not True or catalog.get('access_verified') is not True:
        raise ValueError(f'{runtime} catalog does not prove current account access')
    models = catalog.get('models')
    if not isinstance(models, list) or not models or not all(isinstance(item, str) for item in models):
        raise ValueError(f'{runtime} catalog did not provide current accessible models')
    current = (plan.get('selections') or {}).get('06-implement') or {}
    base = current.get('model')
    families = cfg.get('families') or []
    family = cfg.get('implementation_family')
    variant = cfg.get('implementation_variant')
    if family is None:
        family = next((item for item in families
                       if isinstance(item, str) and (base == item or base.startswith(item + '-'))), None)
    if not isinstance(family, str) or not family:
        raise ValueError(f'{runtime} implementation family cannot be identified')
    accessible = [item for item in models
                  if (item == family or item.startswith(family + '-'))
                  and (not isinstance(variant, str) or not variant
                       or item.endswith('-' + variant))]
    if not accessible:
        raise ValueError(f'{runtime} catalog has no current accessible model in family {family}')
    if len(accessible) == 1:
        return _MODELS.validate_model(accessible[0], runtime, '06-implement')
    order = catalog.get('order')
    if (not isinstance(order, list) or not all(isinstance(item, str) for item in order)
            or len(order) != len(set(order)) or not set(accessible).issubset(order)
            or not set(order).issubset(models)):
        raise ValueError(f'{runtime} catalog lacks explicit version ordering evidence for {family}')
    return _MODELS.validate_model(
        [item for item in order if item in accessible][-1], runtime, '06-implement')


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

    risk = effective_risk(work, consumer, os.environ, decision.get('risk'))
    env = dict(os.environ)
    env['ASK_RISK'] = risk
    previous = work.get('model_plan') or {}
    previous_runtime = previous.get('runtime')
    explicit_before = previous.get('explicit_overrides') or []
    materialized_before = previous.get('materialized_overrides') or []
    explicit_before = ([stage for stage in explicit_before
                        if isinstance(stage, str) and stage in stages]
                       if isinstance(explicit_before, list) else [])
    materialized_before = ([stage for stage in materialized_before
                            if isinstance(stage, str) and stage in stages]
                           if isinstance(materialized_before, list) else [])
    previous_overrides = explicit_before + materialized_before
    if submission == 'confirm' and previous.get('status') == 'confirmed':
        if previous_runtime != runtime or previous.get('implementation_policy') != policy:
            raise ValueError('changing a confirmed model plan requires submission=change')
        retained = {}
        for stage in explicit_before:
            configured = _MODELS.value_from_overlay(work, stage, runtime)
            if configured is not _MODELS.MISSING:
                retained[stage] = configured
        for stage, model in overrides.items():
            if stage not in retained or retained[stage] != model:
                raise ValueError('changing a saved stage override requires submission=change')
        overrides = retained
    if submission == 'change' and previous_runtime in _MODELS.RUNTIMES:
        prior_overlay = work.get(previous_runtime)
        if isinstance(prior_overlay, dict):
            for stage in previous_overrides:
                prior_overlay.pop(stage, None)
    runtime_overlay = work.get(runtime)
    if not isinstance(runtime_overlay, dict):
        runtime_overlay = {}
    runtime_overlay.update(overrides)
    work[runtime] = runtime_overlay
    work['risk'] = risk

    table = model_table(runtime, risk, defaults, cfg, consumer, work, env, set(overrides))
    materialized_overrides = []
    if policy == 'exact' and '06-implement' not in overrides:
        runtime_overlay['06-implement'] = table['06-implement']['model']
        table['06-implement']['source'] = 'exact-policy'
        materialized_overrides.append('06-implement')

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
        'explicit_overrides': sorted(overrides),
        'materialized_overrides': materialized_overrides,
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
    risk = effective_risk(work, consumer, os.environ)
    env = dict(os.environ)
    env['ASK_RISK'] = risk
    selections = model_table(runtime, risk, defaults, cfg, consumer, work, env)
    saved = work.get('model_plan') or {}
    confirmed = saved.get('status') == 'confirmed' and saved.get('runtime') == runtime
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
    env['ASK_RISK'] = effective_risk(work, consumer, env)
    return _MODELS.validate_model(
        _MODELS.resolve_slug(stage, runtime, defaults, cfg, consumer, work, env),
        runtime, stage,
    )


def _confidence(value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 100:
        raise ValueError('confidence must be a finite number from 0 to 100')
    return float(value)


def _confidence_ladder(work_id: str, runtime: str, runtime_cfg: dict) -> list[tuple[str, str | None]]:
    _, _, _, consumer, work = load_inputs(work_id)
    configured = runtime_cfg.get('confidence_escalation') or []
    for source in (consumer, work):
        if 'confidence_escalation' in source:
            overrides = source['confidence_escalation']
            if not isinstance(overrides, dict):
                raise ValueError('confidence_escalation overrides must map runtimes to ordered lists')
        else:
            overrides = {}
        if runtime in overrides:
            configured = overrides[runtime]
    if not isinstance(configured, list):
        raise ValueError('confidence_escalation must be an ordered list for the active runtime')
    ladder = []
    for value in configured:
        if not isinstance(value, str) or not value.strip() or value.count('@') > 1:
            raise ValueError('confidence_escalation entries must be native model names with optional @effort')
        model, separator, effort = value.partition('@')
        if not model or (separator and not effort):
            raise ValueError('confidence_escalation entries must be native model names with optional @effort')
        pair = (model, effort if separator else None)
        if pair not in ladder:
            ladder.append(pair)
    return ladder


def decide(work_id: str, request: dict) -> dict:
    """Choose one native consultation rung for one material decision."""
    for field in ('decision_id', 'evidence_digest', 'session_id'):
        if not isinstance(request.get(field), str) or not request[field].strip():
            raise ValueError('decision requires ' + field)
    if not re.fullmatch(r'[0-9a-f]{64}', request['evidence_digest']):
        raise ValueError('decision evidence_digest must be SHA256')
    confidence = _confidence(request.get('confidence'))
    identity = {key: request[key] for key in ('decision_id', 'evidence_digest', 'session_id')}
    def outcome(action, reason, **extra):
        return {**identity, 'action': action, 'reason': reason, **extra}
    authority = request.get('authority_kind')
    if authority != 'within-scope':
        return outcome('ask-human', 'human authority required: ' + str(authority))
    if request.get('human_decision_required') or request.get('model_restriction_requires_choice'):
        return outcome('ask-human', 'explicit human authority or model preference')
    if confidence > 90:
        return outcome('continue', 'confidence above policy threshold', confidence=confidence)
    runtime = request.get('runtime') or os.environ.get('ASK_MODEL_RUNTIME') or 'codex'
    try:
        cfg = runtime_config(_MODELS.bindings_dir(ROOT), runtime)
        ladder = _confidence_ladder(work_id, runtime, cfg)
    except ValueError:
        return outcome('ask-human', 'runtime has no verified confidence ladder')
    if not ladder:
        return outcome('ask-human', 'runtime has no verified confidence ladder')
    evidence = request.get('capability_evidence') or {}
    valid_catalog = (evidence.get('session_id') == identity['session_id']
                     and evidence.get('runtime') == runtime
                     and evidence.get('source') in {'native-tool-metadata', 'current-session-adapter'}
                     and evidence.get('authenticated') is True
                     and evidence.get('access_verified') is True)
    models = evidence.get('models') if valid_catalog else []
    if not isinstance(models, list):
        models = []
    allowed = request.get('allowed_models')
    if allowed is not None and (not isinstance(allowed, list) or not all(isinstance(m, str) for m in allowed)):
        raise ValueError('allowed_models must be a list of native model names')
    assessments = request.get('assessments') or []
    if not isinstance(assessments, list):
        raise ValueError('assessments must be a list')
    used = -1
    latest = None
    for assessment in assessments:
        if not isinstance(assessment, dict):
            raise ValueError('assessment must be an object')
        if any(assessment.get(k) != v for k, v in identity.items()):
            continue
        pair = (assessment.get('requested_model'), assessment.get('requested_effort'))
        if pair not in ladder:
            continue
        rank = ladder.index(pair)
        status = assessment.get('status')
        verified = (assessment.get('identity_verified') is True
                    and assessment.get('actual_model') == pair[0]
                    and assessment.get('actual_effort') == pair[1])
        if status not in {'assessed', 'unavailable'}:
            raise ValueError('invalid assessment status')
        if status == 'assessed':
            if not verified or not isinstance(assessment.get('assessment'), str) or not assessment['assessment'].strip():
                raise ValueError('assessment requires verified returned identity and reasoning; record unavailable otherwise')
            _confidence(assessment.get('confidence'))
        if rank >= used:
            used, latest = rank, assessment
    if latest and latest.get('status') == 'assessed' and latest['confidence'] > 90:
        return outcome('continue', 'applicable verified assessment above threshold', assessment=latest)
    unavailable = []
    for rank, (model, effort) in enumerate(ladder):
        if rank <= used:
            continue
        available = any(isinstance(m, dict) and m.get('model') == model
                        and (effort is None or (isinstance(m.get('efforts'), list)
                             and effort in m['efforts'])) for m in models)
        if not available or (allowed is not None and model not in allowed):
            unavailable.append({'model': model, 'effort': effort,
                                'reason': 'unavailable model/effort or explicit restriction'})
            continue
        if any(not isinstance(request.get(k), str) or not request[k].strip()
               for k in ('decision', 'scope', 'uncertainty')):
            raise ValueError('consultation requires readable decision, scope and uncertainty')
        if not isinstance(request.get('evidence'), (str, list, dict)) or not request['evidence']:
            raise ValueError('consultation requires concrete evidence or inspectable references')
        return outcome('consult', 'material uncertainty requires next verified native rung',
                       runtime=runtime, model=model, effort=effort, unavailable=unavailable,
                       request={'action': 'consult', 'runtime': runtime, 'model': model,
                                'effort': effort, **identity, 'scope': request['scope'],
                                'decision': request['decision'], 'evidence': request['evidence'],
                                'confidence': confidence,
                                'uncertainty': request.get('uncertainty'), 'assessments': assessments})
    return outcome('ask-human', 'available ladder exhausted with material uncertainty', unavailable=unavailable)


def consult(work_id: str, request: dict) -> dict:
    """Execute the selected request through the existing runtime adapter."""
    decision = decide(work_id, request)
    if decision['action'] != 'consult':
        return decision
    native = decision['request']
    record = {key: decision[key] for key in ('decision_id', 'evidence_digest', 'session_id')}
    record.update(requested_model=decision['model'], requested_effort=decision['effort'])
    try:
        response = runtime_request(native['runtime'], 'consult', **{
            k: v for k, v in native.items() if k not in {'action', 'runtime'}})
        if (response.get('session_id') != request['session_id']
                or response.get('decision_id') != request['decision_id']
                or response.get('evidence_digest') != request['evidence_digest']
                or response.get('actual_model') != decision['model']
                or response.get('actual_effort') != decision['effort']
                or response.get('identity_verified') is not True
                or not isinstance(response.get('assessment'), str) or not response['assessment'].strip()):
            raise ValueError('returned assessment identity or decision binding is unverifiable')
        confidence = _confidence(response.get('confidence'))
        record.update(status='assessed', confidence=confidence, assessment=response['assessment'],
                      actual_model=response['actual_model'], actual_effort=response.get('actual_effort'), identity_verified=True)
    except ValueError as exc:
        record.update(status='unavailable', reason=str(exc))
    updated = dict(request, assessments=[*(request.get('assessments') or []), record])
    return {'assessment': record, 'next': decide(work_id, updated)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    for command in ('save', 'submit', 'show', 'resolve', 'resolve-implementor', 'capability', 'decide', 'consult'):
        sub = subparsers.add_parser(command)
        sub.add_argument('--work-id', required=True)
        if command in {'save', 'submit'}:
            sub.add_argument('--runtime')
            sub.add_argument('--risk')
            sub.add_argument('--implementation-policy')
            sub.add_argument('--override', action='append', default=[])
        if command in {'show', 'resolve', 'resolve-implementor', 'capability'}:
            sub.add_argument('--runtime')
        if command == 'resolve':
            sub.add_argument('--stage', required=True)
    args = parser.parse_args()
    if args.command in {'decide', 'consult'}:
        import sys
        request = json.load(sys.stdin)
        if not isinstance(request, dict):
            raise ValueError('decision request must be an object')
        operation = decide if args.command == 'decide' else consult
        print(json.dumps(operation(args.work_id, request), allow_nan=False))
    elif args.command in {'save', 'submit'}:
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
    elif args.command == 'resolve-implementor':
        print(resolve_implementor(args.work_id, args.runtime))
    elif args.command == 'capability':
        runtime = args.runtime or os.environ.get('ASK_MODEL_RUNTIME') or 'codex'
        print(json.dumps(capability(runtime), ensure_ascii=False))
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
