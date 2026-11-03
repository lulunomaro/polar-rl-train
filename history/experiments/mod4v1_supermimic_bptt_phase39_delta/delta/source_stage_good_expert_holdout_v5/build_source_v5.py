"""Small SOURCE packager only: --derive, --seal, --verify. No materializer import/call."""
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
OLD = R/'source_stage_good_expert_holdout_v4'
OLD_SEAL = (2033, 'a90f11f25b17d8a84caf5681d5ad8a5179f38b781e71118e161a0e5b1a0261a9')
OLD_ROOT = '9a472be4e70e8cf6f9acf31c4bea31557297358dde7c4c59c972c1ffde5cba84'
DIAG = R/'reports/GOOD_HOLDOUT_CONCENTRATED_ACTUAL_SOURCE_INPUT_DIAGNOSTIC_V1.json'
DIAG_PIN = (49207, '31e4ab2668701db00fad59ea94badf09d3e8fe8975cc8b70f35aad73f77767c0')
AUDIT = R/'source_good_holdout_d4_input_assumption_audit_v1'
ROOTS = R/'discovery/good_holdout_runtime_root_metadata_v2'
ROOT_PINS = {'CURB_PROTECTED878': (4814, '671f77ddef5fbd79de8dafc54213ff754cfc70ac5a9d9611680e9c76c021cfc5'),
             'SLOPE135': (5390, 'f9a0a42c6b1390e38013a410e454da4a9d63569d47f014c3b6f6ea4ca7615b41')}
CHANGED = {'prepare', 'preflight_summary', 'stage'}
FILES = ('README.md','SOURCE_INDEX.json','SOURCE_MIRROR_INPUTS.json','TEST_REPORT.json',
         'WHITELIST_DIFF.json','build_source_v5.py','stage_good_expert_holdout_v5.py','test_good_holdout_v5_source.py')
def need(ok, msg):
    if not ok: raise ValueError(msg)
def H(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode('utf-8')
def identity(raw): return dict(bytes=len(raw), SHA256=H(raw))
def relative(path): return Path(path).relative_to(W).as_posix()
def source_reference(value):
    # Exact captured SOURCE provenance prefix only; never normalize runtime wire.
    rel=PurePosixPath(value.replace('\\','/')).relative_to(PurePosixPath('F:/RMPOLAR-RL'))
    need(all(x not in ('','.','..') for x in rel.parts), 'SOURCE provenance relative differs')
    return W.joinpath(*rel.parts)
def read(path, pin=None):
    path = Path(path); relative(path)
    need(path.suffix in ('.py','.json','.md') and not path.is_symlink(), 'only explicit workspace SOURCE text: '+str(path))
    raw = path.read_bytes()
    if pin is not None: need((len(raw), H(raw)) == tuple(pin), 'SOURCE pin differs: '+str(path))
    return raw
def record(path): return dict(workspace_relative=relative(path), **identity(read(path)))
def root_of(rows): return H(''.join(f"{x['name']}\t{x['bytes']}\t{x['SHA256']}\n" for x in sorted(rows,key=lambda x:x['name'])).encode())
def baseline():
    seal = json.loads(read(OLD/'SOURCE_SEAL.json', OLD_SEAL))
    need(len(seal['files']) == 10 and root_of(seal['files']) == seal['root_SHA256'] == OLD_ROOT, 'complete D4 root differs')
    for row in seal['files']:
        need(PurePosixPath(row['name']).name == row['name'], 'D4 member must be flat')
        read(OLD/row['name'], (row['bytes'],row['SHA256']))
    return seal
REPLACEMENTS = (
    ('V4 strict actual-wire identity; typed two-flag runtime publication', 'V5 root canonical metadata; strict actual-wire identity; typed two-flag runtime publication'),
    ('SOURCE_DERIVATION_VERSION = 4', 'SOURCE_DERIVATION_VERSION = 5'),
    ("canonical_rel = 'runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json'", "canonical_rel = 'E1_CANONICAL_SOURCE_METADATA.json'"),
    ('SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V4', 'SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V5'),
    ('SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V4', 'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V5'))
def derive(old):
    text = old.decode('utf-8')
    for before, after in REPLACEMENTS:
        need(text.count(before) == 1, 'single derivation token required: '+before); text = text.replace(before,after,1)
    need(text.count('source_derivation_version=4') == 2, 'two SOURCE version fields required')
    return text.replace('source_derivation_version=4','source_derivation_version=5').encode('utf-8')
def functions(raw): return {n.name:n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
def analyse(old, new):
    need(derive(old) == new, 'D5 changed beyond root canonical_rel and exact SOURCE labels')
    a,b = functions(old),functions(new); dump = lambda n:ast.dump(n,include_attributes=False)
    need(set(a)==set(b) and {n for n in a if dump(a[n])!=dump(b[n])}==CHANGED, 'exact three-function whitelist required')
    proofs=[]
    for name in sorted(set(a)-CHANGED):
        text=ast.get_source_segment(old.decode(),a[name]);other=ast.get_source_segment(new.decode(),b[name])
        need(text==other, 'whole D4 function source changed: '+name)
        proofs.append(dict(function=name,whole_source_bytes=len(text.encode()),whole_source_SHA256=H(text.encode()),whole_AST_equal=True))
    need(len(proofs)==28, '28 unchanged complete functions required')
    return dict(kind='GOOD_HOLDOUT_V5_MINIMAL_ROOT_METADATA_SOURCE_DIFF',source_only=True,changed_functions=sorted(CHANGED),
        new_runtime_helpers=[],unchanged_D4_functions=len(proofs),whole_function_source_proofs=proofs,
        prepare_only_root_canonical_rel_changed=True,strict_canonical_equals_role_unchanged=True,
        stage_and_preflight_only_SOURCE_version_labels_changed=True,
        full_copy_fsync_metadata_main_source_mappings_guard_resources_unchanged=True,
        typed_publication_helper_complete_source_unchanged=True,actual_entry_executed=False,
        patch_utf8=''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),
            fromfile='D4/stage_good_expert_holdout_v4.py',tofile='D5/stage_good_expert_holdout_v5.py')))
