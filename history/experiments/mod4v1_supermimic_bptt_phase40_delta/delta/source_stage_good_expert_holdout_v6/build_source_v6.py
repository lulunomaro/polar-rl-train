"""SOURCE text derivation, AST diff, manifests and two seals only; no consumer import."""
from pathlib import Path, PurePosixPath
import ast
import copy
import difflib
import hashlib
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R, W = HERE.parent, HERE.parent.parent
OLD = R/'source_stage_good_expert_holdout_v5'
COMP = R/'source_good_holdout_teacher_schema_v2'
BASE = R/'source_good_expert_holdout_subset_v1'
GUARD = R/'source_frozen_embedded_teacher_native_v1/producer_teacher_guard_v1.py'
OLD_SEAL = (1700, 'bf9c6dcfa98e2efe47844e13f55763aadfb20915361a139c0b87e564d4f84bad')
OLD_ROOT = '5e44c1870c0dc11fbe325194a12ddafd2715c977599f601c6a136353943db608'
GUARD_PIN = (8902, '855e13c931eb8b8711a15b829a4ca95b10692f11b6a68df73a1dece18f98ecf0')
RUNTIME_PIN = (56370, '4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f')
OVERLAY_PIN = (21075, '6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e')
DIAG = R/'reports/GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V2.json'
DIAG_PIN = (11764, '06faee44b02f910df7093eee19dc3bc1996f0b416fbd8945751aeed24706998a')
HISTORY = (R/'reports/GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V1.json',
           R/'reports/GOOD_HOLDOUT_D5_SEED20260929_ACTUAL_PREFLIGHT_V1.json')
COUNTS = ('physical_byte_opens', 'SHA_calculations', 'decodes')
FLAGS = ('whole_bootstrap_checkpoint_retained', 'original_PPO_optimizer_preserved_not_restored_to_new_BPTT')
KEYS = {'source_path','source_SHA','source_bytes','teacher_frozen',*COUNTS,*FLAGS}
CFILES = ('README.md','SCHEMA_DIFF.json','GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json',
          'producer_teacher_guard_v1.py','good_expert_holdout_runtime_v1.py')
FILES = ('README.md','SOURCE_INDEX.json','SOURCE_MIRROR_INPUTS.json','TEST_REPORT.json',
         'WHITELIST_DIFF.json','build_source_v6.py','stage_good_expert_holdout_v6.py','test_good_holdout_v6_source.py')
CHANGED = {'prepare','preflight_summary','stage'}
def need(ok, message):
    if not ok: raise ValueError(message)
def H(raw): return hashlib.sha256(raw).hexdigest()
def identity(raw): return dict(bytes=len(raw),SHA256=H(raw))
def encoded(value): return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
def relative(path): return Path(path).relative_to(W).as_posix()
def source_reference(value):
    rel=PurePosixPath(value.replace('\\','/')).relative_to(PurePosixPath('F:/RMPOLAR-RL'))
    need(all(x not in ('','.','..') for x in rel.parts),'exact SOURCE provenance path required')
    return W.joinpath(*rel.parts)
def read(path, pin=None):
    path=Path(path);relative(path)
    need(path.suffix.lower() in ('.py','.json','.md') and not path.is_symlink(),'explicit workspace SOURCE text only')
    raw=path.read_bytes()
    if pin is not None:need((len(raw),H(raw))==tuple(pin),'SOURCE pin differs: '+str(path))
    return raw
