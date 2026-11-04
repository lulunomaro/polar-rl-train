"""Disabled SOURCE preparation; only a parent's independently qualified NEW purpose may supply CONFIG."""
from pathlib import Path, PurePosixPath
import hashlib, json, sys

CONFIG = None
STATUS = 'SOURCE_READY_FOR_PARENT_NEW_PURPOSE_ONLY'
B = PurePosixPath('/home/lc01/Zonglin Li/zonglin2')
MAXIMUM = 64 * 1024 * 1024
ALIASES = {'worker_final': 'cases/E3/FINAL.json', 'group_final': 'FINAL.json'}
PINS = {'typed_capture_consumer.py': (62007, 'fd5d80f9c2ef93bebc20e2411b31291e3d926740ce33a5e3051b51a4db82e46d'),
        'capture_evidence_verifier_v1.py': (41739, '2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979')}
MANIFEST34 = '6de25a76b3d2d5a1fb13f9f80daa1669cf02fb81d602220db6a47a6c3a1ef315'
REQUIRED_LIFE = ('parent_exit_scope', 'source_grade', 'common_go', 'worker_ready', 'worker_started', 'env_close',
                 'app_close_binding', 'parent_dispatch', 'outer_parent_wait', 'controller_started', 'parent_started')

def need(ok, message):
    if not ok: raise ValueError(message)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())
def hexsha(value): return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)

def validate_config(c):
    need(type(c) is dict and c['kind'] == 'PARENT_NEW_TYPED_SCIENCE_CACHE_CONFIG_V1', 'explicit CONFIG required')
    need(c['qualified_closed_execution'] is True and c['new_functional_purpose'] == 'OWN_TYPED_CACHE_SCIENCE_AFTER_CLOSED', 'parent new purpose required')
    for key in ('new_purpose_reference', 'independent_source_qualification_reference'):
        need(type(c[key]) is str and c[key] and not c[key].startswith('UNKNOWN'), 'missing independent parent reference')
    root, analysis = PurePosixPath(c['root']), PurePosixPath(c['analysis_root'])
    need(root.is_absolute() and str(root) == c['root'] and root.parent == B/'tasks' and root.name == c['group_id'], 'fixed own B/tasks group only')
    need(all(x.isascii() and (x.isalnum() or x in '_-') for x in root.name), 'unambiguous group name')
    need(analysis.is_absolute() and str(analysis) == c['analysis_root'] and not analysis.is_relative_to(B/'tasks'), 'separate own analysis root')
    need(PurePosixPath(c['OUTPUT']) == analysis/'TYPED_SCIENCE_CACHE_RESULT_V1.json', 'one fixed own OUTPUT')
    need(c['role'] == 'E3' and type(c['controls']) is int and c['controls'] in (64, 128), 'E3 bounded controls')
    closed, task, life = c['qualified_closed_scope'], c['task'], c['lifecycle']
    need(type(closed) is dict and closed['root'] == str(root) and closed['group_id'] == root.name and closed['passed_closed_capture_execution'] is True, 'whole qualified CLOSED scope required')
    need(task['group_id'] == root.name and task['role'] == 'E3' and type(task['controls']) is int and task['controls'] == c['controls'], 'actual task identity')
    need(type(life) is dict and 'group_final' not in life and all(type(life[k]) is dict for k in REQUIRED_LIFE), 'whole lifecycle excluding group cache required')
    binding = life['app_close_binding']; need(type(binding['fast_shutdown']) is bool, 'actual App binding')
    need(type(life['app_fast_intent' if binding['fast_shutdown'] else 'app_close_returned']) is dict, 'original close receipt missing; no reconstruction')
    scope, outer, grade = life['parent_exit_scope'], life['outer_parent_wait'], life['source_grade']
    need(scope['all_own_children_waited'] is True and scope['original_single_GPU_private_EX_released'] is True and scope['original_global_finite_EX_released'] is True, 'actual child wait and double EX required')
    need(outer['actual_parent_p_wait_returned'] is True and type(outer['returncode']) is int and outer['returncode'] == 0 and grade['passed_closed_capture_execution'] is True, 'actual outer wait/source grade required')
    waits = scope['child_waits']; need(len(waits) == 1 and waits[0]['role'] == 'E3' and waits[0]['actual_waited'] is True and type(waits[0]['returncode']) is int and waits[0]['returncode'] == 0, 'one actual child wait')
    need(scope['errors'] == grade['errors'] == outer['controller_errors'] == [] and closed['errors'] == closed['missing_metadata'] == [], 'qualified closure gaps/errors remain')
    for alias, document in dict(life, task=task).items():
        if document is not None:
            pin = c['provenance']['whole_documents'][alias]
            need(type(pin['original_bytes']) is int and pin['original_bytes'] > 0 and hexsha(pin['original_SHA256']) and pin['decoded_canonical_SHA256'] == canonical(document), 'required whole lifecycle byte claim missing/unknown/different')
    need(set(c['expected_whole_files']) == set(ALIASES), 'exact two originals only')
    for alias, relative in ALIASES.items():
        pin, info = c['expected_whole_files'][alias], c['file_metadata'][relative]
        need(type(pin['bytes']) is int and 0 < pin['bytes'] <= MAXIMUM and hexsha(pin['SHA256']), 'bounded actual original byte identity')
        need(info['status'] == 'READ' and info['whole_JSON_read'] is True and type(info['read_count']) is int and info['read_count'] == 1 and type(info['bytes']) is int and (info['bytes'], info['SHA256']) == (pin['bytes'], pin['SHA256']), 'actual MetadataReader bytes differ')
    rows = sorted(c['actual_source_hashes'], key=lambda row: row['relative'])
    need(len(rows) == 34 and canonical(rows) == MANIFEST34, 'complete actual source identity inputs differ from pinned34')
    need(type(c['provenance']['whole_documents']) is dict, 'whole lifecycle original byte proofs required')
    return root, analysis