def input_evidence():
    report=json.loads(read(DIAG,DIAG_PIN));receipt=report['receipt'];captures=report['local_SOURCE_captures']
    need(report['returncode']==0 and receipt['status']=='PASS' and receipt['errors']==[] and json.loads(report['stdout'])==receipt, 'actual SOURCE diagnostic failed')
    need(receipt['Gate1']=='UNKNOWN' and receipt['stage2_GO'] is False and receipt['predicates_are_whole_original_pinned_functions'] is True, 'diagnostic boundary differs')
    need(len(captures)==receipt['core_source_files_read']==receipt['core_source_files_expected']==15 and receipt['upstream_metadata_files_read']==7, '15 core + 7 metadata diagnostic required')
    rows=receipt['input_rows'];need(len(rows)==22 and len({x['path'] for x in rows})==22 and all(x['physical_byte_reads']==1 for x in rows) and receipt['all_original_paths_read_once'] is True, 'parent original read-once evidence differs')
    core={x['relative_to_native']:x for x in rows if x['core_source_input']};need(len(core)==15,'unique core15 required')
    paths=[DIAG];vendor=[]
    for row in captures:
        path=source_reference(row['local_path']);rel=path.relative_to(R/'discovery/good_holdout_concentrated_source_inputs_v1').as_posix()
        data=read(path,(row['bytes'],row['SHA256']));need(identity(data)=={k:core[rel][k] for k in ('bytes','SHA256')}, 'capture/original row mismatch')
        ast.parse(data) if path.suffix=='.py' else json.loads(data)
        if '/supermimic_vendor_v2/' in rel: vendor.append(dict(relative=path.name,bytes=len(data),SHA=H(data)))
        paths.append(path)
    need(len(vendor)==7 and H(json.dumps(sorted(vendor,key=lambda x:x['relative']),sort_keys=True,separators=(',',':')).encode())==receipt['vendor']['SHA']=='ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0', 'complete vendor7 capture differs')
    for role in ROOT_PINS:
        path=ROOTS/(role+'_E1_CANONICAL_SOURCE_METADATA.json');need(json.loads(read(path,ROOT_PINS[role]))['canonical']==role, 'actual ROOT canonical differs');paths.append(path)
    audit=json.loads(read(AUDIT/'SOURCE_AUDIT.json',(13431,'cd3c1380f31d5cfbce381233112e86f21fe1c19a9f19108c23cd6c21e31948d1')))
    read(AUDIT/'SOURCE_AUDIT.md',(14239,'6a44fd92cd97415612fa63854b0ccd620fcb753e86fc1e97fb5cd7fe3150e3b0'))
    paths += [AUDIT/'SOURCE_AUDIT.json',AUDIT/'SOURCE_AUDIT.md']
    for group in ('source_routing_evidence','diagnostic_source_inputs'):
        for row in audit[group]:
            path=source_reference(row['path']);read(path,(row['bytes'],row['SHA256']));paths.append(path)
    return paths,report

