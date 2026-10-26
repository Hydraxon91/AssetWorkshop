"""Fixed, reviewed stage plans; argv subprocesses, never shell strings.

Not a sandbox: reviewed Blender scripts retain the user's OS authority.
One writer per manifest. The runner never accesses interactive Blender.
"""
import os
from pathlib import Path
import signal
import subprocess
import time

from . import review_session as review
from .common import PipelineError, REPO_ROOT


def panel_plan(manifest, blender):
    """Small tested preset, not an asset-authoring recipe or game contract."""
    root = Path(manifest).resolve().parent.relative_to(REPO_ROOT).as_posix()
    def path(name):
        return f'{root}/{name}'
    fixture = 'tools/asset-pipeline/fixtures/review_panel.py'
    helper = 'tools/asset-pipeline/scripts/review_blender.py'
    stages = []
    previous = []
    baseline = path('before_check.json')
    for role in ('before', 'after'):
        work, checkpoint = path(role+'_work.blend'), path(role+'.blend')
        report, image, meta = path(role+'_check.json'), path(role+'.png'), path(role+'_capture.json')
        definitions = [
            ('build', 'construct', path('before.blend') if role == 'after' else None,
             fixture, [role, '--out', work], [work], {}),
            ('save', 'save', work, helper, ['save', '--out', checkpoint], [checkpoint], {'file':checkpoint}),
            ('check', 'check', checkpoint, helper,
             ['check', '--out', report] + (['--baseline', baseline, '--expected-modifier', 'BEVEL'] if role == 'after' else []),
             [report], {'file':report}),
            ('capture', 'capture', checkpoint, helper,
             ['capture','--out',image,'--metadata',meta,'--report',report,'--baseline',baseline],
             [image,meta], {'file':image,'metadata':meta,'view':'three_quarter'})]
        for suffix, kind, source, script, args, outputs, evidence in definitions:
            stage_id = role+'_'+suffix
            stages.append(dict(id=stage_id, kind=kind, role=role, source=source, script=script,
                               args=args, outputs=outputs, requires=previous[:], evidence=evidence))
            previous = [stage_id]
    stages.append(dict(id='sheet', kind='sheet', role='after', source=None, script=None, args=[],
                       outputs=[path('comparison.html')], requires=previous, evidence={}))
    return dict(version=1, goal='Synthetic panel: sharp to rounded edges, matched evidence',
                views=['three_quarter'], construction_stop=5, deadline=12,
                blender=str(Path(blender).resolve()), stages=stages)


def internal(value):
    path = (REPO_ROOT / value).resolve()
    if not path.is_relative_to(REPO_ROOT):
        raise PipelineError('stage paths must remain inside this project')
    return path


def prepare(manifest, plan_file):
    manifest = Path(manifest).resolve()
    if not manifest.is_relative_to(REPO_ROOT / '.dev-shots'):
        raise PipelineError('manifest must be under project .dev-shots')
    plan = review.load(plan_file)
    if set(plan) != {'version', 'goal', 'views', 'construction_stop', 'deadline', 'blender', 'stages'}:
        raise PipelineError('invalid plan fields')
    if plan['version'] != 1 or not Path(plan['blender']).is_file():
        raise PipelineError('need version 1 and an existing explicitly supplied Blender executable')
    stages, seen = [], set()
    for raw in plan['stages']:
        stage = dict(raw)
        if set(stage) != {'id', 'kind', 'role', 'source', 'script', 'args', 'outputs', 'requires', 'evidence'}:
            raise PipelineError('invalid stage fields')
        if stage['id'] in seen or not stage['id'].replace('_', '').isalnum():
            raise PipelineError('stage IDs must be unique simple names')
        if stage['kind'] not in ('construct', 'save', 'check', 'capture', 'sheet'):
            raise PipelineError('unknown stage kind')
        if stage['role'] not in ('before', 'after'):
            raise PipelineError('invalid stage role')
        if not isinstance(stage['args'], list) or any(not isinstance(a, str) for a in stage['args']):
            raise PipelineError('args must be strings passed after Blender --')
        if set(stage['requires']) - seen:
            raise PipelineError('dependencies must refer to preceding stages')
        if not stage['outputs']:
            raise PipelineError('each stage must declare outputs')
        for output in stage['outputs']:
            if not internal(output).is_relative_to(manifest.parent):
                raise PipelineError('outputs must be inside this manifest directory')
        if stage['source']:
            internal(stage['source'])
        if stage['kind'] != 'sheet':
            script = internal(stage['script'])
            if script.suffix != '.py':
                raise PipelineError('Blender stage script must be .py')
            stage['script_artifact'] = review.artifact(script)
        stages.append(stage)
        seen.add(stage['id'])
    if not stages:
        raise PipelineError('empty stage plan')
    review.create(manifest, plan['goal'], plan['construction_stop'], plan['deadline'], plan['views'])
    review.begin_budget(manifest, 'initial', plan['construction_stop'], plan['deadline'], 'Approved initial stage plan')
    document = review.load(manifest)
    document['runner'] = dict(blender=review.artifact(plan['blender']),
                              plan=review.artifact(plan_file), stages=stages)
    review._update(manifest, document)