def read_once(alias, path, pin, state, digest):
    if alias in state['cache']: return state['cache'][alias]
    count = state['counts'][alias]; need(count['read'] == 0, 'failed original is never retried')
    count['read'] += 1
    with path.open('rb') as stream: raw = stream.read(MAXIMUM + 1)
    need(len(raw) <= MAXIMUM, 'original exceeds fixed64MiB')
    count['hash'] += 1; observed = sha(raw)
    need((len(raw), observed) == (pin['bytes'], pin['SHA256']), 'original bytes differ; no fallback')
    count['decode'] += 1; value = json.loads(raw); need(type(value) is dict, 'whole original mapping required')
    proof = dict(original_bytes=len(raw), original_SHA256=observed, decoded_canonical_SHA256=digest(value))
    state['cache'][alias] = value; state['proof'][alias] = proof
    return value

def module_sources(here):
    result = {}
    for name in tuple(PINS) + (Path(__file__).name,):
        path = here/name; need(path.resolve() == path and not path.is_symlink(), 'own module SOURCE path differs')
        raw = path.read_bytes(); row = dict(bytes=len(raw), SHA256=sha(raw)); result[name] = row
        if name in PINS: need((row['bytes'], row['SHA256']) == PINS[name], 'whole analysis module SOURCE pin differs')
    return result