def products():
    seal=baseline();old=read(OLD/'stage_good_expert_holdout_v4.py');new=read(HERE/'stage_good_expert_holdout_v5.py');diff=analyse(old,new)
    old_index=json.loads(read(OLD/'SOURCE_INDEX.json'));old_mirror=json.loads(read(OLD/'SOURCE_MIRROR_INPUTS.json'))
    old_rows=old_mirror['files'];need(len(old_rows)==old_mirror['files_count']==92,'complete D4 mirror92 required');positions={}
    for row in old_rows:
        rel=row['workspace_relative'];need(not PurePosixPath(rel).is_absolute() and all(x not in ('','.','..') for x in rel.split('/')) and rel not in positions,'old mirror path differs')
        read(W.joinpath(*PurePosixPath(rel).parts),(row['bytes'],row['SHA256']));positions[rel]=row
    paths,report=input_evidence();paths += [OLD/x['name'] for x in seal['files']]+[OLD/'SOURCE_SEAL.json']
    for path in paths:
        row=record(path);rel=row['workspace_relative'];need(rel not in positions or positions[rel]==row,'mirror pin collision');positions[rel]=row
    rows=[positions[k] for k in sorted(positions)];need(all(positions[x['workspace_relative']]==x for x in old_rows),'old92 changed')
    test=json.loads(read(HERE/'TEST_REPORT.json'));need(test['passed'] is True and test['tests_run']==12 and test['failures']==test['errors']==0 and all(x==0 for x in test['audit'].values()),'small NEW12 receipt required')
    need(test['full_prepare_invoked'] is False and test['old_test_modules_imported_or_replayed'] is False and test['full_metadata_validate_executed'] is False,'regression scope differs')
    mirror=dict(kind='COMPLETE_GOOD_HOLDOUT_V5_PINNED_TEXT_MIRROR_INPUTS',source_only=True,root_layout=old_mirror['root_layout'],
        files=rows,files_count=len(rows),previous92_members_unchanged=True,added_files_count=len(rows)-len(old_rows),
        raw_assets_static_banks_models_included=False,complete_runtime_materialization_proved=False,requires_new_source_package_members_and_seal_separately=True)
    index=copy.deepcopy(old_index);index.update(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V5',source_derivation_version=5,
        entry=dict(name='stage_good_expert_holdout_v5.py',**identity(new)),
        previous_materializer_seal=dict(workspace_relative=relative(OLD/'SOURCE_SEAL.json'),root_SHA256=OLD_ROOT,files=len(seal['files'])),
        source_mirror=dict(name='SOURCE_MIRROR_INPUTS.json',**identity(encoded(mirror)),files_count=len(rows)),source_test_report=test,
        root_canonical_metadata=[dict(role=role,**record(ROOTS/(role+'_E1_CANONICAL_SOURCE_METADATA.json'))) for role in ROOT_PINS],
        historical_input_audit_source_only=[record(AUDIT/name) for name in ('SOURCE_AUDIT.md','SOURCE_AUDIT.json')],
        source_input_diagnostic=dict(**record(DIAG),parent_reported_status='PASS',parent_core_source_files=15,parent_closure_metadata_files=7,
            local_captures=[record(source_reference(x['local_path'])) for x in report['local_SOURCE_captures']],
            parent_read_once_counts_are_historical_not_local_read_counts=True,source_modules_not_executed_here=True,
            original_pending_audit_condition_resolved_by_this_later_diagnostic=True,native_pass_claim=False),
        canonical_path_correction=dict(old='runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json',new='E1_CANONICAL_SOURCE_METADATA.json',
            strict_canonical_equals_role_unchanged=True,generic_role_is_not_an_alias=True,three_actual_before_stage_failures_preserved=True))
    index['typed_runtime_publication'].update(stage_receipt_kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V5',source_derivation_version=5)
    need(all(index[k] is False for k in ('enabled','source_native_enabled','staged','dispatched')),'SOURCE flags changed')
    diff.update(old_cli=record(OLD/'stage_good_expert_holdout_v4.py'),new_cli=dict(name='stage_good_expert_holdout_v5.py',**identity(new)),previous92_text_members_unchanged=True)
    return mirror,index,diff

def put(name,raw,verify):
    path=HERE/name
    if path.exists(): need(path.read_bytes()==raw,'immutable NEW SOURCE differs: '+name)
    else:
        need(not verify,'missing sealed SOURCE: '+name)
        with path.open('xb') as stream:stream.write(raw)
def main():
    need(sys.argv[1:] in (['--derive'],['--seal'],['--verify']),'choose --derive, --seal or --verify only')
    baseline();mode=sys.argv[1]
    if mode=='--derive':
        raw=derive(read(OLD/'stage_good_expert_holdout_v4.py'));put('stage_good_expert_holdout_v5.py',raw,False)
        print(json.dumps(dict(kind='SOURCE_D5_DERIVED_NO_ENTRY_EXECUTED',**identity(raw))));return
    verify=mode=='--verify';mirror,index,diff=products()
    for name,value in zip(('SOURCE_MIRROR_INPUTS.json','SOURCE_INDEX.json','WHITELIST_DIFF.json'),(mirror,index,diff)):put(name,encoded(value),verify)
    rows=[dict(name=name,**identity(read(HERE/name))) for name in FILES]
    seal=dict(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_IMMUTABLE_SEAL_V5',status='SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE',
        enabled=False,source_native_enabled=False,staged=False,dispatched=False,actual_native_binding='UNKNOWN',
        root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root_of(rows),files=rows)
    put('SOURCE_SEAL.json',encoded(seal),verify)
    print(json.dumps(dict(kind='SOURCE_GOOD_HOLDOUT_V5_SEAL_VERIFIED_NO_WRITES' if verify else 'SOURCE_GOOD_HOLDOUT_V5_SEALED_NOT_NATIVE',
        files=len(rows),text_mirror_files=len(mirror['files']),root_SHA256=seal['root_SHA256'],actual_entry_executed=False)))
if __name__=='__main__':main()
