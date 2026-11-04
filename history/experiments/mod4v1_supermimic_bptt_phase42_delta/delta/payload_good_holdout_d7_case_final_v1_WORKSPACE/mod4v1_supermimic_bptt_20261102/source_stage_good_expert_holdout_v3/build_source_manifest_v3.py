"""SOURCE-only immutable metadata builder. Never calls a materializer entry.
Imports the complete byte-pinned V2 stdlib manifest module for read/hash/AST
helpers; its main/metadata_products/create_or_verify are NEVER called.
"""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R=HERE.parent
WORKSPACE=R.parent
PREVIOUS=R/'source_stage_good_expert_holdout_v2'
PREVIOUS_SEAL=(1874,'efee47debc71f12b9eed123283e08e34dcec757893cbff5532056db08657d75c')
PREVIOUS_ROOT='eb8b7b9ea06bbac56132eb0a761da35780547cc35ff9f9c1fb0166838a6b7d42'
PREVIOUS_BUILDER=(14620,'bc20cec43c0e9192b710083eb1696f2caa672b02d72ea2262e4649405a589f91')
ENTRY_PIN=(53062,'a7eca32d8efc510ba4529b8be7c2b64d7de936f110a4eff4d847925024f43b11')
GAP=R/'source_good_holdout_operational_gap_review_v1'
GAP_PINS={'SOURCE_REVIEW.md':(10899,'abb4995f872209b58fe2c4f6b45b68c252dd0e4dc7abd970b15ba52e58af24c9'),
          'SOURCE_REVIEW.json':(11287,'5f40338e026150e5892bf7a1af5c824c2ff37a3477d4c143d72a3f3f03a8b235')}
FILES=('README.md','SOURCE_INDEX.json','SOURCE_MIRROR_INPUTS.json','TEST_REPORT.json','WHITELIST_DIFF.json',
       'build_source_manifest_v3.py','derive_stage_good_holdout_v3.py','derive_regressions_v3.py',
       'stage_good_expert_holdout_v3.py','test_good_holdout_v3_source.py')
CHANGED={'preflight_summary','stage'}
ADDED={'derive_materialized_runtime_plan'}


def need(value,message):
    if not value:raise ValueError(message)


def H(raw):return hashlib.sha256(raw).hexdigest()


