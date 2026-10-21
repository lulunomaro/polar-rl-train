from pathlib import Path
import ast, hashlib, json, struct, time

B = Path(__file__).resolve().parent
R = B / 'reports'
H = lambda b: hashlib.sha256(b).hexdigest()

def put(p, value):
    with p.open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

report = R / 'STEP270_COOKED_QUERY_V4_SOURCE_AST_PREPARED_ACTUAL.json'
assert not report.exists()
previous = json.loads((R / 'STEP270_COOKED_QUERY_V3_SOURCE_AST_PREPARED_ACTUAL.json').read_bytes())
returned = json.loads((R / 'STEP270_COOKED_QUERY_V3_FINITE_RETURNED_ACTUAL.json').read_bytes())
assert not returned['pending'] and returned['parent_exit']['all_own_children_waited'] and returned['parent_exit']['own_eval_lease_released']
error = json.loads((B / 'cooked_query_V3_actual/out/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').read_bytes())
assert 'Object of type float32 is not JSON serializable' in error['error']
assert (B / 'cooked_query_V3_actual/out/ORIGINAL_MISSING_QUERY_RAW_DIAGNOSTIC.json').stat().st_size == 0
old = (B / 'step270_cooked_PhysX_query_audit_worker_v3_raw_diagnostic.py').read_text(encoding='utf8')
before = "origin=list(origin),direction=list(direction),distance=distance,raycast_all_return=str(returned)"
after = "origin=[float(x) for x in origin],direction=[float(x) for x in direction],distance=float(distance),raycast_all_return=str(returned)"
assert old.count(before) == 1
new = old.replace('H1_step270_cooked_PhysX_queries_v3_diagnostic', 'H1_step270_cooked_PhysX_queries_v4_diagnostic').replace(before, after)
ast.parse(new)
assert ast.dump(ast.parse(new.replace('H1_step270_cooked_PhysX_queries_v4_diagnostic', 'H1_step270_cooked_PhysX_queries_v3_diagnostic').replace(after, before))) == ast.dump(ast.parse(old))
worker = B / 'step270_cooked_PhysX_query_audit_worker_v4_JSON_diagnostic.py'
with worker.open('x', encoding='utf8', newline='\n') as f:
    f.write(new)
payload = B / 'H1_step270_cooked_query_V4_diagnostic_delta'
payload.mkdir()
(payload / 'worker.py').write_bytes(worker.read_bytes())
cfg = json.loads((Path(previous['payload']) / 'FROZEN_CONFIG.json').read_bytes())
cfg['kind'] = 'H1_step270_cooked_PhysX_queries_v4_diagnostic'
put(payload / 'FROZEN_CONFIG.json', cfg)
manifest = json.loads((Path(previous['payload']) / 'SOURCE_MANIFEST.json').read_bytes())
for row in manifest['files']:
    if row['relative'] in ('worker.py', 'FROZEN_CONFIG.json'):
        data = (payload / row['relative']).read_bytes()
        row.update(bytes=len(data), SHA=H(data))
put(payload / 'SOURCE_MANIFEST.json', manifest)
workflows = []
for source, target in (
    ('deploy_step270_cooked_query_V3_unused_root_once.py', 'deploy_step270_cooked_query_V4_unused_root_once.py'),
    ('collect_step270_cooked_query_V3_bounded_once.py', 'collect_step270_cooked_query_V4_bounded_once.py'),
):
    text = (B / source).read_text(encoding='utf8').replace('COOKED_QUERY_V3', 'COOKED_QUERY_V4').replace('cookedquery_2110v3', 'cookedquery_2110v4').replace('cooked_query_V3_actual', 'cooked_query_V4_actual')
    ast.parse(text)
    p = B / target
    with p.open('x', encoding='utf8', newline='\n') as f:
        f.write(text)
    workflows.append(dict(path=str(p), bytes=p.stat().st_size, SHA=H(p.read_bytes()), unused=True))
points = [struct.unpack('f', struct.pack('f', x))[0] for x in (0, .349, .351, 1.5)]
diag = dict(origin=[float(x) for x in points[:3]], direction=[float(x) for x in (0, 0, -1)], distance=float(points[-1]))
assert json.loads(json.dumps(diag)) == diag
put(report, dict(epoch=time.time(), passed_source_AST_only=True, source_SHA=previous['source_SHA'], payload=str(payload), zip=previous['zip'], worker=dict(path=str(worker), bytes=worker.stat().st_size, SHA=H(worker.read_bytes())), workflows=workflows, only_worker_changes=['version kind', 'diagnostic origin/direction/distance explicitly converted to built-in float'], normalized_rest_AST_exact=True, diagnostic_JSON_numeric_roundtrip_CPU=True, original_V3_error_and_empty_diagnostic_retained=True, actual_cooked_query_not_yet_passed=True, not_installed_or_executed=True, no_PPO_or_learning_GO=True, query_filter_and_1um_guard_unchanged=True))
print(json.dumps(dict(prepared_source_AST=True, unused_workflows=workflows, no_GPU_or_transport=True)))
