"""Strict, stdlib-only authored-representation comparison (not appearance proof)."""
import hashlib
import json
import math
import re

from .common import PipelineError

FIELDS = ('geometry', 'uv', 'transforms', 'materials', 'images')
LIMITS = [
    'Exact representation inequality is not proof of visual shape corruption; reindexing can differ.',
    'No evaluated equivalence, appearance, clearance, collision or user approval is established.',
    'Shape keys, modifiers, animation and procedural dependencies require separate verification.',
]


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise PipelineError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    try:
        return json.loads(text, object_pairs_hook=pairs,
                          parse_constant=lambda x: (_ for _ in ()).throw(PipelineError(x)))
    except (ValueError, TypeError) as exc:
        raise PipelineError(str(exc)) from exc


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def keys(value, required, optional=()):
    if not isinstance(value, dict) or set(value) - set(required) - set(optional) or set(required) - set(value):
        raise PipelineError('invalid keys; required=' + str(required))


def number(value, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise PipelineError('expected finite nonnegative number')
    if integer and not isinstance(value, int):
        raise PipelineError('expected integer')


def names(value, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value) or any(not isinstance(x, str) or not x.strip() for x in value) or len(set(value)) != len(value):
        raise PipelineError('expected unique names')


def finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise PipelineError('nonfinite value')
    if isinstance(value, dict):
        for child in value.values():
            finite_tree(child)
    elif isinstance(value, list):
        for child in value:
            finite_tree(child)


def validate_snapshot(snapshot):
    keys(snapshot, ('version', 'context', 'objects', 'cost', 'limits'))
    if type(snapshot['version']) is not int or snapshot['version'] != 1:
        raise PipelineError('unsupported snapshot version')
    keys(snapshot['context'], ('frame', 'view_layer', 'source_path'))
    if type(snapshot['context']['frame']) is not int or not isinstance(snapshot['context']['view_layer'], str) or not snapshot['context']['view_layer'] or not isinstance(snapshot['context']['source_path'], str):
        raise PipelineError('invalid context')
    if not isinstance(snapshot['objects'], dict) or not snapshot['objects']:
        raise PipelineError('empty objects')
    names(list(snapshot['objects']), True)
    for obj in snapshot['objects'].values():
        keys(obj, ('counts', 'fields'))
        keys(obj['counts'], ('vertices', 'edges', 'polygons', 'triangles'))
        for n in obj['counts'].values():
            number(n, True)
        keys(obj['fields'], FIELDS)
        for field in obj['fields'].values():
            keys(field, ('status', 'hash', 'issues'), ('components',))
            if field['status'] not in ('ok', 'unsupported') or not isinstance(field['issues'], list) or any(not isinstance(x, str) for x in field['issues']):
                raise PipelineError('invalid field status')
            if not isinstance(field['hash'], str) or not re.fullmatch('[0-9a-f]{64}', field['hash']):
                raise PipelineError('missing/invalid field hash')
            if field['status'] == 'ok' and field['issues']:
                raise PipelineError('ok field has unresolved issues')
            if 'components' in field:
                if not isinstance(field['components'], dict) or not field['components'] or any(not isinstance(k, str) or not isinstance(v, str) or not re.fullmatch('[0-9a-f]{64}', v) for k, v in field['components'].items()):
                    raise PipelineError('invalid component hashes')
    cost = snapshot['cost']
    keys(cost, ('status', 'errors', 'limits'), ('authored_unique_meshes', 'authored_unique_triangles',
         'authored_per_object', 'authored_object_triangles', 'unique_materials', 'material_node_counts',
         'viewport', 'images', 'unique_image_datablocks', 'packed_unique_content_bytes',
         'packed_unique_content_count', 'rgba8_base_level_estimate_bytes'))
    if cost['status'] not in ('ok', 'limited', 'error', 'not_requested') or not isinstance(cost['errors'], list) or any(not isinstance(x, str) for x in cost['errors']):
        raise PipelineError('invalid cost status')
    if cost['errors'] and cost['status'] != 'error':
        raise PipelineError('cost errors cannot be successful')
    if not isinstance(cost['limits'], list) or any(not isinstance(x, str) for x in cost['limits']):
        raise PipelineError('invalid cost limits')
    if cost['status'] != 'not_requested':
        required_cost = ('authored_unique_meshes', 'authored_unique_triangles', 'authored_per_object',
                         'authored_object_triangles', 'unique_materials', 'material_node_counts',
                         'viewport', 'images', 'unique_image_datablocks', 'packed_unique_content_bytes',
                         'packed_unique_content_count', 'rgba8_base_level_estimate_bytes')
        if set(required_cost) - set(cost):
            raise PipelineError('incomplete cost report')
        for key in required_cost:
            if key not in ('authored_per_object', 'material_node_counts', 'viewport', 'images'):
                number(cost[key], True)
        keys(cost['viewport'], ('linked_instances', 'direct_objects', 'triangles'))
        for value in cost['viewport'].values():
            number(value, True)
        if not isinstance(cost['images'], list) or not isinstance(cost['authored_per_object'], dict) or not isinstance(cost['material_node_counts'], dict):
            raise PipelineError('invalid cost inventory')
    if not isinstance(snapshot['limits'], list) or any(not isinstance(x, str) for x in snapshot['limits']):
        raise PipelineError('invalid cost/limits')
    finite_tree(snapshot)
    return snapshot


def validate_policy(policy):
    keys(policy, ('version', 'objects'), ('mapping', 'allow_new', 'allow_missing'))
    if type(policy['version']) is not int or policy['version'] != 1 or not isinstance(policy['objects'], dict):
        raise PipelineError('unsupported policy')
    mapping = policy.get('mapping', {})
    if not isinstance(mapping, dict):
        raise PipelineError('mapping must be object')
    names(list(mapping))
    names(list(mapping.values()))
    for key in ('allow_new', 'allow_missing'):
        names(policy.get(key, []))
    names(list(policy['objects']))
    for rule in policy['objects'].values():
        keys(rule, ('preserve',), ('require_changes', 'triangle_ratio'))
        names(rule['preserve'], True)
        names(rule.get('require_changes', []))
        if (set(rule['preserve']) | set(rule.get('require_changes', []))) - set(FIELDS) or set(rule['preserve']) & set(rule.get('require_changes', [])):
            raise PipelineError('unknown/conflicting fields')
        if 'triangle_ratio' in rule:
            keys(rule['triangle_ratio'], ('ratio', 'tolerance'))
            for n in rule['triangle_ratio'].values():
                number(n)
    return policy


def compare(before, after, policy):
    validate_snapshot(before)
    validate_snapshot(after)
    validate_policy(policy)
    source, target = before['objects'], after['objects']
    mapping = {name: policy.get('mapping', {}).get(name, name) for name in source}
    if set(policy['objects']) - set(source) or set(policy.get('mapping', {})) - set(source):
        raise PipelineError('policy names unknown source object')
    if len(set(mapping.values())) != len(mapping):
        raise PipelineError('mapping is not one-to-one')
    if set(policy.get('allow_missing', [])) - set(source) or set(policy.get('allow_new', [])) & set(mapping.values()):
        raise PipelineError('invalid object exception')
    checks = []
    def record(code, obj, field, expected, actual, passed):
        checks.append(dict(code=code, object=obj, field=field, expected=expected, actual=actual,
                           status='pass' if passed else 'fail'))
    record('CONTEXT', None, 'context', {k: before['context'][k] for k in ('frame', 'view_layer')},
           {k: after['context'][k] for k in ('frame', 'view_layer')},
           all(before['context'][k] == after['context'][k] for k in ('frame', 'view_layer')))
    for label, snapshot in (('source', before), ('target', after)):
        record('COST_EVALUATION', label, 'cost', 'no evaluation errors', snapshot['cost']['errors'],
               snapshot['cost']['status'] != 'error')
    for name in sorted(set(target) - set(mapping.values())):
        record('NEW_OBJECT', name, None, 'explicitly allowed', name, name in policy.get('allow_new', []))
    for name, dest in mapping.items():
        if dest not in target:
            record('MISSING_OBJECT', name, None, dest, None, name in policy.get('allow_missing', []))
            continue
        rule = policy['objects'].get(name, {'preserve': list(FIELDS)})
        for field in FIELDS:
            a, b = source[name]['fields'][field], target[dest]['fields'][field]
            if field not in rule['preserve'] and field not in rule.get('require_changes', []):
                continue
            supported = a['status'] == b['status'] == 'ok'
            changed = field in rule.get('require_changes', [])
            record('UNSUPPORTED' if not supported else ('REQUIRED_CHANGE' if changed else 'EXACT_REPRESENTATION'),
                   name, field, a, b, supported and ((a['hash'] != b['hash']) if changed else (a['hash'] == b['hash'])))
        if 'triangle_ratio' in rule:
            a, b = source[name]['counts']['triangles'], target[dest]['counts']['triangles']
            ratio = b / a if a else None
            r = rule['triangle_ratio']
            record('TRIANGLE_RATIO', name, 'triangles', r, ratio,
                   ratio is not None and abs(ratio - r['ratio']) <= r['tolerance'])
    return dict(version=1, status='pass' if all(c['status'] == 'pass' for c in checks) else 'fail',
                checks=checks, counts={'source': {n: o['counts'] for n, o in source.items()},
                                       'target': {n: o['counts'] for n, o in target.items()}},
                cost={'source': before['cost'], 'target': after['cost']}, warnings=list(LIMITS),
                downstream='unverified')