def completed(document):
    return {e['stage'] for e in document['events'] if e['kind'] == 'operation' and e['state'] == 'complete'}


def status(manifest):
    result = review.status(manifest)
    document = review.load(manifest)
    done = completed(document)
    operations = result.pop('operations')
    result['completed_stages'] = [e['stage'] for e in operations if e['state'] == 'complete']
    result['blocked_operations'] = [e for e in operations if e['state'] != 'complete']
    blocked = any(e['kind'] == 'operation' and e['state'] != 'complete' for e in document['events'])
    result['next'] = [] if blocked else [s['id'] for s in document['runner']['stages']
                                       if s['id'] not in done and set(s['requires']) <= done]
    return result


def command(blender, stage):
    argv = [blender, '--background', '--factory-startup', '--disable-autoexec', '--threads', '2']
    if stage['source']:
        argv.append(str(internal(stage['source'])))
    argv += ['--python-exit-code', '1', '--python', stage['script_artifact']['path'], '--', *stage['args']]
    return argv


def terminate(child):
    if os.name == 'nt':
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(child.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        os.killpg(child.pid, signal.SIGKILL)


def run(manifest, stage_id, timeout=90):
    if not 0 < timeout <= 120:
        raise PipelineError('owned process timeout must be within 0..120 seconds')
    document = review.load(manifest)
    runner = document['runner']
    review.verify(runner['plan'])
    review.verify(runner['blender'])
    matches = [s for s in runner['stages'] if s['id'] == stage_id]
    if not matches:
        raise PipelineError('stage not in reviewed plan')
    stage = matches[0]
    if stage_id in completed(document):
        raise PipelineError('stage already complete; resume next pending stage, do not rerun')
    if not set(stage['requires']) <= completed(document):
        raise PipelineError('stage dependencies incomplete')
    # Revalidate recorded outputs of dependencies before trusting completed flags.
    for event in document['events']:
        if event['kind'] == 'operation' and event['state'] == 'complete':
            for item in event.get('outputs', []):
                review.verify(item)
    if any(internal(p).exists() for p in stage['outputs']):
        raise PipelineError('output exists: reconcile partial state, never overwrite or retry blind')
    if stage['source'] and not internal(stage['source']).is_file():
        raise PipelineError('input checkpoint/work scene missing')
    if stage['kind'] != 'sheet':
        review.verify(stage['script_artifact'])
    count = review.start_operation(manifest, stage_id, stage['kind'] == 'construct')
    logdir = Path(manifest).resolve().parent / 'logs'
    logdir.mkdir(exist_ok=True)
    log = logdir / f'{stage_id}.log'
    started = time.monotonic()
    details = {}
    try:
        if stage['source']:
            details['source'] = review.artifact(internal(stage['source']))
        if stage['kind'] == 'sheet':
            review.sheet(manifest, internal(stage['outputs'][0]))
        else:
            argv = command(runner['blender']['path'], stage)
            details['command'] = argv
            with log.open('xb') as stream:
                child = subprocess.Popen(argv, cwd=REPO_ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                         start_new_session=True)
                details['owned_pid'] = child.pid
                try:
                    child.wait(timeout=timeout)
                except BaseException:
                    # Only the process tree launched by this command; not interactive Blender.
                    if child.poll() is None:
                        terminate(child)
                        child.wait(timeout=15)
                    raise
                details['exit_code'] = child.returncode
                if child.returncode != 0:
                    raise PipelineError(f'Blender exited {child.returncode}; inspect {log}, do not retry')
            if stage['source']:
                review.verify(details['source'])
        outputs = [review.artifact(internal(p)) for p in stage['outputs']]
        evidence = stage['evidence']
        if stage['kind'] == 'check':
            report = review.load(internal(evidence['file']))
            checkpoint = review.latest(review.load(manifest), 'checkpoint', stage['role'])
            if (report.get('status') != 'pass' or checkpoint is None
                    or report.get('blend_sha256') != checkpoint['artifact']['sha256']):
                raise PipelineError('check failed or identifies different checkpoint bytes')
        review.finish_operation(manifest, stage_id, True, outputs=outputs,
                                seconds=time.monotonic()-started, **details)
        if stage['kind'] in ('save', 'check', 'capture'):
            review.record(manifest, {'save':'checkpoint','check':'check','capture':'capture'}[stage['kind']],
                          stage['role'], internal(evidence['file']), count,
                          outcome='pass' if stage['kind'] == 'check' else None,
                          view=evidence.get('view'),
                          metadata=internal(evidence['metadata']) if evidence.get('metadata') else None)
        return status(manifest)
    except BaseException as exc:
        # Completion and evidence registration are distinct. Preserve any partial output.
        current = review.load(manifest)
        event = next(e for e in reversed(current['events']) if e['kind'] == 'operation' and e['stage'] == stage_id)
        event.update(state='failed', error=str(exc), seconds=time.monotonic()-started, **details)
        review._update(manifest, current)
        raise