def bootstrap_complete_previous_helpers():
    raw=(PREVIOUS/'SOURCE_SEAL.json').read_bytes();need((len(raw),H(raw))==PREVIOUS_SEAL,'fixed V2 SOURCE seal differs')
    seal=json.loads(raw);need(seal['root_SHA256']==PREVIOUS_ROOT and len(seal['files'])==9,'V2 fixed nine-member root differs')
    records=''.join(f"{r['name']}\t{r['bytes']}\t{r['SHA256']}\n" for r in sorted(seal['files'],key=lambda r:r['name'])).encode()
    need(H(records)==PREVIOUS_ROOT,'V2 canonical root differs')
    for row in seal['files']:
        need(PurePosixPath(row['name']).name==row['name'],'V2 seal member is not flat')
        path=PREVIOUS/row['name'];need(not path.is_symlink() and path.suffix in ('.py','.json','.md'),'V2 source member type differs')
        data=path.read_bytes();need((len(data),H(data))==(row['bytes'],row['SHA256']),'V2 sealed source differs: '+row['name'])
    helper=PREVIOUS/'build_source_manifest_v2.py';data=helper.read_bytes();need((len(data),H(data))==PREVIOUS_BUILDER,'V2 full helper module pin differs')
    spec=importlib.util.spec_from_file_location('_good_holdout_v3_whole_previous_manifest_helpers',helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


M=bootstrap_complete_previous_helpers()
encoded=M.encoded
identity=M.identity
root_of=M.root_of
read_text=M.read_text
relative=M.relative
function_map=M.function_map
function_source=M.function_source


def metadata_products():
    inputs=set();previous=M.verify_old_seal(PREVIOUS,'SOURCE_SEAL.json',PREVIOUS_ROOT,9,inputs)
    old_index=json.loads(read_text(PREVIOUS/'SOURCE_INDEX.json'));old_mirror=json.loads(read_text(PREVIOUS/'SOURCE_MIRROR_INPUTS.json'))
    old_rows=old_mirror['files'];need(len(old_rows)==old_mirror['files_count']==67,'original complete67 text closure differs')
    seen=set()
    for row in old_rows:
        rel=row['workspace_relative'];pure=PurePosixPath(rel)
        need(not pure.is_absolute() and all(p not in ('','.','..') for p in rel.split('/')) and rel not in seen,'old SOURCE mirror relative differs')
        seen.add(rel);path=WORKSPACE.joinpath(*pure.parts)
        read_text(path,(row['bytes'],row['SHA256']));inputs.add(path)
    for name,pin in GAP_PINS.items():read_text(GAP/name,pin);inputs.add(GAP/name)
    old_raw=read_text(PREVIOUS/'stage_good_expert_holdout_v2.py',(47717,'f7638e1f24e416780d6124df5fea2492a63d5daac73984470b96a32132ca242d'))
    new_raw=read_text(HERE/'stage_good_expert_holdout_v3.py',ENTRY_PIN)
    old_funcs=function_map(old_raw);new_funcs=function_map(new_raw)
    dump=lambda node:ast.dump(node,include_attributes=False)
    need({n for n in old_funcs if dump(old_funcs[n])!=dump(new_funcs[n])}==CHANGED,'V3 two-function whitelist differs')
    need(set(new_funcs)-set(old_funcs)==ADDED and set(old_funcs)<=set(new_funcs),'V3 helper or original function set differs')
    unchanged=[]
    for name in sorted(set(old_funcs)-CHANGED):
        old_source=function_source(old_raw,old_funcs[name]);new_source=function_source(new_raw,new_funcs[name])
        need(old_source==new_source,'whole original V2 function source changed: '+name)
        unchanged.append(dict(function=name,whole_source_bytes=len(old_source.encode()),whole_source_SHA256=H(old_source.encode()),whole_AST_equal=True))
    need(len(unchanged)==28,'V2 complete function count differs')
    first_raw=read_text(M.OLD/'stage_good_expert_holdout_v1.py',(38828,'fc9dd74437258d408e0223359b45814909b5a9a2f80df450dfdea1f546290a2f'))
    first_funcs=function_map(first_raw)
    need({n for n in first_funcs if dump(first_funcs[n])!=dump(new_funcs[n])}=={'prepare','preflight_summary','stage'},'V1 preserved source set differs')
    need(len(first_funcs)-3==22,'V1 complete function count differs')
    before_loop=next(n for n in ast.walk(old_funcs['stage']) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple))
    after_loop=next(n for n in ast.walk(new_funcs['stage']) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple))
    need(dump(before_loop)==dump(after_loop),'whole actual copy/hash/fsync loop changed')
    stage=ast.unparse(new_funcs['stage']);need(stage.index('derive_materialized_runtime_plan(')<stage.index('metadata_validate(runtime_prepared, actual_root=root)')<stage.index("root / 'GROUP_PLAN.json'"),'plan publication ordering differs')
    need("put_once(root / 'GROUP_PLAN.json', runtime_bytes)" in stage and "runtime_plan['group_id'] == root.name" in stage,'runtime bytes/root publication guard differs')
    helper=ast.unparse(new_funcs['derive_materialized_runtime_plan'])
    for forbidden in ('approved','Popen','.open(','.read_bytes(','.write_bytes(','metadata_validate(','os.fsync'):
        need(forbidden not in helper,'pure SOURCE helper gained IO/admission: '+forbidden)
    report=json.loads(read_text(HERE/'TEST_REPORT.json'))
    need(report['passed'] is True and report['tests_run']==32 and report['errors']==report['failures']==0,'NEW32 regression receipt required')
    need(all(v==0 for v in report['audit'].values()) and len(report['audit'])==5,'SOURCE audit is not all zero')
    for key in ('actual_prepare_preflight_stage_dispatch_executed','actual_parent_worker_executed','V2_test_module_imported_or_replayed'):
        need(report[key] is False,'a forbidden original/native operation was reported')
    for key in ('true_plan_two_seed_whole_metadata_passed','publication_probe_is_own_in_memory_fake_IO_not_stage','negative_publication_probes_emit_nothing'):
        need(report[key] is True,'new publication regression is missing: '+key)
    rows=[]
    for path in sorted(inputs,key=lambda p:relative(p)):
        raw=read_text(path);rows.append(dict(workspace_relative=relative(path),**identity(raw)))
    positions={row['workspace_relative']:row for row in rows};need(len(positions)==len(rows),'mirror aliases collide')
    need(all(positions[row['workspace_relative']]==row for row in old_rows),'a previous67 mirror member was dropped or rewritten')
    mirror=dict(kind='COMPLETE_GOOD_HOLDOUT_V3_PINNED_TEXT_MIRROR_INPUTS',source_only=True,
        root_layout=old_mirror['root_layout'],files=rows,files_count=len(rows),previous67_members_unchanged=True,
        raw_assets_static_banks_models_included=False,complete_runtime_materialization_proved=False,
        requires_new_source_package_members_and_seal_separately=True)
    descriptor=dict(stage_receipt_kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3',
        source_derivation_version=3,COMPLETE_NAME='STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json',
        source_receipt=dict(materialized=True,source_native_enabled=False,staged=False,dispatched=False),
        runtime_plan_changes_only=dict(enabled=True,staged=True),runtime_plan_source_native_enabled=False,runtime_plan_dispatched=False,
        added_receipt_binding_fields=dict(GROUP_PLAN_bytes='strict int length of the exact successfully written GROUP_PLAN UTF8 bytes',
            GROUP_PLAN_SHA256='SHA256 of those same exact bytes; not a hash of a reserialized projection'),
        original_plan_SHA='fixed original V8 plan SHA, not the new GROUP_PLAN hash',
        root_rule='explicit absolute absent non-symlink non-overlapping new_root; name == group_id; [A-Za-z0-9_]+; contains decimal strict seed; no fixed PREFIX',
        complete_original_metadata_validate_before_GROUP_PLAN_write=True,
        only_after_all_materials_copy_fsync_origin_retained_stream_checks=True,
        controller_or_dispatcher_or_resource_admission_created_here=False,actual_execution=False)
    index=json.loads(json.dumps(old_index));index.update(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V3',source_derivation_version=3,
        entry=dict(name='stage_good_expert_holdout_v3.py',**identity(new_raw)),previous_materializer_seal=previous,
        source_mirror=dict(name='SOURCE_MIRROR_INPUTS.json',**identity(encoded(mirror)),files_count=len(rows)),
        source_test_report=report,typed_runtime_publication=descriptor,
        operational_gap_review_source_only=[dict(workspace_relative=relative(GAP/name),bytes=pin[0],SHA256=pin[1]) for name,pin in GAP_PINS.items()])
    # Complete mapping/27/deferred/physics/teacher/resource fields survive verbatim.
    for key in ('flat_source_dir_complete20_mapping','original_worker_files','original_group_plan','source_index','wire','preserved_original_resource_logic','native_unknowns'):
        need(index[key]==old_index[key],'immutable upstream index evidence changed: '+key)
    for key in ('enabled','source_native_enabled','staged','dispatched'):need(index[key] is False,'SOURCE index activation differs')
    diff=dict(kind='GOOD_HOLDOUT_V3_EXACT_TWO_FUNCTION_SOURCE_DIFF',source_only=True,changed_functions=sorted(CHANGED),
        new_source_helpers=sorted(ADDED),unchanged_V2_functions=28,unchanged_original_V1_functions=22,whole_function_source_proofs=unchanged,
        old_cli=dict(workspace_relative=relative(PREVIOUS/'stage_good_expert_holdout_v2.py'),**identity(old_raw)),
        new_cli=dict(name='stage_good_expert_holdout_v3.py',**identity(new_raw)),
        actual_copy_hash_fsync_loop_complete_AST_equal=True,semantics=descriptor,
        parent_and_runtime_complete_bytes_unchanged=True,previous67_text_members_unchanged=True,
        original_prepare_metadata_main_put_once_and_all_resource_functions_unchanged=True,
        actual_prepare_preflight_stage_parent_worker_executed=False)
    return mirror,index,diff


