"""Build/verify NEW D4 immutable SOURCE metadata, never a materializer entry.
Import the complete pinned D3 stdlib metadata module for read/hash/AST helpers;
its main/metadata_products/create_or_verify and all materializer entries stay idle.
"""
from pathlib import Path, PurePosixPath
import ast
import copy
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R=HERE.parent
WORKSPACE=R.parent
PREVIOUS=R/'source_stage_good_expert_holdout_v3'
PREVIOUS_SEAL=(2034,'0777c2e284d339ffc9c658a92188ee8c2ebb491c82d4124330a794f68654f426')
PREVIOUS_ROOT='1cdd8c72dfdc9fbb3b75f4068f53e8f489d7d558c79a637f39597efae8e765cd'
PREVIOUS_BUILDER=(12503,'54812c942d518eca89561618a3e3398f5d4f3286578d2039122584509ef9026c')
PREVIOUS_ENTRY=(53062,'a7eca32d8efc510ba4529b8be7c2b64d7de936f110a4eff4d847925024f43b11')
ENTRY_PIN=(53515,'c6be5e8acd2bd1a83f09427fb717cc1d102077cf363b67034d65d09f4e86ab0d')
WIRE=R/'discovery/good_holdout_original_plan_wire_v1/ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json'
WIRE_PIN=(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1')
PUBLISHED=WORKSPACE/'mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json'
PUBLISHED_PIN=(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0')
CANONICAL_SHA='8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a'
DIAG=R/'reports/GOOD_HOLDOUT_ORIGINAL_PLAN_WIRE_VS_PUBLISHED_DIAGNOSIS_V1.json'
DIAG_PIN=(1459,'673398d112f60f084b9c945a747d0d13625e43487291549d9d4dfca0a3991b38')
FILES=('README.md','SOURCE_INDEX.json','SOURCE_MIRROR_INPUTS.json','TEST_REPORT.json','WHITELIST_DIFF.json',
       'build_source_manifest_v4.py','derive_stage_good_holdout_v4.py','derive_regressions_v4.py',
       'stage_good_expert_holdout_v4.py','test_good_holdout_v4_source.py')
CHANGED={'prepare','preflight_summary','stage'}


def need(value,message):
    if not value:raise ValueError(message)


def H(raw):return hashlib.sha256(raw).hexdigest()


def bootstrap_complete_previous_helpers():
    raw=(PREVIOUS/'SOURCE_SEAL.json').read_bytes();need((len(raw),H(raw))==PREVIOUS_SEAL,'fixed D3 SOURCE seal differs')
    seal=json.loads(raw);need(seal['root_SHA256']==PREVIOUS_ROOT and len(seal['files'])==10,'D3 fixed complete root differs')
    records=''.join(f"{r['name']}\t{r['bytes']}\t{r['SHA256']}\n" for r in sorted(seal['files'],key=lambda r:r['name'])).encode()
    need(H(records)==PREVIOUS_ROOT,'D3 canonical source root differs')
    for row in seal['files']:
        need(PurePosixPath(row['name']).name==row['name'],'D3 source member is not flat')
        path=PREVIOUS/row['name'];need(not path.is_symlink() and path.suffix in ('.py','.json','.md'),'D3 source member type differs')
        data=path.read_bytes();need((len(data),H(data))==(row['bytes'],row['SHA256']),'D3 sealed source differs: '+row['name'])
    path=PREVIOUS/'build_source_manifest_v3.py';data=path.read_bytes();need((len(data),H(data))==PREVIOUS_BUILDER,'whole D3 helper module pin differs')
    spec=importlib.util.spec_from_file_location('_good_holdout_v4_whole_previous_manifest_helpers',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


P=bootstrap_complete_previous_helpers()
encoded=P.encoded
identity=P.identity
root_of=P.root_of
read_text=P.read_text
relative=P.relative
function_map=P.function_map
function_source=P.function_source


def metadata_products():
    inputs=set();previous=P.M.verify_old_seal(PREVIOUS,'SOURCE_SEAL.json',PREVIOUS_ROOT,10,inputs)
    old_index=json.loads(read_text(PREVIOUS/'SOURCE_INDEX.json'));old_mirror=json.loads(read_text(PREVIOUS/'SOURCE_MIRROR_INPUTS.json'))
    old_rows=old_mirror['files'];need(len(old_rows)==old_mirror['files_count']==79,'complete previous79 text closure differs')
    seen=set()
    for row in old_rows:
        rel=row['workspace_relative'];pure=PurePosixPath(rel)
        need(not pure.is_absolute() and all(p not in ('','.','..') for p in rel.split('/')) and rel not in seen,'old SOURCE mirror relative differs')
        seen.add(rel);path=WORKSPACE.joinpath(*pure.parts)
        read_text(path,(row['bytes'],row['SHA256']));inputs.add(path)
    w=read_text(WIRE,WIRE_PIN);p=read_text(PUBLISHED,PUBLISHED_PIN);d=read_text(DIAG,DIAG_PIN)
    inputs.update((WIRE,PUBLISHED,DIAG))
    canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
    need(json.loads(w)==json.loads(p),'actual wire and published SOURCE decoded values differ')
    need(H(canonical(json.loads(w)))==H(canonical(json.loads(p)))==CANONICAL_SHA,'fixed decoded canonical identity differs')
    need(w!=p and p.replace(b'\r\n',b'\n')==w and p.count(b'\r\n')==273 and w.count(b'\r\n')==0,'observed wire/source newline evidence differs')
    diagnosis=json.loads(d)
    need(diagnosis['whole_decoded_values_equal'] is True and diagnosis['differences_first30']==[],'source diagnosis equality differs')
    need((diagnosis['actual_wire_bytes'],diagnosis['actual_wire_SHA256'])==WIRE_PIN and
         (diagnosis['cached_published_bytes'],diagnosis['cached_published_SHA256'])==PUBLISHED_PIN,'source diagnosis identities differ')
    need(diagnosis['old_preflight_failure_unchanged'] is True and diagnosis['stage2_GO'] is False and diagnosis['gate1']=='UNKNOWN','historical failure/unknown boundaries differ')
    old_raw=read_text(PREVIOUS/'stage_good_expert_holdout_v3.py',PREVIOUS_ENTRY)
    new_raw=read_text(HERE/'stage_good_expert_holdout_v4.py',ENTRY_PIN)
    old_funcs=function_map(old_raw);new_funcs=function_map(new_raw);dump=lambda node:ast.dump(node,include_attributes=False)
    need(set(old_funcs)==set(new_funcs),'D4 added/removed a runtime helper')
    need({n for n in old_funcs if dump(old_funcs[n])!=dump(new_funcs[n])}==CHANGED,'D4 three-function whitelist differs')
    unchanged=[]
    for name in sorted(set(old_funcs)-CHANGED):
        a=function_source(old_raw,old_funcs[name]);b=function_source(new_raw,new_funcs[name])
        need(a==b,'whole original D3 function source changed: '+name)
        unchanged.append(dict(function=name,whole_source_bytes=len(a.encode()),whole_source_SHA256=H(a.encode()),whole_AST_equal=True))
    need(len(unchanged)==28,'D3 complete unchanged function count differs')
    new_prepare=copy.deepcopy(new_funcs['prepare'])
    guard=[node for node in new_prepare.body if 'ORIGINAL_PLAN_CANONICAL_SHA256' in ast.unparse(node)]
    need(len(guard)==1,'exactly one new canonical guard required');new_prepare.body.remove(guard[0])
    for node in ast.walk(new_prepare):
        if isinstance(node,ast.Constant) and node.value=='fixed original GROUP_PLAN wire bytes differ':
            node.value='fixed published original GROUP_PLAN bytes differ'
    need(dump(new_prepare)==dump(old_funcs['prepare']),'prepare changed beyond strict wire message and single canonical guard')
    expected_global={'SOURCE_DERIVATION_VERSION':4,'ORIGINAL_PLAN_PIN':WIRE_PIN,'PUBLISHED_ORIGINAL_PLAN_PIN':PUBLISHED_PIN,
                     'ORIGINAL_PLAN_CANONICAL_SHA256':CANONICAL_SHA}
    globals_found={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(new_raw).body
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in expected_global}
    need(globals_found==expected_global,'strict runtime-wire/published-SOURCE constants differ')
    for name in ('preflight_summary','stage'):
        candidate=copy.deepcopy(new_funcs[name])
        for node in ast.walk(candidate):
            if isinstance(node,ast.Constant) and isinstance(node.value,str):
                node.value=node.value.replace('SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V4','SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V3').replace(
                    'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V4','SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3')
            if isinstance(node,ast.keyword) and node.arg=='source_derivation_version':
                need(isinstance(node.value,ast.Constant) and node.value.value==4,'SOURCE version label shape differs');node.value.value=3
        need(dump(candidate)==dump(old_funcs[name]),'D4 changed stage/preflight beyond SOURCE version labels')
    before_loop=next(n for n in ast.walk(old_funcs['stage']) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple))
    after_loop=next(n for n in ast.walk(new_funcs['stage']) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple))
    need(dump(before_loop)==dump(after_loop),'complete copy/hash/fsync loop changed')
    stage=ast.unparse(new_funcs['stage'])
    need(stage.index('derive_materialized_runtime_plan(')<stage.index('metadata_validate(runtime_prepared, actual_root=root)')<stage.index("root / 'GROUP_PLAN.json'"),'runtime publication ordering differs')
    report=json.loads(read_text(HERE/'TEST_REPORT.json'))
    need(report['passed'] is True and report['tests_run']==36 and report['errors']==report['failures']==0,'NEW36 regression receipt required')
    need(len(report['audit'])==5 and all(v==0 for v in report['audit'].values()),'SOURCE audit not all zero')
    for key in ('actual_prepare_preflight_stage_dispatch_executed','actual_parent_worker_executed','V2_test_module_imported_or_replayed',
                'D3_test_module_imported_or_replayed','full_prepare_invoked'):
        need(report[key] is False,'a forbidden original/native operation was reported: '+key)
    for key in ('true_plan_two_seed_whole_metadata_passed','publication_probe_is_own_in_memory_fake_IO_not_stage',
                'negative_publication_probes_emit_nothing','strict_actual_wire_and_canonical_guard_exercised_in_FAKE_fixture',
                'canonical_equal_not_treated_as_wire_identity'):
        need(report[key] is True,'D4 regression evidence missing: '+key)
    rows=[]
    for path in sorted(inputs,key=lambda path:relative(path)):
        raw=read_text(path);rows.append(dict(workspace_relative=relative(path),**identity(raw)))
    positions={row['workspace_relative']:row for row in rows};need(len(positions)==len(rows),'mirror aliases collide')
    need(all(positions[row['workspace_relative']]==row for row in old_rows),'previous79 SOURCE members were dropped or rewritten')
    need(positions[relative(PUBLISHED)]==old_index['original_group_plan'],'cached published SOURCE mirror declaration changed')
    mirror=dict(kind='COMPLETE_GOOD_HOLDOUT_V4_PINNED_TEXT_MIRROR_INPUTS',source_only=True,
        root_layout=old_mirror['root_layout'],files=rows,files_count=len(rows),previous79_members_unchanged=True,
        raw_assets_static_banks_models_included=False,complete_runtime_materialization_proved=False,
        requires_new_source_package_members_and_seal_separately=True)
    descriptor=copy.deepcopy(old_index['typed_runtime_publication'])
    descriptor.update(stage_receipt_kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V4',source_derivation_version=4,
        original_plan_SHA='SHA256 of exact actual original V8 wire bytes: '+WIRE_PIN[1]+'; neither published SOURCE bytes nor the new GROUP_PLAN hash',
        original_plan_wire_pin=dict(bytes=WIRE_PIN[0],SHA256=WIRE_PIN[1]),
        published_original_plan_SOURCE_reference=dict(workspace_relative=relative(PUBLISHED),bytes=PUBLISHED_PIN[0],SHA256=PUBLISHED_PIN[1]))
    identity_descriptor=dict(kind='STRICT_ACTUAL_ORIGINAL_WIRE_AND_PUBLISHED_SOURCE_IDENTITY_V1',
        runtime_ORIGINAL_PLAN_PIN=dict(bytes=WIRE_PIN[0],SHA256=WIRE_PIN[1]),
        PUBLISHED_ORIGINAL_PLAN_PIN=dict(bytes=PUBLISHED_PIN[0],SHA256=PUBLISHED_PIN[1]),
        decoded_canonical_SHA256=CANONICAL_SHA,whole_decoded_values_equal=True,literal_wire_bytes_equal=False,
        canonical_equivalence_does_not_relax_raw_wire_pin=True,
        original_plan_SHA_is_actual_wire_not_published_or_new_GROUP_PLAN=True,
        previous_published_SOURCE_mirror_declaration_unchanged=True,
        prior_before_stage_failures_remain_historical_failures=True,
        wire_capture_read_is_local_SOURCE_not_new_remote_read=True)
    index=json.loads(json.dumps(old_index));index.update(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V4',source_derivation_version=4,
        entry=dict(name='stage_good_expert_holdout_v4.py',**identity(new_raw)),previous_materializer_seal=previous,
        source_mirror=dict(name='SOURCE_MIRROR_INPUTS.json',**identity(encoded(mirror)),files_count=len(rows)),
        source_test_report=report,typed_runtime_publication=descriptor,
        original_group_plan_wire=dict(workspace_relative=relative(WIRE),**identity(w)),
        original_group_plan_wire_identity=identity_descriptor,
        wire_identity_diagnosis_source_only=dict(workspace_relative=relative(DIAG),**identity(d),executed=False))
    for key in ('flat_source_dir_complete20_mapping','original_worker_files','original_group_plan','source_index','wire',
                'preserved_original_resource_logic','native_unknowns','upstream_source_seal','old_materializer_seal'):
        need(index[key]==old_index[key],'immutable upstream SOURCE evidence changed: '+key)
    for key in ('enabled','source_native_enabled','staged','dispatched'):need(index[key] is False,'SOURCE activation changed')
    diff=dict(kind='GOOD_HOLDOUT_V4_EXACT_THREE_FUNCTION_SOURCE_DIFF',source_only=True,changed_functions=sorted(CHANGED),
        new_runtime_helpers=[],unchanged_D3_functions=28,whole_function_source_proofs=unchanged,
        old_cli=dict(workspace_relative=relative(PREVIOUS/'stage_good_expert_holdout_v3.py'),**identity(old_raw)),
        new_cli=dict(name='stage_good_expert_holdout_v4.py',**identity(new_raw)),
        prepare_only_strict_wire_message_and_one_extra_canonical_guard=True,
        stage_and_preflight_only_SOURCE_version_labels_changed=True,
        actual_copy_hash_fsync_loop_complete_AST_equal=True,semantics=descriptor,
        source_wire_identity=identity_descriptor,parent_and_runtime_complete_bytes_unchanged=True,
        source_mappings_complete_source_AST_unchanged=True,previous79_text_members_unchanged=True,
        full_metadata_main_helper_put_once_and_all_resource_functions_unchanged=True,
        actual_prepare_preflight_stage_parent_worker_executed=False)
    return mirror,index,diff


def create_or_verify(name,value,verify):
    path=HERE/name;raw=encoded(value)
    if path.exists():need(path.read_bytes()==raw,'immutable NEW D4 SOURCE differs: '+name)
    else:
        need(not verify,'missing sealed D4 SOURCE metadata: '+name)
        with path.open('xb')as stream:stream.write(raw)


def main():
    need(sys.argv[1:] in ([],['--verify']),'only --verify is accepted');verify=sys.argv[1:]==['--verify']
    mirror,index,diff=metadata_products()
    for name,value in [('SOURCE_MIRROR_INPUTS.json',mirror),('SOURCE_INDEX.json',index),('WHITELIST_DIFF.json',diff)]:create_or_verify(name,value,verify)
    files=[dict(name=name,**identity(read_text(HERE/name))) for name in FILES]
    seal=dict(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_IMMUTABLE_SEAL_V4',status='SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE',
        enabled=False,source_native_enabled=False,staged=False,dispatched=False,actual_native_binding='UNKNOWN',
        root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root_of(files),files=files)
    create_or_verify('SOURCE_SEAL.json',seal,verify)
    print(json.dumps(dict(kind='SOURCE_GOOD_HOLDOUT_V4_SEAL_VERIFIED_NO_WRITES' if verify else 'SOURCE_GOOD_HOLDOUT_V4_SEALED_NOT_NATIVE',
        files=len(files),root_SHA256=seal['root_SHA256'],text_mirror_files=len(mirror['files']),NEW_tests=36,
        actual_prepare_preflight_stage_parent_worker_executed=False)))

if __name__=='__main__':main()
