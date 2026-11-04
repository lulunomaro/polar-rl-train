"""SOURCE derivation only. Read fixed text/JSON inputs, write NEW CLI or verify equality; never prepare/stage."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parent.parent
R=HERE.parent
T=WORKSPACE/'mod4v1_experts_fulldr_rm70_20261101'
OLD=R/'source_stage_good_expert_holdout_v1/stage_good_expert_holdout_v1.py'
INDEX=R/'source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json'
PLAN=T/'reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json'
SUPERVISOR=T/'NINE_N80_PARALLEL_SOURCE_V8/single_gpu_group_supervisor.py'
OLD_PIN=(38828,'fc9dd74437258d408e0223359b45814909b5a9a2f80df450dfdea1f546290a2f')
PLAN_PIN=(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0')
SUPERVISOR_PIN=(9247,'7c826b983887cb9ec890c92737095c5e7e7d93538fafaa211021fea2e0d9fc27')
H=lambda raw:hashlib.sha256(raw).hexdigest()

def canonical(value):
    return H(json.dumps(value,sort_keys=True,separators=(',',':')).encode())

def replace_once(text,old,new):
    assert text.count(old)==1,('derive exact substitution count differs',old[:100])
    return text.replace(old,new,1)

def main():
    raw=OLD.read_bytes();assert (len(raw),H(raw))==OLD_PIN
    original=raw.decode();text=original
    plan_raw=PLAN.read_bytes();assert (len(plan_raw),H(plan_raw))==PLAN_PIN
    plan=json.loads(plan_raw);index=json.loads(INDEX.read_bytes())
    extra=SUPERVISOR.read_bytes();assert (len(extra),H(extra))==SUPERVISOR_PIN
    expected={r['relative']:(r['bytes'],r['SHA256']) for r in index['inherited_original_worker_source_entries']}
    expected.update({r['relative']:(r['bytes'],r['SHA']) for r in index['required_original_pinned_assets']})
    assert len(expected)==26
    expected['single_gpu_group_supervisor.py']=SUPERVISOR_PIN
    actual={r['relative']:(r['bytes'],r['SHA']) for r in plan['worker_files']}
    assert len(plan['worker_files'])==27 and actual==expected
    dependency_rows=[dict(relative=rel,bytes=n,SHA=sha) for rel,(n,sha) in sorted(expected.items())]
    text=replace_once(text,'"""Good-expert holdout stdlib ONLY:',
        '"""V2 fixed original27 + independently retained bytes. Good-expert holdout stdlib ONLY:')
    additions=("\nSOURCE_DERIVATION_VERSION = 2\n"
        +"ORIGINAL_PLAN_PIN = "+repr(PLAN_PIN)+"\n"
        +"EXTRA_ORIGINAL_DEPENDENCY = "+repr(dict(relative='single_gpu_group_supervisor.py',bytes=SUPERVISOR_PIN[0],SHA=SUPERVISOR_PIN[1]))+"\n"
        +"ORIGINAL_DEPENDENCY_SHA = "+repr(canonical(dependency_rows))+"\n"
        +"RETAIN_PREFIX = 'worker_sources/good_holdout_retained_original/'\n"
        +"ORIGINAL_PRESERVATION_NAME = 'RETAINED_ORIGINAL_STATIC_FILES_GOOD_EXPERT_HOLDOUT_V2.json'\n")
    text=replace_once(text,"APP_CLOSE_PIN = (27769, '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39')\n",
        "APP_CLOSE_PIN = (27769, '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39')\n"+additions)
    helpers='''def preservation_digest(value):
    return H(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def original_dependency_map(old_files, index):
    """Exactly the published 27, not acceptance of an arbitrary extra source."""
    expected = {r['relative']:(r['bytes'],r['SHA256']) for r in index['inherited_original_worker_source_entries']}
    expected.update({r['relative']:(r['bytes'],r['SHA']) for r in index['required_original_pinned_assets']})
    need(len(expected) == 26 and EXTRA_ORIGINAL_DEPENDENCY['relative'] not in expected,
         'fixed prior26 source-index dependency set differs')
    extra = EXTRA_ORIGINAL_DEPENDENCY
    expected[extra['relative']] = (extra['bytes'],extra['SHA'])
    rows = [dict(relative=rel,bytes=n,SHA=sha) for rel,(n,sha) in sorted(expected.items())]
    need(len(expected) == 27 and preservation_digest(rows) == ORIGINAL_DEPENDENCY_SHA,
         'fixed complete original27 dependency provenance differs')
    need(type(old_files) is list and len(old_files) == 27
         and len({r['relative'] for r in old_files}) == 27
         and {r['relative'] for r in old_files} == set(expected),
         'complete original27 worker_files dependency set differs')
    for row in old_files:
        rel = safe_relative(row['relative'])
        need((row['bytes'],row['SHA']) == expected[rel], 'original27 dependency pin differs: ' + rel)
    return expected


def retain_originals(originals, sources, *, original_root, original_plan_SHA, native_root, required):
    """Keep the whole independently read input inventory; relocate only actual byte conflicts."""
    materials = dict(originals); moves = {}; origin = []; baseline = []
    for rel,(path,info) in sorted(originals.items()):
        safe_relative(rel); alias = rel
        if rel in sources and sources[rel][1] != info:
            alias = RETAIN_PREFIX + rel
            need(alias not in originals and alias not in sources and alias not in materials,
                 'retained original alias collides: ' + alias)
            materials[alias] = (path,info); moves[rel] = alias
        origin.append(dict(relative=rel,bytes=info['bytes'],SHA=info['SHA'],input_path=str(path),bytes_read=info['bytes']))
        baseline.append(dict(relative=alias,bytes=info['bytes'],SHA=info['SHA']))
    materials.update(sources); baseline.sort(key=lambda r:r['relative'])
    logical = [{k:r[k] for k in ('relative','bytes','SHA')} for r in origin]
    inventory = dict(kind='GOOD_HOLDOUT_INDEPENDENT_ORIGINAL_STATIC_PRESERVATION_V2',
        baseline=baseline,installed=copy.deepcopy(baseline),baseline_SHA=preservation_digest(baseline),
        installed_status='PLANNED_HASH_IDENTITIES_NOT_ACTUAL_MATERIALIZATION',vendor7_SHA=VENDOR_PIN[1],
        baseline_provenance=dict(kind='INDEPENDENT_COMPLETE_SELECTED_INPUT_TREE_BYTE_INVENTORY_V2',
            original_root=str(original_root),original_plan_SHA=original_plan_SHA,native_root=str(native_root),
            original_logical_rows=origin,original_logical_tree_SHA=preservation_digest(logical),
            source_to_retained=moves,all_original_input_files_read=len(origin),
            operational_raw_model_names_excluded_before_classification=True))
    validate_preservation(inventory,materials,originals=originals,required=required)
    return materials,inventory


def validate_preservation(inventory, materials, *, originals, required, observed=None):
    """Bind independent input paths/hash inventory and actual stream hashes, not two asserted lists."""
    proof = inventory['baseline_provenance']; origin = proof['original_logical_rows']; moves = proof['source_to_retained']
    need(origin and len({r['relative'] for r in origin}) == len(origin), 'unique full original input inventory required')
    logical = [{k:r[k] for k in ('relative','bytes','SHA')} for r in origin]
    actual = [dict(relative=rel,**info) for rel,(_,info) in sorted(originals.items())]
    need(logical == sorted(logical,key=lambda r:r['relative']) and logical == actual
         and preservation_digest(logical) == proof['original_logical_tree_SHA'],
         'provenance is not the complete independently read input tree')
    need(all(r['input_path'] == str(originals[r['relative']][0]) and r['bytes_read'] == r['bytes'] for r in origin),
         'actual original input path/read-byte provenance differs')
    need(proof['all_original_input_files_read'] == len(origin) and set(moves) <= set(originals),
         'original input/relocation domain differs')
    for rel,(n,sha) in required.items():
        need(rel in originals and originals[rel][1] == dict(bytes=n,SHA=sha),
             'required original dependency missing/changed in independent input: ' + rel)
    expected = []
    for row in origin:
        old = safe_relative(row['relative']); alias = moves.get(old,old)
        if old in moves: need(alias == RETAIN_PREFIX + old, 'only exact retained-original namespace permitted')
        need(materials.get(alias,(None,None))[1] == dict(bytes=row['bytes'],SHA=row['SHA']),
             'original byte lost/changed under retained alias: ' + alias)
        expected.append(dict(relative=alias,bytes=row['bytes'],SHA=row['SHA']))
    expected.sort(key=lambda r:r['relative'])
    need(len({r['relative'] for r in expected}) == len(expected) and inventory['baseline'] == expected,
         'retained original baseline is incomplete or duplicates')
    if observed is None:
        installed = expected
    else:
        need(all(r['relative'] in observed for r in expected), 'actual installed stream dropped original bytes')
        installed = [dict(relative=r['relative'],**observed[r['relative']]) for r in expected]
    need(inventory['installed'] == installed == expected and inventory['baseline_SHA'] == preservation_digest(expected),
         'actual installed retained bytes differ from independent original baseline')
    need(all(any(r['relative'].startswith('runtimes/'+role+'/') for r in logical) for role in REQUESTED),
         'both complete selected original runtime inventories required')
    need(any(r['relative'].startswith('pinned_assets/') for r in logical)
         and any(r['relative'].startswith('worker_sources/') for r in logical), 'original asset/worker trees required')
    need(len([r for r in logical if r['relative'].startswith('supermimic_vendor_v2/')]) == 7
         and inventory['vendor7_SHA'] == VENDOR_PIN[1], 'full original vendor7 preservation required')
    return True


def preservation_summary(inventory):
    proof = inventory['baseline_provenance']
    return dict(kind=inventory['kind'],original_static_files=len(inventory['baseline']),
        original_dependency_files=27,baseline_SHA=inventory['baseline_SHA'],
        original_logical_tree_SHA=proof['original_logical_tree_SHA'],
        source_to_retained=proof['source_to_retained'],installed_status=inventory['installed_status'],
        independent_origin_paths_and_read_bytes=True,actual_native_binding='UNKNOWN')


'''
    text=replace_once(text,'def prepare(original_group_root, source_dir, source_index, native_root, new_root, group_id, gpu_uuid, seed):',
        helpers+'def prepare(original_group_root, source_dir, source_index, native_root, new_root, group_id, gpu_uuid, seed):')
    text=replace_once(text,"    old, old_raw = metadata(original_group_root / 'GROUP_PLAN.json')\n",
        "    old, old_raw = metadata(original_group_root / 'GROUP_PLAN.json')\n"
        "    need((len(old_raw), H(old_raw)) == ORIGINAL_PLAN_PIN, 'fixed published original GROUP_PLAN bytes differ')\n")
    text=replace_once(text,"    expected = {r['relative']:(r['bytes'],r['SHA256']) for r in index['inherited_original_worker_source_entries']}\n"
        "    expected.update({r['relative']:(r['bytes'],r['SHA']) for r in index['required_original_pinned_assets']})\n"
        "    old_files = old.get('worker_files')\n"
        "    need(type(old_files) is list and len(old_files) == len(expected)\n"
        "         and {r['relative'] for r in old_files} == set(expected), 'complete original worker_files dependency set differs')\n",
        "    old_files = old.get('worker_files')\n    expected = original_dependency_map(old_files, index)\n")
    text=replace_once(text,"    for rel,value in sources.items():\n"
        "        if rel.startswith('supermimic_vendor_v2/'): need(materials[rel][1] == value[1], 'vendor/index source mismatch')\n"
        "        materials[rel] = value\n",
        "    originals = dict(materials)\n    for rel,value in sources.items():\n"
        "        if rel.startswith('supermimic_vendor_v2/'): need(materials[rel][1] == value[1], 'vendor/index source mismatch')\n"
        "    materials, original_preservation = retain_originals(originals, sources, original_root=original_group_root,\n"
        "        original_plan_SHA=H(old_raw), native_root=native_root, required=expected)\n")
    text=replace_once(text,"    verify_aliases = {r['relative'] for r in old_files} | ALIASES | {'supermimic_vendor_v2/' + r for r in vendor}\n",
        "    verify_aliases = ({r['relative'] for r in old_files} | ALIASES | {'supermimic_vendor_v2/' + r for r in vendor}\n"
        "        | set(original_preservation['baseline_provenance']['source_to_retained'].values()))\n")
    text=replace_once(text,"    prepared = dict(plan=plan,materials=materials,boundary=boundary,source_index=index_receipt,original_plan_SHA=H(old_raw),\n",
        "    prepared = dict(plan=plan,materials=materials,originals=originals,original_dependency_files=expected,\n"
        "        original_preservation=original_preservation,boundary=boundary,source_index=index_receipt,original_plan_SHA=H(old_raw),\n")
    text=replace_once(text,"kind='SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V1',passed=True,",
        "kind='SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V2',passed=True,\n"
        "        source_derivation_version=2,original_preservation=preservation_summary(prepared['original_preservation']),")
    text=replace_once(text,"            need(dict(bytes=count,SHA=digest.hexdigest())==info,'source changed after preflight: '+rel)\n"
        "            rows.append(dict(relative=rel,**info))\n",
        "            observed=dict(bytes=count,SHA=digest.hexdigest())\n"
        "            need(observed==info,'source changed after preflight: '+rel)\n"
        "            rows.append(dict(relative=rel,**observed))\n"
        "        written={r['relative']:{k:r[k] for k in ('bytes','SHA')} for r in rows}\n"
        "        preservation=copy.deepcopy(prepared['original_preservation'])\n"
        "        preservation['installed']=[dict(relative=r['relative'],**written[r['relative']]) for r in preservation['baseline']]\n"
        "        preservation['installed_status']='ACTUAL_STREAM_HASH_VERIFIED_STATIC_FILES'\n"
        "        validate_preservation(preservation,prepared['materials'],originals=prepared['originals'],\n"
        "            required=prepared['original_dependency_files'],observed=written)\n"
        "        preservation_raw=(json.dumps(preservation,indent=2,allow_nan=False)+'\\n').encode()\n"
        "        need(len(preservation_raw)<=8*1024*1024,'independent static preservation metadata exceeds8MiB')\n"
        "        put_once(root/ORIGINAL_PRESERVATION_NAME,preservation_raw)\n")
    text=replace_once(text,"receipt=dict(kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V1',materialized=True,",
        "receipt=dict(kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V2',materialized=True,\n"
        "            source_derivation_version=2,original_preservation=preservation_summary(preservation),\n"
        "            original_preservation_file=dict(relative=ORIGINAL_PRESERVATION_NAME,bytes=len(preservation_raw),SHA=H(preservation_raw)),")
    old_functions={n.name:n for n in ast.parse(original).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    new_functions={n.name:n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    changed={n for n in old_functions if ast.dump(old_functions[n],include_attributes=False)!=ast.dump(new_functions[n],include_attributes=False)}
    assert changed=={'prepare','preflight_summary','stage'},changed
    assert set(new_functions)-set(old_functions)=={'preservation_digest','original_dependency_map','retain_originals','validate_preservation','preservation_summary'}
    target=HERE/'stage_good_expert_holdout_v2.py';data=text.encode()
    if target.exists():assert target.read_bytes()==data,'NEW derived entry differs; no overwrite'
    else:
        with target.open('xb')as stream:stream.write(data)
    print(json.dumps(dict(kind='GOOD_HOLDOUT_V2_NARROW_SOURCE_DERIVED',entry=target.name,bytes=len(data),SHA256=H(data),
        original_dependency_count=27,changed_functions=sorted(changed),unchanged_functions=len(old_functions)-len(changed),
        prepare_preflight_stage_dispatch_executed=False),indent=2))

if __name__=='__main__':main()
