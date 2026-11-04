"""Fixed SOURCE derivation/seal only. Never call prepare, stage, main, native or old tests.
Historical mirror rows are preserved as metadata; actual reports/discovery/FINAL are never opened.
"""
from __future__ import annotations
import argparse,ast,copy,hashlib,json
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent;R=HERE.parent;W=R.parent
OLD=R/'source_stage_good_expert_holdout_v6';PREV=R/'source_good_holdout_teacher_schema_v2'
COMP=R/'source_good_holdout_case_final_contract_v3';AUDIT=R/'source_good_holdout_final_size_contract_audit_v1'
OLD_SEAL=(1699,'c3d6164ee5edc8fc05dbf2741bd99b3df447b1cbe9f0abf652f82cb0111d952d')
OLD_ROOT='976a1370e4ab6550a004c4ec621694e228a61174bf94eeac68ac797decff4bc2'
PREV_SEAL=(1247,'4951037f9df73e05d1ffdb16f66697e6e99c6ecdcfb2be862c7f323d9eaa97c1')
PREV_ROOT='4b3076d0cb187bd88f22699996f6b8dea9ec8650707ff75fbea204ac95ce9301'
RUNTIME='good_expert_holdout_runtime_v1.py';INDEX='GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V3.json'
CASE_FINAL_MAX=2097152
RCHANGED={'close_original_eval_resources','evaluate_waited_eval_case','grade_closed_reference_group'}
SCHANGED={'preflight_summary','stage'}
CFILES=('README.md','CONTRACT_DIFF.json',INDEX,RUNTIME)
FILES=('README.md','SOURCE_INDEX.json','SOURCE_MIRROR_INPUTS.json','TEST_REPORT.json','WHITELIST_DIFF.json','build_source_v7.py','stage_good_expert_holdout_v7.py','test_good_holdout_v7_source.py')
ANCHOR='ALLOWED_SEEDS = (20260929, 20260930)\n'
INSERT=ANCHOR+'CASE_FINAL_MAX = 2097152\n'
CALLS=(("        final, raw = _metadata(case / 'FINAL.json')","        final, raw = _metadata(case / 'FINAL.json', maximum=CASE_FINAL_MAX)"),
       ("            case_final, _ = _base._metadata(case / 'FINAL.json')","            case_final, _ = _base._metadata(case / 'FINAL.json', maximum=CASE_FINAL_MAX)"))
def need(ok,message):
    if not ok:raise ValueError(message)
def H(raw):return hashlib.sha256(raw).hexdigest()
def identity(raw):return dict(bytes=len(raw),SHA256=H(raw))
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def relative(path):return Path(path).relative_to(W).as_posix()
def source_path(value):
    rel=PurePosixPath(value.replace('\\','/')).relative_to(PurePosixPath('F:/RMPOLAR-RL'))
    need(all(p not in ('','.','..') for p in rel.parts),'explicit SOURCE provenance required');return W.joinpath(*rel.parts)
def eligible(path):
    path=Path(path);rel=Path(relative(path))
    return path.suffix.lower() in ('.py','.json','.md') and not {'reports','discovery'}.intersection(rel.parts) and path.name!='FINAL.json'
def read(path,pin=None):
    path=Path(path);need(eligible(path),'SOURCE only: no actual report/discovery/FINAL/model path');need(not path.is_symlink(),'SOURCE symlink differs');raw=path.read_bytes()
    if pin is not None:need((len(raw),H(raw))==tuple(pin),'SOURCE pin differs: '+str(path))
    return raw
def record(path):return dict(workspace_relative=relative(path),**identity(read(path)))
def root_of(rows):return H(''.join(f"{r['name']}\t{r['bytes']}\t{r['SHA256']}\n" for r in sorted(rows,key=lambda r:r['name'])).encode())
def verify_bundle(folder,pin,root):
    seal=json.loads(read(folder/'SOURCE_SEAL.json',pin));need(root_of(seal['files'])==seal['root_SHA256']==root,'complete SOURCE root differs')
    for row in seal['files']:need(PurePosixPath(row['name']).name==row['name'],'flat source member required');read(folder/row['name'],(row['bytes'],row['SHA256']))
    return seal