def main(c=None):
    c = CONFIG if c is None else c  # Runtime CONFIG injection never rewrites frozen SOURCE.
    root0, analysis0 = validate_config(c)  # No original data open before these guards.
    root, here = Path(str(root0)), Path(__file__).resolve().parent
    output = here/'TYPED_SCIENCE_CACHE_RESULT_V1.json'
    need(root.resolve() == root and here == Path(str(analysis0)) and output == Path(c['OUTPUT']) and not output.exists(), 'fixed resolved own roots/output')
    state = dict(cache={}, proof={}, counts={a: dict(read=0, hash=0, decode=0) for a in ALIASES})
    errors, before, after, modules_before, modules_after, application, calls = [], {}, {}, None, None, None, 0
    config_before, phase = canonical(c), 'module_source_before'
    try:
        modules_before = module_sources(here); sys.dont_write_bytecode = True; sys.path.insert(0, str(here))
        need(not any(name in sys.modules for name in ('capture_evidence_verifier_v1', 'typed_capture_consumer')), 'fresh normal whole-module imports required')
        import capture_evidence_verifier_v1 as pure
        import typed_capture_consumer as consumer
        need(Path(pure.__file__).resolve() == here/'capture_evidence_verifier_v1.py' and Path(consumer.__file__).resolve() == here/'typed_capture_consumer.py' and consumer.original is pure, 'normal full module identity')
        for alias, relative in ALIASES.items():
            phase = 'original:' + alias; path = root/relative
            need(path.resolve() == path and not path.is_symlink(), 'exact resolved original path required')
            read_once(alias, path, c['expected_whole_files'][alias], state, pure.digest)
            before[alias] = state['proof'][alias]['decoded_canonical_SHA256']
        worker, group = state['cache']['worker_final'], state['cache']['group_final']
        phase = 'whole_identity_and_provenance'
        need(worker['group_id'] == group['group_id'] == c['group_id'] and worker['role'] == 'E3' and type(worker['controls']) is int and worker['controls'] == c['controls'], 'whole originals differ from qualified identity')
        life = dict(c['lifecycle'], group_final=group); provenance = dict(c['provenance'])
        provenance['whole_documents'] = dict(c['provenance']['whole_documents'])
        for alias, observed in state['proof'].items():
            if alias in provenance['whole_documents']: need(pure.typed_equal(provenance['whole_documents'][alias], observed), 'existing original proof contradiction')
            provenance['whole_documents'][alias] = observed
        for alias, document in dict(life, task=c['task'], worker_final=worker).items():
            if document is not None: need(provenance['whole_documents'][alias]['decoded_canonical_SHA256'] == pure.digest(document), 'whole supplied lifecycle canonical mismatch')
        need(len(group['terminal']) == 1 and pure.typed_equal(group['terminal'][0]['data'], worker), 'whole group terminal differs; projection rejected')
        phase = 'consumer'; calls += 1
        application = consumer.verify_typed_capture(worker, c['task'], life, provenance)
    except Exception as error:
        errors.append(dict(phase=phase, exception_type=type(error).__name__))  # No exception payload/trace export.
    try:
        after = {alias: canonical(value) for alias, value in state['cache'].items()}
        modules_after = module_sources(here) if modules_before is not None else None
        need(not before or before == after, 'whole cache mutated')
        need(modules_before == modules_after and canonical(c) == config_before, 'module SOURCE or CONFIG changed')
        if not errors: need(calls == 1 and all(v == dict(read=1, hash=1, decode=1) for v in state['counts'].values()), 'one read/hash/decode and consumer call required')
    except Exception as error:
        errors.append(dict(phase='after_checks', exception_type=type(error).__name__))
    status = 'FAILED_NO_FALLBACK' if errors else 'CONTRADICTED_NO_REPAIR' if application['status'] == 'CONTRADICTED' else 'APPLIED_NOT_QUALIFICATION'
    result = dict(kind='PARENT_NEW_TYPED_CACHE_SCIENCE_RESULT_V1', source_readiness=STATUS, status=status, errors=errors,
                  root=str(root), group_id=c['group_id'], whole_files=state['proof'], counters=state['counts'], actual_data_reads=sum(x['read'] for x in state['counts'].values()), consumer_calls=calls,
                  canonical_before=before, canonical_after=after, module_SOURCE_before=modules_before, module_SOURCE_after=modules_after,
                  config_canonical_before=config_before, config_canonical_after=canonical(c), application=application,
                  source_identity_inputs='PINNED34_DECLARATIONS_NOT_RUNTIME_AUTHENTICATION_OR_STAGE1_QUALIFICATION', qualified_scope_canonical=canonical(c['qualified_closed_scope']),
                  actual_source_grade_canonical=canonical(c['lifecycle']['source_grade']), raw_worker_group_or_tensor_payload_exported=False,
                  source_grade_external_reference=dict(present='external_settlement_reference' in c['lifecycle']['source_grade'], UNKNOWN=type(c['lifecycle']['source_grade'].get('external_settlement_reference')) is str and c['lifecycle']['source_grade']['external_settlement_reference'].startswith('UNKNOWN')),
                  Gate1='UNKNOWN', Stage2=False, stage2_GO=False, exact=False, capture_interface_passed=False)
    with output.open('x', encoding='utf-8') as stream: stream.write(json.dumps(result, allow_nan=False, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], OUTPUT=str(output), consumer_calls=calls, Gate1='UNKNOWN', Stage2=False)))
    return result

if __name__ == '__main__': main()