def record(path): return dict(workspace_relative=relative(path),**identity(read(path)))
def root_of(rows): return H(''.join(f"{x['name']}\t{x['bytes']}\t{x['SHA256']}\n" for x in sorted(rows,key=lambda x:x['name'])).encode())
def functions(raw): return {n.name:n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
def same_functions(old,new,changed):
    a,b=functions(old),functions(new);need(set(a)==set(b),'complete function set differs');proofs=[]
    actual={n for n in a if ast.dump(a[n],include_attributes=False)!=ast.dump(b[n],include_attributes=False)}
    need(actual==set(changed),'exact complete-function AST whitelist differs: '+str(actual))
    for name in sorted(set(a)-set(changed)):
        text=ast.get_source_segment(old.decode(),a[name]);need(text==ast.get_source_segment(new.decode(),b[name]),'whole function source changed: '+name)
        proofs.append(dict(function=name,whole_source_bytes=len(text.encode()),whole_source_SHA256=H(text.encode()),whole_AST_equal=True))
    return proofs
def replace_once(text,before,after):
    need(text.count(before)==1,'single exact SOURCE token required: '+before);return text.replace(before,after,1)
def baseline():
    seal=json.loads(read(OLD/'SOURCE_SEAL.json',OLD_SEAL))
    need(len(seal['files'])==8 and root_of(seal['files'])==seal['root_SHA256']==OLD_ROOT,'complete immutable D5 root differs')
    for row in seal['files']:
        need(PurePosixPath(row['name']).name==row['name'],'flat D5 source member required');read(OLD/row['name'],(row['bytes'],row['SHA256']))
    return seal
IDENTITY_BEFORE = "    need(row.get('original_bootstrap_teacher') == mother, 'explicit original mother identity differs from producer')"
IDENTITY_AFTER = """    original = row.get('original_bootstrap_teacher')
    need(type(original) is dict and original == producer['FINAL']['teacher']
         and set(original) == {'source_path', 'source_SHA', 'source_bytes', 'teacher_frozen',
             'physical_byte_opens', 'SHA_calculations', 'decodes', 'whole_bootstrap_checkpoint_retained',
             'original_PPO_optimizer_preserved_not_restored_to_new_BPTT'}
         and all(type(original[key]) is int and original[key] == 1
                 for key in ('physical_byte_opens', 'SHA_calculations', 'decodes'))
         and all(original[key] is True for key in ('whole_bootstrap_checkpoint_retained',
                 'original_PPO_optimizer_preserved_not_restored_to_new_BPTT'))
         and teacher_identity(original) == mother, 'explicit complete original mother identity/schema differs from producer')"""
def teacher_inputs():
    report=json.loads(read(DIAG,DIAG_PIN));receipt=report['receipt']
    need(report['returncode']==0 and json.loads(report['stdout'])==receipt,'actual metadata diagnostic differs')
    roles=receipt['roles'];need(set(roles)=={'CURB_PROTECTED878','SLOPE135'},'two fixed baselines required')
    for role,row in roles.items():
        teacher=row['final_teacher'];need(type(teacher) is dict and set(teacher)==KEYS and teacher==row['checkpoint_teacher_source'],'actual nine-field raw teacher differs')
        need(all(type(teacher[k]) is int and teacher[k]==1 for k in COUNTS) and all(teacher[k] is True for k in FLAGS),'actual history schema differs')
        need(len(row['current_stager_original_bootstrap_teacher'])==4,'historical D5 projection differs')
    return report

def component_products():
    old_guard=read(GUARD,GUARD_PIN);old_runtime=read(BASE/'good_expert_holdout_runtime_v1.py',RUNTIME_PIN)
    guard=replace_once(old_guard.decode(),IDENTITY_BEFORE,IDENTITY_AFTER).encode()
    runtime=replace_once(old_runtime.decode(),repr(GUARD_PIN),repr((len(guard),H(guard)))).encode()
    gp=same_functions(old_guard,guard,{'validate_reference_row'});rp=same_functions(old_runtime,runtime,set())
    old_index=json.loads(read(BASE/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json',OVERLAY_PIN));index=copy.deepcopy(old_index)
    changed=[]
    for row in index['overlay_entries']:
        name=row['relative']
        if name in ('producer_teacher_guard_v1.py','good_expert_holdout_runtime_v1.py'):
            raw=guard if name=='producer_teacher_guard_v1.py' else runtime
            row.update(path=str(COMP/name),**identity(raw));changed.append(name)
    need(len(index['overlay_entries'])==20 and len(changed)==2,'exactly two of complete20 required')
    index['teacher_schema_source_revision']=dict(kind='NEW_COMPLETE_TEACHER_METADATA_SCHEMA_SOURCE_REVISION_V2',revision=2,
        format_schema_kind_is_unchanged_not_new_artifact_identity=True,source_only=True,
        component_seal_workspace_relative=relative(COMP/'SOURCE_SEAL.json'),actual_native_binding='UNKNOWN')
    diff=dict(kind='GOOD_HOLDOUT_COMPLETE_TEACHER_SCHEMA_SOURCE_DIFF_V2',source_only=True,
        original_guard=record(GUARD),new_guard=dict(name='producer_teacher_guard_v1.py',**identity(guard)),
        guard_changed_functions=['validate_reference_row'],guard_unchanged_complete_functions=gp,
        derive_allstate_read_pins_identity_projection_and_return_evidence_unchanged=True,
        original_runtime=record(BASE/'good_expert_holdout_runtime_v1.py'),new_runtime=dict(name='good_expert_holdout_runtime_v1.py',**identity(runtime)),
        runtime_only_guard_PIN_tuple_changed=True,runtime_unchanged_complete_functions=rp,
        original_overlay_index=record(BASE/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json'),overlay_count=20,
        overlay_changed=sorted(changed),other18_complete_rows_unchanged=True,actor_physics_acceptance_resources_changed=False,
        raw_nine_field_equality_and_strict_four_identity_required=True,strict_history_counts_exact_int1=True,strict_history_flags_isTrue=True,
        subset_or_default_field_acceptance=False,
        guard_patch=''.join(difflib.unified_diff(old_guard.decode().splitlines(True),guard.decode().splitlines(True))),
        runtime_patch=''.join(difflib.unified_diff(old_runtime.decode().splitlines(True),runtime.decode().splitlines(True))))
    return {'producer_teacher_guard_v1.py':guard,'good_expert_holdout_runtime_v1.py':runtime,
            'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json':encoded(index),'SCHEMA_DIFF.json':encoded(diff)}
def derive_entry(old,index_raw):
    text=old.decode();changes=(
      ('V5 root canonical metadata; strict actual-wire identity; typed two-flag runtime publication','V6 complete raw teacher identity; root canonical metadata; strict actual-wire identity; typed two-flag runtime publication'),
      ('SOURCE_DERIVATION_VERSION = 5','SOURCE_DERIVATION_VERSION = 6'),
      ('INDEX_PIN = '+repr(OVERLAY_PIN),'INDEX_PIN = '+repr((len(index_raw),H(index_raw)))),
      ("original_bootstrap_teacher=guard.teacher_identity(producers[role]['FINAL']['teacher'])","original_bootstrap_teacher=copy.deepcopy(producers[role]['FINAL']['teacher'])"),
      ('SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V5','SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V6'),
      ('SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V5','SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V6'))
    for before,after in changes:text=replace_once(text,before,after)
    need(text.count('source_derivation_version=5')==2,'two SOURCE version labels required')
    return text.replace('source_derivation_version=5','source_derivation_version=6').encode()
def entry_diff(old,new,index_raw):
    need(derive_entry(old,index_raw)==new,'D6 entry changed outside exact literals and raw deepcopy')
    proofs=same_functions(old,new,CHANGED);need(len(proofs)==28,'28 complete D5 functions required')
    return dict(kind='GOOD_HOLDOUT_V6_MINIMAL_RAW_TEACHER_AND_PIN_SOURCE_DIFF',source_only=True,
        changed_functions=sorted(CHANGED),unchanged_D5_functions=28,whole_function_source_proofs=proofs,
        new_runtime_helpers=[],prepare_only_raw_teacher_deepcopy_changed=True,global_INDEX_PIN_exact_new_overlay=True,
        full_source_mappings_metadata_copy_fsync_typed_publish_main_resources_unchanged=True,
        actual_entry_executed=False,patch_utf8=''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True))))
def component_seal(verify):
    for name,raw in component_products().items():put(COMP/name,raw,verify)
    rows=[dict(name=name,**identity(read(COMP/name))) for name in CFILES]
    seal=dict(kind='SOURCE_ONLY_GOOD_HOLDOUT_TEACHER_SCHEMA_V2_IMMUTABLE_SEAL',status='SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE',
        enabled=False,source_native_enabled=False,staged=False,dispatched=False,actual_native_binding='UNKNOWN',
        root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root_of(rows),files=rows)
    put(COMP/'SOURCE_SEAL.json',encoded(seal),verify);return seal

def products():
    old_seal=baseline();teacher_inputs();index_raw=read(COMP/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json')
    old=read(OLD/'stage_good_expert_holdout_v5.py');new=read(HERE/'stage_good_expert_holdout_v6.py');diff=entry_diff(old,new,index_raw)
    previous=json.loads(read(OLD/'SOURCE_MIRROR_INPUTS.json'));old_rows=previous['files'];need(len(old_rows)==previous['files_count']==127,'complete D5 mirror127 required');positions={}
    for row in old_rows:
        rel=row['workspace_relative'];need(not PurePosixPath(rel).is_absolute() and all(x not in ('','.','..') for x in rel.split('/')) and rel not in positions,'old mirror path differs')
        read(W.joinpath(*PurePosixPath(rel).parts),(row['bytes'],row['SHA256']));positions[rel]=row
    additions=[OLD/x['name'] for x in old_seal['files']]+[OLD/'SOURCE_SEAL.json']+[COMP/x for x in CFILES]+[COMP/'SOURCE_SEAL.json',DIAG,*HISTORY]
    for path in additions:
        row=record(path);rel=row['workspace_relative'];need(rel not in positions or positions[rel]==row,'SOURCE mirror pin collision');positions[rel]=row
    need(all(positions[x['workspace_relative']]==x for x in old_rows),'old127 member changed');rows=[positions[k] for k in sorted(positions)]
    test=json.loads(read(HERE/'TEST_REPORT.json'));need(test['passed'] is True and test['tests_run']==8 and test['failures']==test['errors']==0 and all(v==0 for v in test['audit'].values()),'NEW small eight-test receipt required')
    need(all(test[k] is False for k in ('full_prepare_invoked','full_metadata_validate_executed','old_test_modules_imported_or_replayed','actual_guard_derive_invoked')),'test scope differs')
    mirror=dict(kind='COMPLETE_GOOD_HOLDOUT_V6_PINNED_TEXT_MIRROR_INPUTS',source_only=True,root_layout=previous['root_layout'],files=rows,files_count=len(rows),
        previous127_members_unchanged=True,added_files_count=len(rows)-127,raw_assets_static_banks_models_included=False,
        complete_runtime_materialization_proved=False,requires_new_source_package_members_and_seal_separately=True)
    index=copy.deepcopy(json.loads(read(OLD/'SOURCE_INDEX.json')));old_source_index=copy.deepcopy(index['source_index'])
    overlay=json.loads(index_raw);by_alias={x['relative']:x for x in overlay['overlay_entries']};mapping=index['flat_source_dir_complete20_mapping']
    for row in mapping:
        if row['relative'] in ('producer_teacher_guard_v1.py','good_expert_holdout_runtime_v1.py'):
            src=by_alias[row['relative']];row.update(source_workspace_relative=relative(source_reference(src['path'])),bytes=src['bytes'],SHA256=src['SHA256'])
    index.update(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V6',source_derivation_version=6,
        entry=dict(name='stage_good_expert_holdout_v6.py',**identity(new)),source_index=record(COMP/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json'),
        historical_original_overlay_source_index=old_source_index,
        previous_materializer_seal=dict(**record(OLD/'SOURCE_SEAL.json'),root_SHA256=OLD_ROOT,files=8),
        teacher_schema_component=dict(**record(COMP/'SOURCE_SEAL.json'),root_SHA256=json.loads(read(COMP/'SOURCE_SEAL.json'))['root_SHA256'],files=len(CFILES)),
        teacher_identity_actual_source_diagnostic=dict(**record(DIAG),parent_original_FINAL_reads_per_role=1,parent_counts_are_historical_not_local_read_counts=True,actual_model_read=False),
        historical_failed_operations_metadata=[record(x) for x in HISTORY],
        source_mirror=dict(name='SOURCE_MIRROR_INPUTS.json',**identity(encoded(mirror)),files_count=len(rows)),source_test_report=test,
        remaining_metadata_SOURCE_audit=dict(complete_source_inspection=True,only_additional_schema_conflict_was_guard_full9_vs_projection4=True,
            select_make_task_and_cache_all_use_same_reference_guard=True,runtime147_full_equality_and_frozen_unchanged=True,
            nested_embedded_reference_projection4_compares_consistently_or_only_SHA=True,canonical_core_has_no_guard_or_runtime_hardpin=True,
            canonical7a092_AppV6_Base_and_parent_fc445_bytes_unchanged=True,existing_12_module_cache_list_unchanged=True,
            extra_cache_or_hot_module_workaround=False,real_preflight_or_native_claim=False),
        raw_teacher_correction=dict(old_projection_keys=4,new_raw_keys=9,deepcopy_whole_raw_object=True,no_flags_invented=True,
            source_container_and_mother_identities_remain_separate=True,four_actual_before_stage_failures_preserved=True,old_RC127_diagnostic_preserved=True))
    index['typed_runtime_publication'].update(stage_receipt_kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V6',source_derivation_version=6)
    need(all(index[k] is False for k in ('enabled','source_native_enabled','staged','dispatched')),'SOURCE flags differ')
    diff.update(old_cli=record(OLD/'stage_good_expert_holdout_v5.py'),new_cli=dict(name='stage_good_expert_holdout_v6.py',**identity(new)),
        previous127_text_members_unchanged=True,component_diff=record(COMP/'SCHEMA_DIFF.json'))
    return mirror,index,diff

def put(path,raw,verify):
    path=Path(path);need(path.parent in (HERE,COMP),'only the two NEW SOURCE directories may be written')
    if path.exists():need(read(path)==raw,'immutable NEW SOURCE differs: '+str(path))
    else:
        need(not verify,'missing sealed SOURCE: '+str(path));path.parent.mkdir(exist_ok=True)
        with path.open('xb') as stream:stream.write(raw)
def main():
    need(sys.argv[1:] in (['--derive'],['--seal'],['--verify']),'choose --derive, --seal or --verify only');baseline();teacher_inputs();mode=sys.argv[1]
    if mode=='--derive':
        values=component_products()
        for name,raw in values.items():put(COMP/name,raw,False)
        raw=derive_entry(read(OLD/'stage_good_expert_holdout_v5.py'),values['GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json']);put(HERE/'stage_good_expert_holdout_v6.py',raw,False)
        print(json.dumps(dict(kind='SOURCE_D6_AND_TEACHER_SCHEMA_DERIVED_NO_CONSUMER_EXECUTED',entry=identity(raw),component_outputs=len(values))));return
    verify=mode=='--verify';cs=component_seal(verify);mirror,index,diff=products()
    for name,value in zip(('SOURCE_MIRROR_INPUTS.json','SOURCE_INDEX.json','WHITELIST_DIFF.json'),(mirror,index,diff)):put(HERE/name,encoded(value),verify)
    rows=[dict(name=name,**identity(read(HERE/name))) for name in FILES]
    seal=dict(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_IMMUTABLE_SEAL_V6',status='SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE',
        enabled=False,source_native_enabled=False,staged=False,dispatched=False,actual_native_binding='UNKNOWN',
        root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root_of(rows),files=rows)
    put(HERE/'SOURCE_SEAL.json',encoded(seal),verify)
    print(json.dumps(dict(kind='SOURCE_GOOD_HOLDOUT_V6_TWO_SEALS_VERIFIED_NO_WRITES' if verify else 'SOURCE_GOOD_HOLDOUT_V6_TWO_COMPONENTS_SEALED_NOT_NATIVE',
        files=len(rows),component_files=len(cs['files']),text_mirror_files=len(mirror['files']),added_text_files=mirror['added_files_count'],
        root_SHA256=seal['root_SHA256'],component_root_SHA256=cs['root_SHA256'],actual_entry_executed=False)))
if __name__=='__main__':main()