def create_or_verify(name,value,verify):
    path=HERE/name;raw=encoded(value)
    if path.exists():need(path.read_bytes()==raw,'immutable NEW SOURCE differs: '+name)
    else:
        need(not verify,'missing sealed SOURCE metadata: '+name)
        with path.open('xb')as stream:stream.write(raw)


def main():
    need(sys.argv[1:] in ([],['--verify']),'only --verify is accepted');verify=sys.argv[1:]==['--verify']
    mirror,index,diff=metadata_products()
    for name,value in [('SOURCE_MIRROR_INPUTS.json',mirror),('SOURCE_INDEX.json',index),('WHITELIST_DIFF.json',diff)]:create_or_verify(name,value,verify)
    files=[dict(name=name,**identity(read_text(HERE/name))) for name in FILES]
    seal=dict(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_IMMUTABLE_SEAL_V3',status='SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE',
        enabled=False,source_native_enabled=False,staged=False,dispatched=False,actual_native_binding='UNKNOWN',
        root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root_of(files),files=files)
    create_or_verify('SOURCE_SEAL.json',seal,verify)
    print(json.dumps(dict(kind='SOURCE_GOOD_HOLDOUT_V3_SEAL_VERIFIED_NO_WRITES' if verify else 'SOURCE_GOOD_HOLDOUT_V3_SEALED_NOT_NATIVE',
        files=len(files),root_SHA256=seal['root_SHA256'],text_mirror_files=len(mirror['files']),NEW_tests=32,
        actual_prepare_preflight_stage_parent_worker_executed=False)))

if __name__=='__main__':main()
