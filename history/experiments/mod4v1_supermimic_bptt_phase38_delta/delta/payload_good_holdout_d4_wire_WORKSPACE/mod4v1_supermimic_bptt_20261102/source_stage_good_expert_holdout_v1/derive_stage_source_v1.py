"""Derive one NEW stdlib-only CLI from the complete reviewed embedded16 stager.
Original files and sealed holdout V1 are read-only. No materializer is invoked.
"""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
R = HERE.parent
OLD = R / 'source_frozen_embedded_teacher_native_v1/stage_embedded_teacher_native_v1.py'
SEALED = R / 'source_good_expert_holdout_subset_v1'


def replace(text, old, new):
    assert text.count(old) == 1, (old[:80], text.count(old))
    return text.replace(old, new)


def block(text, start, end, new):
    a = text.index('def ' + start + '('); b = text.index('def ' + end + '(', a)
    return text[:a] + new.strip() + '\n\n\n' + text[b:]


def main():
    original = OLD.read_text(encoding='utf-8')
    index_raw = (SEALED / 'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json').read_bytes()
    assert (len(index_raw), hashlib.sha256(index_raw).hexdigest()) == (21075, '6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e')
    index = json.loads(index_raw)
    text = original
    text = replace(text, 'Teacher-reference stdlib ONLY: sixteen complete mappings and original static plant; one NEW stage, NEVER dispatch.', 'Good-expert holdout stdlib ONLY: twenty complete pinned mappings and full selected original static trees; NEVER dispatch.')
    text = replace(text, 'The only evaluator invocation is full pinned --validate-plan under metadata I/O guards.', 'Full unchanged metadata modules are imported under model/budget/native guards; make_task and seed negatives are checked. No parent/worker main is called.')
    text = replace(text, 'import runpy\n', 'import tempfile\n')
    text = replace(text, "REQUESTED = ('E3', 'W35')", "REQUESTED = ('CURB_PROTECTED878', 'SLOPE135')\nALLOWED_SEEDS = (20260929, 20260930)\nSOURCE_NATIVE_ENABLED = SOURCE_STAGED = SOURCE_DISPATCHED = False\nCOMPLETE_NAME = 'STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json'")
    text = replace(text, "INDEX_PIN = (5685, 'cfedd40d5c70d61a5a32e10861c3af3b6da16cab86c23306053eeccb650c5205')", "INDEX_PIN = (21075, '6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e')")
    start = text.index('ALIASES = '); end = text.index('\nMODEL_SUFFIXES =', start)
    text = text[:start] + 'ALIASES = frozenset(' + repr(tuple(sorted(row['relative'] for row in index['overlay_entries']))) + ')' + text[end:]
    text = block(text, 'source_mappings', 'semantic_success', '''
def source_mappings(source_dir, source_index):
    index, raw = metadata(source_index)
    need((len(raw), H(raw)) == INDEX_PIN, 'sealed holdout V1 twenty-overlay index pin differs')
    need(index.get('kind') == 'SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_C878_S135_INDEX_V1', 'new source index kind required')
    entries = index.get('overlay_entries')
    need(type(entries) is list and len(entries) == 20, 'exact twenty source overlays required')
    result = {}; basenames = set(); source_dir = Path(source_dir)
    for entry in entries:
        rel = safe_relative(entry['relative'])
        basename = entry['path'].replace('\\\\', '/').rsplit('/', 1)[-1]
        need(basename not in ('', '.', '..') and basename not in basenames, 'unique flat source basename required')
        basenames.add(basename)
        need(rel in ALIASES and rel not in result, 'unknown/duplicate source alias')
        path = no_links(source_dir, basename); info = identity(path)
        need((info['bytes'], info['SHA']) == (entry['bytes'], entry['SHA256']), 'flat pinned source differs: ' + basename)
        if path.suffix == '.py': ast.parse(path.read_bytes())
        else: need(path.suffix == '.json' and type(metadata(path)[0]) is dict, 'explicit source JSON contract required')
        result[rel] = (path, info)
    need(set(result) == ALIASES, 'all twenty pinned aliases required, including canonical7a092 and AppV6/Base')
    return result, dict(path=str(source_index), bytes=len(raw), SHA=H(raw), provenance_paths_not_dereferenced=True), index
''')
    text = block(text, 'paired_plan', 'prepare', '''
def paired_plan(seed):
    need(type(seed) is int and seed in ALLOWED_SEEDS, 'independent holdout seed20260929 or20260930 only')
    protocol = dict(pose_source_SHA=POSE_SHA, pose_source_bytes=18161,
        pose_source_version='POSE_CACHE_RUNTIME_ADAPTER_V4_NATIVE_NEGATIVE_INFINITY_STALE_V1',
        install_timing='after_env_construction_before_original_single_explicit_reset', seed=seed, num_envs=80,
        explicit_original_reset_count=1, physics_dt=.0025, control_dt=.02, feedback_hz=100,
        actor_observation='original_noisy_delayed_policy35')
    return dict(kind='PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2', reference_planned_protocol=dict(protocol),
        candidate_planned_protocol=dict(protocol), historical_bug_baseline_reused=False, reference_actual_receipt=None)
''')
    text = block(text, 'prepare', 'verify_close_dependency_imports', '''
def prepare(original_group_root, source_dir, source_index, native_root, new_root, group_id, gpu_uuid, seed):
    need(type(seed) is int and seed in ALLOWED_SEEDS, 'independent holdout seed20260929 or20260930 only')
    need(Path(new_root).is_absolute(), 'explicit absolute new-root required')
    original_group_root, new_root = lexical(original_group_root), lexical(new_root)
    need(not new_root.is_symlink() and not new_root.exists(), 'each seed requires an absent one-use new-root')
    need(group_id == new_root.name and group_id != ORIGINAL_GROUP_ID and str(seed) in group_id
         and re.fullmatch(r'[A-Za-z0-9_]+', group_id), 'seed-tagged new explicit group-id/root required')
    need(re.fullmatch(r'GPU-[0-9a-f-]+', gpu_uuid) is not None, 'explicit GPU UUID required')
    for old in (original_group_root, lexical(native_root), lexical(source_dir), lexical(source_index).parent):
        need(not new_root.is_relative_to(old) and not old.is_relative_to(new_root), 'new-root overlaps an input')
    producers, boundary = native_boundary(native_root)
    sources, index_receipt, index = source_mappings(source_dir, source_index)
    old, old_raw = metadata(original_group_root / 'GROUP_PLAN.json')
    need(old.get('group_id') == original_group_root.name == index['original_group_id'] == ORIGINAL_GROUP_ID
         and old.get('asset_SHA') == USD and old.get('contract_SHA') == CONTRACT, 'exact original V8 group/assets required')
    original_rows = old.get('roles')
    need(type(original_rows) is list and len(original_rows) == 9
         and {r['role'] for r in original_rows} == set(ROLES) | {'H1_normal'}, 'original nine-to-eight catalog differs')
    materials = {}
    for directory in ('worker_sources', 'pinned_assets'):
        for rel, value in tree(original_group_root / directory).items(): materials[directory + '/' + rel] = value
    expected = {r['relative']:(r['bytes'],r['SHA256']) for r in index['inherited_original_worker_source_entries']}
    expected.update({r['relative']:(r['bytes'],r['SHA']) for r in index['required_original_pinned_assets']})
    old_files = old.get('worker_files')
    need(type(old_files) is list and len(old_files) == len(expected)
         and {r['relative'] for r in old_files} == set(expected), 'complete original worker_files dependency set differs')
    for item in old_files:
        rel = safe_relative(item['relative']); need(not any(denied(p) for p in rel.split('/')), 'non-static original worker input')
        need((item['bytes'],item['SHA']) == expected[rel], 'original source-index dependency pin differs: ' + rel)
        src = no_links(original_group_root, rel); info = identity(src)
        need(info == {k:item[k] for k in ('bytes','SHA')}, 'actual original worker-file pin differs: ' + rel)
        materials[rel] = (src, info)
    purpose = 'GOOD_EXPERT_HOLDOUT_C878_S135_SEED' + str(seed) + '_V1'
    plan = dict(kind='GOOD_EXPERT_HOLDOUT_C878_S135_PLAN_V1', seed=seed, batch_purpose=purpose,
        policy_variant='ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1', enabled=False, staged=False,
        source_native_enabled=False, dispatched=False, group_id=group_id, GPU_UUID=gpu_uuid, asset_SHA=USD, contract_SHA=CONTRACT,
        holdout_protocol=dict(kind='INDEPENDENT_GOOD_EXPERT_HOLDOUT_SEED_PROTOCOL_V1',seed=seed,purpose=purpose,published_baseline_seed=20260928,
            historical_seed_reassessment_counts_as_new_evidence=False,independent_group_per_seed=True,paired_effect_claim=False,
            cohort='original_env_id_mod3_ascending27_descending27_stand26',controls_per_role=750,num_envs=80,original_acceptance_unchanged=True),
        requested_roles=list(REQUESTED), deferred_roles=[r for r in ROLES if r not in REQUESTED],
        comparison=None, relative_improvement=None, paired_actual_reference=None, UID_alignment=None,
        reference_cache_match=None, reward_effect_identification=None, overall_eight_pass_rate=None,
        all_eight_actual_execution_complete=None, actual_resource_admission=None, actual_frozen_evaluation=None,
        paired_reset_protocol=paired_plan(seed), roles=[])
    by_role = {row['role']:row for row in original_rows}
    indexed_roles = {row['role']:row for row in index['required_original_runtime_rows']}
    runtime_receipts = {}
    guard_spec = importlib.util.spec_from_file_location('_holdout_stage_producer_guard', sources['producer_teacher_guard_v1.py'][0])
    guard = importlib.util.module_from_spec(guard_spec); guard_spec.loader.exec_module(guard)
    for role in ROLES:
        row = copy.deepcopy(by_role[role]); need(row.get('controls') == CONTROLS[role], 'original controls differ')
        historical = {k:row.pop(k) for k in list(row) if k.startswith('source_')}
        row.update(historical_mother_source=historical, source_identity='DEFERRED_NOT_A_NEW_CACHE_SOURCE',
                   a1_producer=None, num_envs=80, seed=20260928, status='deferred_not_constructed')
        if role in REQUESTED:
            old_runtime = lexical(row['runtime_root'])
            need(old_runtime == original_group_root / 'runtimes' / role, 'exact selected original runtime tree required')
            reference = indexed_roles[role]
            need(row['runtime_origin'] == reference['runtime_origin'] and row['worker'] == reference['worker'], 'selected original runtime/worker provenance differs')
            files = tree(old_runtime)
            canonical_rel = 'runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json'
            need(canonical_rel in files and metadata(files[canonical_rel][0])[0].get('canonical') == role, 'actual selected E1 canonical metadata differs')
            runtime_receipts[role] = digest_tree(files)
            for rel, value in files.items(): materials['runtimes/' + role + '/' + rel] = value
            asset = lexical(row['asset_dir']); need(asset.is_relative_to(old_runtime), 'original selected asset-dir escaped runtime')
            row.update(runtime_root=str(new_root / 'runtimes' / role),
                asset_dir=str(new_root / 'runtimes' / role / asset.relative_to(old_runtime)), seed=seed, status='requested_source_only',
                a1_producer=producers[role], policy_variant=plan['policy_variant'], actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN',
                actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',
                original_bootstrap_teacher=guard.teacher_identity(producers[role]['FINAL']['teacher']),
                producer_teacher_freeze_evidence=guard.derive_producer_guard(producers[role]))
            cp = producers[role]['FINAL']['checkpoint']
            row.update(source_path=cp['path'], source_SHA=cp['SHA'], source_bytes=cp['bytes'],
                       source_identity='OWN_A1_FULL_NEW_CHECKPOINT_NOT_MOTHER_OR_OLD_PPO')
        plan['roles'].append(row)
    vendor = tree(Path(native_root) / 'roles' / 'E3' / 'worker_sources' / 'supermimic_vendor_v2')
    observed = digest_tree(vendor)
    need((observed['files'], observed['SHA']) == VENDOR_PIN, 'actual complete original vendor7 tree differs')
    for path,_ in vendor.values(): ast.parse(path.read_bytes())
    need({'__init__.py','learner.py','networks.py','geometry.py','replay.py','contract.py'} <= set(vendor)
         and all('/' not in rel and rel.endswith('.py') for rel in vendor), 'full original flat vendor7 required')
    init = ast.parse(vendor['__init__.py'][0].read_bytes())
    need(len(init.body) == 1 and isinstance(init.body[0],ast.Expr) and isinstance(init.body[0].value,ast.Constant)
         and type(init.body[0].value.value) is str, 'original docstring-only vendor init required; no cropping/stub')
    for rel,value in vendor.items(): materials['supermimic_vendor_v2/' + rel] = value
    for rel,value in sources.items():
        if rel.startswith('supermimic_vendor_v2/'): need(materials[rel][1] == value[1], 'vendor/index source mismatch')
        materials[rel] = value
    verify_aliases = {r['relative'] for r in old_files} | ALIASES | {'supermimic_vendor_v2/' + r for r in vendor}
    plan['worker_files'] = [dict(relative=rel,**materials[rel][1]) for rel in sorted(verify_aliases)]
    encoded = json.dumps(plan,indent=2,allow_nan=False).encode()
    need(len(encoded) <= 262144, 'plan exceeds sealed metadata bound')
    prepared = dict(plan=plan,materials=materials,boundary=boundary,source_index=index_receipt,original_plan_SHA=H(old_raw),
        native_vendor=observed,selected_runtime_trees=runtime_receipts,new_root=new_root,encoded_plan=encoded)
    prepared['metadata_validation'] = metadata_validate(prepared)
    return prepared
''')
    text = block(text, 'metadata_validate', 'put_once', '''
def metadata_validate(prepared, actual_root=None):
    """Full real metadata import closure, never native parent/bridge execution.
    Before stage only text aliases are copied into a disposable import view; all
    actual role/static/vendor materials have already been hashed in full. No new-root
    or native-root is created. After materialization, import the actual target aliases.
    """
    temporary = None
    if actual_root is None:
        temporary = tempfile.TemporaryDirectory(prefix='HOLDOUT_METADATA_IMPORT_ONLY_')
        root = Path(temporary.name)
        for rel,(source,info) in prepared['materials'].items():
            if rel.startswith(('runtimes/','pinned_assets/')) or Path(rel).suffix not in ('.py','.json'): continue
            target = root / safe_relative(rel); target.parent.mkdir(parents=True,exist_ok=True)
            raw = source.read_bytes(); need(dict(bytes=len(raw),SHA=H(raw)) == info,'source changed before metadata import')
            with target.open('xb') as stream: stream.write(raw)
    else: root = Path(actual_root)
    old_path, old_bytecode = list(sys.path), sys.dont_write_bytecode
    old_resolve, old_open, old_io_open, old_stat, old_lstat, old_import = Path.resolve,builtins.open,io.open,os.stat,os.lstat,builtins.__import__
    names = ('good_expert_holdout_runtime_v1','a1_frozen_eval_runtime_v2','producer_teacher_guard_v1',
        'embedded_teacher_reference_v1','frozen_a1_raw35_v1','pose_cache_runtime_adapter_v3',
        'app_close_semantics_v5','resume_runtime_contracts_v3','e1_parallel_worker_safe','e1_fresh_runtime_bridge','e1_route80_factories','e1_endpoint_predicate')
    modules = {name:sys.modules.get(name) for name in names}; avoided=[]
    forbidden = {'torch','numpy','isaacsim','isaaclab','omni','warp','pxr','rsl_rl','tensordict','psutil','fcntl'}
    def guarded(function):
        def call(path,*args,**kwargs):
            need(not model_path(path) and not (not isinstance(path,int) and ('budget' in Path(os.fspath(path)).name.lower()
                 or Path(os.fspath(path)).suffix.lower() == '.lock')), 'metadata attempted model/budget/lock filesystem access')
            return function(path,*args,**kwargs)
        return call
    def resolve(path,*args,**kwargs):
        if model_path(path): avoided.append(str(path)); return lexical(path)
        return old_resolve(path,*args,**kwargs)
    def imported(name,*args,**kwargs):
        need(name.split('.')[0] not in forbidden,'native import is outside metadata closure: ' + name)
        return old_import(name,*args,**kwargs)
    try:
        sys.path[:0] = [str(root),str(root/'worker_sources/e1')]; sys.dont_write_bytecode=True
        for name in names: sys.modules.pop(name,None)
        Path.resolve=resolve; builtins.open=guarded(old_open); io.open=guarded(old_io_open)
        os.stat=guarded(old_stat); os.lstat=guarded(old_lstat); builtins.__import__=imported
        dependency = verify_close_dependency_imports(root/'app_close_semantics_v5.py',root/'resume_runtime_contracts_v3.py')
        runtime = importlib.import_module('good_expert_holdout_runtime_v1')
        for name in ('frozen_a1_raw35_v1','pose_cache_runtime_adapter_v3','e1_parallel_worker_safe','e1_fresh_runtime_bridge','e1_route80_factories','e1_endpoint_predicate'):
            module = importlib.import_module(name)
            expected = root / (('worker_sources/e1/' if name.startswith('e1_') else '') + name + '.py')
            need(Path(module.__file__).resolve() == expected.resolve(),'actual metadata import origin differs: ' + name)
        plan = copy.deepcopy(prepared['plan']); rows = runtime.select_requested_roles(plan)
        need([row['role'] for row in rows] == list(REQUESTED),'metadata exact two roles differs')
        task_checks=[]
        for row in rows:
            task=runtime.make_task(row,plan,9999999999.,[101,102])
            runtime._validate_batch_members(task,row['role'])
            need(task['seed'] == plan['seed'] and task['physics_callbacks'] == 6000 and task['feedback_samples'] == 1500,'metadata task scope differs')
            bad=copy.deepcopy(task); other=ALLOWED_SEEDS[1] if plan['seed']==ALLOWED_SEEDS[0] else ALLOWED_SEEDS[0]
            bad.update(seed=other,batch_purpose=runtime.purpose_for(other),holdout_protocol=runtime.holdout_protocol(other))
            try: runtime._validate_batch_members(bad,row['role'])
            except (ValueError,AssertionError): pass
            else: raise ValueError('cross-seed task/pose was accepted')
            task_checks.append(dict(role=row['role'],seed=task['seed'],make_task_passed=True,cross_seed_pose_rejected=True))
        bad=copy.deepcopy(plan); bad['seed']=20260928
        try: runtime.select_requested_roles(bad)
        except (ValueError,AssertionError): pass
        else: raise ValueError('historical seed incorrectly accepted as holdout')
        need(not any(name.split('.')[0] in forbidden for name in sys.modules),'metadata imported a native module')
        return dict(kind='GOOD_EXPERT_HOLDOUT_REAL_COMPLETE_METADATA_CLOSURE_CHECK_V1',passed=True,
            requested_roles=list(REQUESTED),seed=plan['seed'],purpose=plan['batch_purpose'],dependency_completeness=dependency,
            task_checks=task_checks,historical_seed_rejected=True,full_modules_not_AST_cropped_or_stubbed=True,
            model_path_resolve='LEXICAL_METADATA_ONLY_NO_LSTAT',model_lstats_avoided=len(avoided),
            actual_resource_admission=None,actual_parent_or_worker_main_executed=False,
            metadata_preview_FDs_are_in_memory_placeholders_not_opened=True,
            parent_launches=0,model_stat_open_hash=0,C_lock_SDK_GPU_operations=0)
    finally:
        Path.resolve,builtins.open,io.open,os.stat,os.lstat,builtins.__import__=old_resolve,old_open,old_io_open,old_stat,old_lstat,old_import
        sys.path[:]=old_path; sys.dont_write_bytecode=old_bytecode
        for name,previous in modules.items():
            if previous is None: sys.modules.pop(name,None)
            else: sys.modules[name]=previous
        if temporary is not None:
            need(Path(temporary.name).resolve()==root.resolve() and root.name.startswith('HOLDOUT_METADATA_IMPORT_ONLY_'),'owned metadata temp cleanup target differs')
            temporary.cleanup()
''')
    text = block(text, 'preflight_summary', 'stage', '''
def preflight_summary(prepared):
    return dict(kind='SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V1',passed=True,
        source_native_enabled=False,staged=False,dispatched=False,materialized=False,
        new_root=str(prepared['new_root']),group_id=prepared['plan']['group_id'],seed=prepared['plan']['seed'],purpose=prepared['plan']['batch_purpose'],
        requested_roles=list(REQUESTED),deferred_roles=[r for r in ROLES if r not in REQUESTED],
        files=len(prepared['materials']),source_index=prepared['source_index'],native_boundary=prepared['boundary'],
        native_vendor=prepared['native_vendor'],selected_runtime_trees=prepared['selected_runtime_trees'],original_plan_SHA=prepared['original_plan_SHA'],
        metadata_validation=prepared['metadata_validation'],resource_admission=None,actual_frozen_evaluation=None,
        model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,parent_launches=0,new_root_created=False)
''')
    text = block(text, 'stage', 'main', '''
def stage(prepared):
    root=prepared['new_root']; need(not root.is_symlink() and not root.exists(),'actual materialization root already exists')
    root.mkdir(parents=False,exist_ok=False)
    put_json(root/'STAGE_BEGIN_GOOD_EXPERT_HOLDOUT_V1.json',preflight_summary(prepared))
    try:
        rows=[]
        for rel,(source,info) in sorted(prepared['materials'].items()):
            target=root/safe_relative(rel); target.parent.mkdir(parents=True,exist_ok=True)
            digest=hashlib.sha256(); count=0
            with source.open('rb') as incoming,target.open('xb') as outgoing:
                for chunk in iter(lambda:incoming.read(1024*1024),b''):
                    outgoing.write(chunk);digest.update(chunk);count+=len(chunk)
                outgoing.flush();os.fsync(outgoing.fileno())
            need(dict(bytes=count,SHA=digest.hexdigest())==info,'source changed after preflight: '+rel)
            rows.append(dict(relative=rel,**info))
        put_once(root/'GROUP_PLAN.json',prepared['encoded_plan'])
        validation=metadata_validate(prepared,actual_root=root)
        put_json(root/'STAGED_STATIC_FILES_GOOD_EXPERT_HOLDOUT_V1.json',dict(files=rows,source_index=prepared['source_index'],native_boundary=prepared['boundary']))
        receipt=dict(kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V1',materialized=True,
            source_native_enabled=False,staged=False,dispatched=False,group_id=prepared['plan']['group_id'],root=str(root),
            seed=prepared['plan']['seed'],purpose=prepared['plan']['batch_purpose'],requested_roles=list(REQUESTED),
            source_files=len(rows),metadata_validation=validation,native_boundary=prepared['boundary'],selected_runtime_trees=prepared['selected_runtime_trees'],
            original_plan_SHA=prepared['original_plan_SHA'],model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,
            parent_launches=0,resource_admission=None,actual_frozen_evaluation=None,comparison=None,overall_eight_pass_rate=None)
        put_json(root/COMPLETE_NAME,receipt)
        return receipt
    except BaseException:
        put_json(root/'STAGE_ERROR_GOOD_EXPERT_HOLDOUT_V1.json',dict(error=traceback.format_exc(),dispatched=False,
            root_consumed_no_same_root_retry=True,parent_launches=0))
        raise
''')
    start = text.index('def main():')
    text = text[:start] + '''def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ('original-group-root','source-dir','source-index','native-root','new-root'):
        parser.add_argument('--'+arg,required=True,type=Path)
    parser.add_argument('--group-id',required=True);parser.add_argument('--gpu-uuid',required=True)
    parser.add_argument('--seed',required=True,type=int,choices=ALLOWED_SEEDS)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--preflight-only',action='store_true');modes.add_argument('--stage',action='store_true')
    args=parser.parse_args()
    prepared=prepare(args.original_group_root,args.source_dir,args.source_index,args.native_root,args.new_root,args.group_id,args.gpu_uuid,args.seed)
    print(json.dumps(stage(prepared) if args.stage else preflight_summary(prepared),indent=2,allow_nan=False))


if __name__=='__main__': main()
'''
    ast.parse(text)
    target = HERE / 'stage_good_expert_holdout_v1.py'
    raw = text.encode()
    if target.exists(): assert target.read_bytes() == raw, 'existing NEW source differs; review targeted edit'
    else:
        with target.open('xb') as stream: stream.write(raw)
    print(json.dumps(dict(kind='NEW_STDLIB_CLI_SOURCE_DERIVED_NOT_RUN',files=1,bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),source_native_enabled=False,staged=False,dispatched=False)))


if __name__ == '__main__': main()
