"""Resumable evidence ledger, not a modeller, scheduler or acceptance gate."""
import hashlib
import html
import json
import os
import tempfile
from pathlib import Path

from .common import PipelineError


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    from .preservation import strict_json
    return strict_json(Path(path).read_text(encoding='utf-8'))


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False) + '\n')


def create(path, goal, construction_stop, deadline, views):
    if not goal.strip() or not 0 < construction_stop < deadline:
        raise PipelineError('need a goal and 0 < construction_stop < deadline')
    if not views or len(set(views)) != len(views):
        raise PipelineError('need unique governing view names')
    write_new(path, dict(version=1, goal=goal, construction_stop=construction_stop,
                         deadline=deadline, views=views, events=[]))


def artifact(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise PipelineError(f'missing artifact: {path}')
    return dict(path=str(path), sha256=digest(path))


def verify(item):
    if digest(item['path']) != item['sha256']:
        raise PipelineError(f'artifact changed: {item["path"]}')


def latest(document, kind, role):
    return next((event for event in reversed(document['events'])
                 if event['kind'] == kind and event['role'] == role), None)


def begin_budget(path, continuation, construction_stop, deadline, reason):
    """Explicit budget revision. Units are runner operations, NOT model turns."""
    document = load(path)
    if (not continuation or not reason.strip() or type(construction_stop) is not int
            or type(deadline) is not int or not 0 < construction_stop < deadline):
        raise PipelineError('need continuation, reason and integer 0 < stop < deadline')
    history = document.setdefault('budgets', [])
    if any(item['continuation'] == continuation for item in history):
        raise PipelineError('continuation already exists')
    if any(e['kind'] == 'operation' and e['state'] == 'running' for e in document['events']):
        raise PipelineError('reconcile running operation before changing budget')
    history.append(dict(continuation=continuation, construction_stop=construction_stop,
                        deadline=deadline, reason=reason, unit='runner_operations'))
    document['construction_stop'], document['deadline'] = construction_stop, deadline
    _update(path, document)


def _update(path, document):
    path = Path(path)
    payload = json.dumps(document, indent=2, allow_nan=False) + '\n'
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix=path.name+'.', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def operation_count(document):
    continuation = document['budgets'][-1]['continuation']
    return sum(e['kind'] == 'operation' and e['continuation'] == continuation
               for e in document['events'])


def start_operation(path, stage, construction=False):
    document = load(path)
    if not document.get('budgets'):
        raise PipelineError('runner requires an explicit continuation budget')
    if any(e['kind'] == 'operation' and e['state'] != 'complete' for e in document['events']):
        raise PipelineError('failed/running operation needs explicit reconciliation; no automatic retry')
    budget = document['budgets'][-1]
    count = operation_count(document)
    if count >= budget['deadline'] or construction and count >= budget['construction_stop']:
        raise PipelineError('operation outside recorded budget/reserve')
    event = dict(kind='operation', stage=stage, continuation=budget['continuation'],
                 step=count + 1, state='running')
    document['events'].append(event)
    _update(path, document)
    return count + 1


def finish_operation(path, stage, success, **evidence):
    document = load(path)
    event = document['events'][-1]
    if event['kind'] != 'operation' or event['stage'] != stage or event['state'] != 'running':
        raise PipelineError('operation completion does not match running stage')
    event.update(state='complete' if success else 'failed', **evidence)
    _update(path, document)


def record(path, kind, role, file, step, outcome=None, view=None, metadata=None):
    """Append one observation; events retained so a replacement cannot erase history."""
    document = load(path)
    if kind not in ('checkpoint', 'check', 'capture') or role not in ('before', 'after'):
        raise PipelineError('invalid kind or role')
    if type(step) is not int or step < 0:
        raise PipelineError('step must be a nonnegative integer')
    if document.get('budgets'):
        if step != operation_count(document):
            raise PipelineError('step must equal the recorded runner operation count')
    event = dict(kind=kind, role=role, step=step, artifact=artifact(file))
    if kind != 'checkpoint':
        checkpoint = latest(document, 'checkpoint', role)
        if checkpoint is None:
            raise PipelineError('record the checkpoint first')
        verify(checkpoint['artifact'])
        event['checkpoint_sha256'] = checkpoint['artifact']['sha256']
    if kind == 'check':
        if outcome not in ('pass', 'fail', 'error'):
            raise PipelineError('check needs explicit pass/fail/error outcome')
        event['outcome'] = outcome
    if kind == 'capture':
        check = latest(document, 'check', role)
        if (check is None or check['outcome'] != 'pass'
                or check['checkpoint_sha256'] != event['checkpoint_sha256']):
            raise PipelineError('capture requires a passing check for this checkpoint')
        verify(check['artifact'])
        if view not in document['views'] or metadata is None:
            raise PipelineError('capture needs governing view and metadata JSON')
        # This is a declaration from the capture producer, not inferred from a filename.
        data = load(metadata)
        required = {'checkpoint_sha256', 'view', 'camera', 'resolution', 'shading', 'visibility'}
        if not isinstance(data, dict) or set(data) != required:
            raise PipelineError('metadata needs exactly ' + ', '.join(sorted(required)))
        if data['checkpoint_sha256'] != event['checkpoint_sha256'] or data['view'] != view:
            raise PipelineError('capture metadata does not identify this checkpoint/view')
        if not isinstance(data['camera'], dict) or not data['camera']:
            raise PipelineError('camera metadata must include transform and projection settings')
        if not {'matrix_world', 'type', 'lens', 'ortho_scale'} <= set(data['camera']):
            raise PipelineError('camera needs matrix_world, type, lens and ortho_scale')
        matrix = data['camera']['matrix_world']
        if (not isinstance(matrix, list) or len(matrix) != 4
                or any(not isinstance(row, list) or len(row) != 4 for row in matrix)):
            raise PipelineError('matrix_world must be a 4x4 matrix')
        from .preservation import finite_tree
        finite_tree(data)
        if (not isinstance(data['resolution'], list) or len(data['resolution']) != 2
                or any(type(v) is not int or v <= 0 for v in data['resolution'])):
            raise PipelineError('resolution must be two positive integers')
        event.update(view=view, metadata=artifact(metadata))
    document['events'].append(event)
    # Explicit mutable ledger; only its own newly-created manifest is updated.
    _update(path, document)


def captures(document, role):
    checkpoint = latest(document, 'checkpoint', role)
    if checkpoint is None:
        raise PipelineError(f'missing {role} checkpoint')
    verify(checkpoint['artifact'])
    check = latest(document, 'check', role)
    if (check is None or check['outcome'] != 'pass'
            or check['checkpoint_sha256'] != checkpoint['artifact']['sha256']):
        return {}
    verify(check['artifact'])
    result = {}
    for event in document['events']:
        if (event['kind'] == 'capture' and event['role'] == role
                and event['checkpoint_sha256'] == checkpoint['artifact']['sha256']):
            verify(event['artifact'])
            verify(event['metadata'])
            result[event['view']] = event
    return result


def status(path, step=None):
    document = load(path)
    budget = document.get('budgets', [])
    if budget:
        if step is not None:
            raise PipelineError('runner budget counts operations automatically; omit --step')
        step = operation_count(document)
    elif type(step) is not int or step < 0:
        raise PipelineError('legacy ledger needs explicit nonnegative --step')
    active = budget[-1] if budget else document
    phase = ('stopped' if step >= active['deadline'] else
             'evidence-only' if step >= active['construction_stop'] else 'construction')
    pending = []
    for role in ('before', 'after'):
        checkpoint = latest(document, 'checkpoint', role)
        if checkpoint is None:
            pending.append(f'{role}: checkpoint')
            continue
        verify(checkpoint['artifact'])
        check = latest(document, 'check', role)
        if (check is None or check['checkpoint_sha256'] != checkpoint['artifact']['sha256']
                or check['outcome'] != 'pass'):
            pending.append(f'{role}: passing check')
        elif check:
            verify(check['artifact'])
        present = captures(document, role)
        pending.extend(f'{role}: capture {view}' for view in document['views'] if view not in present)
    return dict(phase=phase, pending=pending, evidence_complete=not pending,
                continuation=budget[-1]['continuation'] if budget else None,
                budget_unit='runner_operations' if budget else 'legacy_caller_reported_steps',
                used=step, construction_stop=active['construction_stop'], deadline=active['deadline'],
                operations=[e for e in document['events'] if e['kind'] == 'operation'],
                acceptance='unjudged', limits='Runner operations are not agent/model turns; no model-step enforcement.')


def sheet(path, output):
    document = load(path)
    before, after = captures(document, 'before'), captures(document, 'after')
    rows = []
    for view in document['views']:
        if view not in before or view not in after:
            raise PipelineError(f'missing matched capture: {view}')
        a, b = before[view], after[view]
        ma, mb = load(a['metadata']['path']), load(b['metadata']['path'])
        for field in ('camera', 'resolution', 'shading', 'visibility'):
            if ma[field] != mb[field]:
                raise PipelineError(f'unmatched {view}: {field}')
        cells = ''.join('<td><img src="' + html.escape(Path(e['artifact']['path']).as_uri(), quote=True)
                        + '"><p>' + role + ' · ' + e['checkpoint_sha256'][:16] + '</p></td>'
                        for role, e in (('before', a), ('after', b)))
        rows.append('<tr><th colspan="2">' + html.escape(view) + '</th></tr><tr>' + cells + '</tr>')
    with Path(output).open('x', encoding='utf-8') as stream:
        stream.write('<!doctype html><meta charset="utf-8"><title>Matched review</title>'
                     '<style>body{font:16px sans-serif}table{width:100%;table-layout:fixed}'
                     'img{width:100%}td{vertical-align:top}</style><h1>' + html.escape(document['goal'])
                     + '</h1><p>Evidence only — visual review and user acceptance remain unjudged. '
                     'Local linked artifacts; regenerate if artifacts move or change.</p><table>'
                     + ''.join(rows) + '</table>')