def baseline():return verify_bundle(OLD,OLD_SEAL,OLD_ROOT),verify_bundle(PREV,PREV_SEAL,PREV_ROOT)
def functions(raw):return {n.name:n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
def same_functions(old,new,changed):
    a,b=functions(old),functions(new);need(set(a)==set(b),'complete function set changed');actual={k for k in a if ast.dump(a[k],include_attributes=False)!=ast.dump(b[k],include_attributes=False)};need(actual==set(changed),'function whitelist differs: '+str(actual));rows=[]
    for k in sorted(set(a)-set(changed)):
        text=ast.get_source_segment(old.decode(),a[k]);need(text==ast.get_source_segment(new.decode(),b[k]),'whole source differs: '+k);rows.append(dict(function=k,whole_source_SHA256=H(text.encode()),whole_AST_equal=True))
    return rows
def replace_once(text,before,after):need(text.count(before)==1,'exact single derivation token differs: '+before);return text.replace(before,after,1)
def component_products():
    old=read(PREV/RUNTIME);text=replace_once(old.decode(),ANCHOR,INSERT)
    for before,after in CALLS:need(text.count(before)==(2 if before==CALLS[0][0] else 1),'exact case-FINAL count differs');text=text.replace(before,after)
    runtime=text.encode();reverse=text
    for before,after in reversed(CALLS):reverse=reverse.replace(after,before)
    reverse=replace_once(reverse,INSERT,ANCHOR);need(reverse.encode()==old,'reverse complete bytes differ from D6')
    unchanged=same_functions(old,runtime,RCHANGED)
    oldclasses={n.name:ast.get_source_segment(old.decode(),n) for n in ast.parse(old).body if isinstance(n,ast.ClassDef)}
    classes={n.name:ast.get_source_segment(text,n) for n in ast.parse(runtime).body if isinstance(n,ast.ClassDef)};need(classes==oldclasses,'complete classes changed')
    index=json.loads(read(PREV/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json'));previous=copy.deepcopy(index['overlay_entries']);rows=[r for r in index['overlay_entries'] if r['relative']==RUNTIME];need(len(rows)==1,'single runtime overlay required')
    rows[0].update(path='F:/RMPOLAR-RL/'+relative(COMP/RUNTIME),**identity(runtime));need(sum(a!=b for a,b in zip(previous,index['overlay_entries']))==1,'only runtime overlay may change')
    index['case_final_contract_source_revision']=dict(kind='NEW_FINITE_CASE_FINAL_SOURCE_CONTRACT_REVISION_V3',revision=3,CASE_FINAL_MAX=CASE_FINAL_MAX,format_schema_kind_is_unchanged_not_new_artifact_identity=True,source_only=True,component_seal_workspace_relative=relative(COMP/'SOURCE_SEAL.json'),actual_native_binding='UNKNOWN')
    diff=dict(kind='EXACT_D6_TO_CASE_FINAL_V3_SOURCE_DIFF',before=record(PREV/RUNTIME),after=identity(runtime),CASE_FINAL_MAX=CASE_FINAL_MAX,changed_functions=sorted(RCHANGED),unchanged_complete_functions=unchanged,unchanged_complete_classes=sorted(classes),reverse_full_bytes_equal_D6=True,other_overlay_rows_unchanged=19,canonical_metadata_default_unchanged=262144,group_MAX_unchanged=8388608,other_task_plan_and_close_receipt_readers_unchanged=True,AppV6_Base_helper_close_arguments_intent_predicates_unchanged=True)
    return {RUNTIME:runtime,INDEX:encoded(index),'CONTRACT_DIFF.json':encoded(diff)}
def entry_products(component):
    old=read(OLD/'stage_good_expert_holdout_v6.py');text=old.decode();ip=identity(component[INDEX]);oldip=identity(read(PREV/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json'))
    changes=[('"""V6 complete raw teacher identity;','"""V7 finite case-FINAL contract; complete raw teacher identity;'),(f"INDEX_PIN = ({oldip['bytes']}, '{oldip['SHA256']}')",f"INDEX_PIN = ({ip['bytes']}, '{ip['SHA256']}')"),('SOURCE_DERIVATION_VERSION = 6','SOURCE_DERIVATION_VERSION = 7'),('SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V6','SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V7'),('SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V6','SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V7')]
    for before,after in changes:text=replace_once(text,before,after)
    need(text.count('source_derivation_version=6')==2,'two typed revision fields required');text=text.replace('source_derivation_version=6','source_derivation_version=7');entry=text.encode();reverse=text.replace('source_derivation_version=7','source_derivation_version=6')
    for before,after in reversed(changes):reverse=replace_once(reverse,after,before)
    need(reverse.encode()==old,'reverse complete stager bytes differ from D6');proof=same_functions(old,entry,SCHANGED)
    diff=dict(kind='EXACT_D6_TO_V7_MATERIALIZER_SOURCE_DIFF',changed_functions=sorted(SCHANGED),unchanged_complete_functions=proof,reverse_full_bytes_equal_D6=True,prepare_full9dict_copyfsync_fullmetadata_original27_plus3_assets_vendor_parent_resources_unchanged=True,runtime_delta=json.loads(component['CONTRACT_DIFF.json']),stage_kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V7',enabled=False,staged=False,dispatched=False)
    return entry,encoded(diff)
def put(path,raw):
    path=Path(path);need(path.parent in (HERE,COMP),'writes confined to two NEW SOURCE folders');need(not (path.parent/'SOURCE_SEAL.json').exists(),'sealed SOURCE is immutable');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
def seal_value(folder,names,kind):
    rows=[dict(name=n,**identity(read(folder/n))) for n in names]
    return dict(kind=kind,status='SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE',enabled=False,source_native_enabled=False,staged=False,dispatched=False,actual_native_binding='UNKNOWN',root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root_of(rows),files=rows)
def products(component,cseal,entry):
    oldmir=json.loads(read(OLD/'SOURCE_MIRROR_INPUTS.json'));rows={x['workspace_relative']:copy.deepcopy(x) for x in oldmir['files']};need(len(rows)==len(oldmir['files'])==145,'complete prior145 declaration differs');observed=[];inherited=[]
    for row in oldmir['files']:
        p=W/row['workspace_relative']
        if eligible(p):read(p,(row['bytes'],row['SHA256']));observed.append(row['workspace_relative'])
        else:inherited.append(copy.deepcopy(row))
    additions=[OLD/n for n in ('README.md','SOURCE_INDEX.json','SOURCE_MIRROR_INPUTS.json','TEST_REPORT.json','WHITELIST_DIFF.json','build_source_v6.py','stage_good_expert_holdout_v6.py','test_good_holdout_v6_source.py','SOURCE_SEAL.json')]
    additions += [AUDIT/'SOURCE_AUDIT.md',AUDIT/'SOURCE_AUDIT.json']
    audit=json.loads(read(AUDIT/'SOURCE_AUDIT.json',(16755,'b648a00aa3f1c2d090b63b58f257825f5be5353c454e841452b11c692b9b800b')))
    additions += [W/x['workspace_relative'] for x in audit['source_pins'] if x['id'].startswith('CFF_')]
    for p in additions:
        row=record(p);key=row['workspace_relative'];need(key not in rows or rows[key]==row,'inherited row changed');rows[key]=row
    for name in CFILES:
        row=record(COMP/name);rows[row['workspace_relative']]=row
    sr=dict(workspace_relative=relative(COMP/'SOURCE_SEAL.json'),**identity(encoded(cseal)));rows[sr['workspace_relative']]=sr
    for row in oldmir['files']:need(rows[row['workspace_relative']]==row,'prior145 SOURCE declaration changed')
    mirror=dict(kind='COMPLETE_GOOD_HOLDOUT_V7_PINNED_TEXT_MIRROR_INPUTS',source_only=True,root_layout=oldmir['root_layout'],files=sorted(rows.values(),key=lambda x:x['workspace_relative']),prior_mirror_rows=145,prior_rows_rehashed_SOURCE_only=len(observed),prior_rows_inherited_metadata_not_opened=inherited,no_actual_report_discovery_or_FINAL_opened=True)
    index=json.loads(read(OLD/'SOURCE_INDEX.json'));index.update(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V7',source_derivation_version=7,entry=dict(name='stage_good_expert_holdout_v7.py',**identity(entry)),previous_materializer_seal=dict(**record(OLD/'SOURCE_SEAL.json'),root_SHA256=OLD_ROOT,files=8),historical_D6_active_source_index=copy.deepcopy(index['source_index']),source_index=dict(workspace_relative=relative(COMP/INDEX),**identity(component[INDEX])))
    newindex=json.loads(component[INDEX]);byrel={x['relative']:x for x in newindex['overlay_entries']}
    for row in index['flat_source_dir_complete20_mapping']:
        if row['relative']==RUNTIME:row.update(source_workspace_relative=relative(COMP/RUNTIME),**identity(component[RUNTIME]))
        else:need((row['bytes'],row['SHA256'])==(byrel[row['relative']]['bytes'],byrel[row['relative']]['SHA256']),'unchanged19 active pin differs')
    index['typed_runtime_publication'].update(stage_receipt_kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V7',source_derivation_version=7)
    index['case_final_contract_component']=dict(**sr,root_SHA256=cseal['root_SHA256'],files=len(CFILES),CASE_FINAL_MAX=CASE_FINAL_MAX)
    index['case_final_SOURCE_tests']=dict(**record(HERE/'TEST_REPORT.json'),only_own_synthetic_metadata_and_FakeApp=True,native_or_quality_pass=False,CFF_new_packet_selector_tests_delegated_to_parent=True)
    index['mirror_verification_scope']=dict(prior_rows=145,rehashed_SOURCE_only=len(observed),inherited_metadata_not_opened=len(inherited),inherited_rows_preserved_exact=True,actual_reports_FINALs_opened=0,actual_discovery_capture_opens=0)
    return encoded(index),encoded(mirror)
def main():
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    for name in ('derive','seal','verify'):mode.add_argument('--'+name,action='store_true')
    args=parser.parse_args();baseline();component=component_products();entry,diff=entry_products(component)
    if args.derive:
        for name,raw in component.items():put(COMP/name,raw)
        put(HERE/'stage_good_expert_holdout_v7.py',entry);put(HERE/'WHITELIST_DIFF.json',diff)
        print(json.dumps(dict(kind='SOURCE_DERIVED_V7_NO_CONSUMER',runtime=identity(component[RUNTIME]),index=identity(component[INDEX]),entry=identity(entry),actual_reports_or_FINAL_opens=0)));return
    for name,raw in component.items():need(read(COMP/name)==raw,'derived component differs: '+name)
    need(read(HERE/'stage_good_expert_holdout_v7.py')==entry and read(HERE/'WHITELIST_DIFF.json')==diff,'derived stager differs')
    test=json.loads(read(HERE/'TEST_REPORT.json'));need(test['passed'] is True and test['tests_run']==12,'NEW12 target tests required')
    cseal=seal_value(COMP,CFILES,'SOURCE_ONLY_GOOD_HOLDOUT_CASE_FINAL_CONTRACT_V3_IMMUTABLE_SEAL');index,mirror=products(component,cseal,entry)
    if args.verify:
        verify_bundle(COMP,(len(encoded(cseal)),H(encoded(cseal))),cseal['root_SHA256'])
        need(read(COMP/'SOURCE_SEAL.json')==encoded(cseal),'component seal bytes differ')
        need(read(HERE/'SOURCE_INDEX.json')==index and read(HERE/'SOURCE_MIRROR_INPUTS.json')==mirror,'fixed current metadata differs')
        own=seal_value(HERE,FILES,'SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_IMMUTABLE_SEAL_V7');need(read(HERE/'SOURCE_SEAL.json')==encoded(own),'main seal differs');print(json.dumps(dict(kind='SOURCE_GOOD_HOLDOUT_V7_TWO_SEALS_VERIFIED_NO_WRITES',component_root=cseal['root_SHA256'],root=own['root_SHA256'],mirror_files=len(json.loads(mirror)['files']),inherited_not_opened=len(json.loads(mirror)['prior_rows_inherited_metadata_not_opened']),actual_report_FINAL_opens=0,writes=0)));return
    put(HERE/'SOURCE_INDEX.json',index);put(HERE/'SOURCE_MIRROR_INPUTS.json',mirror)
    put(COMP/'SOURCE_SEAL.json',encoded(cseal));own=seal_value(HERE,FILES,'SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_IMMUTABLE_SEAL_V7');put(HERE/'SOURCE_SEAL.json',encoded(own));print(json.dumps(dict(kind='SOURCE_ONLY_V7_TWO_SEALS_FIXED',component=cseal,main=own,mirror_files=len(json.loads(mirror)['files'])),indent=2))
if __name__=='__main__':main()
