"""V4 D6 SOURCE inventory only; no actual reports or producer entry calls.

145 external references = 136 full SOURCE texts + nine unread declarations.
Old127 and added18 are separate; logical154 is not flat20 or SDK evidence.
"""
from pathlib import Path, PurePosixPath
import ast
import json
import good_holdout_contract as C

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
WORKSPACE=BASE.parent
GOOD=BASE/'source_good_expert_holdout_subset_v1'
COMPONENT=BASE/'source_good_holdout_teacher_schema_v2'
GOOD_INDEX=COMPONENT/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json'
GOOD_SEAL=GOOD/'GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json'
GOOD_SEAL_PIN=(2876,'f4fe8185efb87f079f1b9ff00e20391e366dd96f8f4c0fc6f459d41f68fb6ae0')
GOOD_ROOT='032c431b844aedc02bffad76549b9516f92e5cfd06cce6194e47d5f4451c7534'
COMPONENT_SEAL_PIN=(1247,'4951037f9df73e05d1ffdb16f66697e6e99c6ecdcfb2be862c7f323d9eaa97c1')
COMPONENT_ROOT='4b3076d0cb187bd88f22699996f6b8dea9ec8650707ff75fbea204ac95ce9301'
OLD_GOOD_INDEX_PIN=(21075,'6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e')
OLD_PLAN_REL='mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json'
WIRE_REL=BASE.name+'/discovery/good_holdout_original_plan_wire_v1/ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json'
DIAG_REL=BASE.name+'/reports/GOOD_HOLDOUT_ORIGINAL_PLAN_WIRE_VS_PUBLISHED_DIAGNOSIS_V1.json'
INPUT_DIAG_REL=BASE.name+'/reports/GOOD_HOLDOUT_CONCENTRATED_ACTUAL_SOURCE_INPUT_DIAGNOSTIC_V1.json'
REPORT_DECLARATIONS={
 OLD_PLAN_REL:C.PUBLISHED_ORIGINAL_PLAN_PIN,
 DIAG_REL:(1459,'673398d112f60f084b9c945a747d0d13625e43487291549d9d4dfca0a3991b38'),
 INPUT_DIAG_REL:(49207,'31e4ab2668701db00fad59ea94badf09d3e8fe8975cc8b70f35aad73f77767c0'),
 BASE.name+'/reports/A1_ADMISSION2_QUALITY_BOUNDARY_CLOSED_TRUTH_V1.json':(193581,'67830ccb9f7cc24e94f29e1bfe364265225732ae6049efa481793ddfc24b26d1'),
 BASE.name+'/reports/GOOD_HOLDOUT_RUNTIME_ROOT_CANONICAL_METADATA_DIAGNOSIS_V2.json':(3180,'f3c2bab54a38baddf4d2c1bbce49ac7b2df6abe8210828b8a833f4ca4d00ecd2'),
 BASE.name+'/reports/GOOD_HOLDOUT_SELECTED_RUNTIME_CANONICAL_METADATA_DIAGNOSIS_V1.json':(1094,'8e0ba4fa24f6efc021f2e1e9bbd2d9964455bf326a861fe5b4a57ad508009c57')}
B2_AUDIT_REL=BASE.name+'/source_phase1_passive_sensor_capture_v2/source_api.py'
AUDIT_REFERENCES={k:v for k,v in REPORT_DECLARATIONS.items() if k not in (OLD_PLAN_REL,DIAG_REL,INPUT_DIAG_REL)}
AUDIT_REFERENCES[B2_AUDIT_REL]=(31456,'a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62')
TEACHER_DIAG_REL=BASE.name+'/reports/GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V2.json'
NEW_REPORT_DECLARATIONS={
 TEACHER_DIAG_REL:(11764,'06faee44b02f910df7093eee19dc3bc1996f0b416fbd8945751aeed24706998a'),
 BASE.name+'/reports/GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V1.json':(305,'bb5031e71bbe5e60caeccd92abe357e4d15a32e7e33ab5b13d42925734f6a830'),
 BASE.name+'/reports/GOOD_HOLDOUT_D5_SEED20260929_ACTUAL_PREFLIGHT_V1.json':(48566,'467f35299f883dc1a8d95b93b1a4bd557c18a7d12972f4e45f6184074688a4a5')}
REPORT_DECLARATIONS.update(NEW_REPORT_DECLARATIONS)
ROOT_PINS={
 'CURB_PROTECTED878':(4814,'671f77ddef5fbd79de8dafc54213ff754cfc70ac5a9d9611680e9c76c021cfc5'),
 'SLOPE135':(5390,'f9a0a42c6b1390e38013a410e454da4a9d63569d47f014c3b6f6ea4ca7615b41')}
OLD_CONTROLLER=BASE/'source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py'
OLD_CONTROLLER_SHA='95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831'
CONNECTOR=WORKSPACE/'mod4v1_experts_fulldr_rm70_20261101/project_connector.py'
CONNECTOR_SHA='623599cf014fe39b46f1a10bc4e858c498860578f4b277ac81a802ede2da09d6'
TEXT_EXTENSIONS={'.py','.json','.md','.txt','.yml','.yaml'}
MAX_SOURCE=2*1024*1024


def source_path(value):
    C.need(type(value) in (str,type(Path())) or isinstance(value,Path),'SOURCE path required')
    path=Path(value)
    C.need(path.is_absolute() and '..' not in path.parts,'absolute lexical SOURCE path required')
    C.need('reports' not in (p.lower() for p in path.parts),'actual reports never opened by SOURCE inventory')
    C.need(path.suffix.lower() in TEXT_EXTENSIONS and 'budget' not in path.name.lower(),'only small SOURCE text, no model/raw/ledger')
    C.need(path.is_relative_to(WORKSPACE),'SOURCE outside named workspace')
    relative=path.relative_to(WORKSPACE)
    C.need(relative.parts[0] in (BASE.name,'mod4v1_experts_fulldr_rm70_20261101'),'unrelated project')
    cursor=path
    while cursor!=WORKSPACE:
        C.need(not cursor.is_symlink(),'SOURCE symlink rejected');cursor=cursor.parent
    return path


def checked_source(value,expected_bytes=None,expected_sha=None):
    path=source_path(value);size=path.stat().st_size
    C.need(0<size<=MAX_SOURCE,'small SOURCE text bound')
    blob=path.read_bytes();C.need(len(blob)==size,'SOURCE changed during read')
    sha=C.H(blob)
    if expected_bytes is not None:C.need(type(expected_bytes)is int and size==expected_bytes,'SOURCE byte length differs: '+str(path))
    if expected_sha is not None:C.need(C.sha(expected_sha) and sha==expected_sha,'SOURCE SHA differs: '+str(path))
    if path.suffix.lower()=='.py':ast.parse(blob.decode('utf-8-sig'),filename=str(path))
    return dict(path=path.as_posix(),bytes=size,SHA256=sha,full_bytes_verified=True,Python_AST_parsed=path.suffix.lower()=='.py'),blob


def member_root(rows):
    C.need(type(rows)is list and rows and len({r.get('name')for r in rows})==len(rows),'unique complete seal member list')
    records=[]
    for row in rows:
        name=row.get('name');C.need(type(name)is str and PurePosixPath(name).name==name and name not in ('.','..'),'flat sealed SOURCE member')
        C.need(type(row.get('bytes'))is int and row['bytes']>0 and C.sha(row.get('SHA256')),'valid sealed SOURCE identity')
        records.append(name+'\t'+str(row['bytes'])+'\t'+row['SHA256']+'\n')
    return C.H(''.join(sorted(records)).encode())


def checked_seal(path,pin,expected_members,expected_root=None):
    seal_row,blob=checked_source(path,*pin);seal=json.loads(blob)
    C.need(len(seal.get('files',[]))==expected_members,'whole seal member count differs')
    root=member_root(seal['files']);C.need(root==seal.get('root_SHA256'),'whole seal root differs')
    if expected_root is not None:C.need(root==expected_root,'fixed upstream SOURCE root differs')
    checked=[]
    for row in seal['files']:
        item,_=checked_source(Path(path).parent/row['name'],row['bytes'],row['SHA256']);checked.append(dict(item,name=row['name']))
    return dict(seal=seal_row,root_SHA256=root,members=checked,count=len(checked),source_members_unchanged=True)


def mirror_rows(mirror):
    rows=mirror.get('files')
    C.need(type(rows)is list and len(rows)==145 and type(mirror.get('files_count'))is int and mirror['files_count']==145 and mirror.get('kind')=='COMPLETE_GOOD_HOLDOUT_V6_PINNED_TEXT_MIRROR_INPUTS','whole fixed D6 mirror145 required')
    seen=set();allowed=[];declarations=[]
    for row in rows:
        value=row.get('workspace_relative');C.need(type(value)is str and value not in seen,'unique workspace SOURCE reference');seen.add(value)
        path=PurePosixPath(value)
        C.need(not path.is_absolute() and str(path)==value and '..'not in path.parts and '\\'not in value and ':'not in value,'lexical workspace SOURCE reference')
        C.need(type(row.get('bytes'))is int and row['bytes']>0 and C.sha(row.get('SHA256')),'complete mirror SOURCE identity')
        if 'reports'in(p.lower()for p in path.parts):
            C.need(value in REPORT_DECLARATIONS and (row['bytes'],row['SHA256'])==REPORT_DECLARATIONS[value],'only nine exact unread report declarations')
            declarations.append(dict(row,verification='PUBLISHED_SOURCE_DECLARATION_ONLY',full_bytes_verified=False,actual_file_stat_or_read=False,audit_reference_only=value in AUDIT_REFERENCES))
        else:
            source_path(WORKSPACE/value);allowed.append(row)
    C.need(len(allowed)==136 and len(declarations)==9 and {r['workspace_relative']for r in declarations}==set(REPORT_DECLARATIONS),'D6 full136/declaration9 split differs')
    return allowed,declarations


def check_good_overlay(index):
    rows=index.get('overlay_entries')
    C.need(type(rows)is list and len(rows)==20,'whole active good20 required')
    actual={};checked=[]
    for row in rows:
        alias=row.get('relative');C.need(type(alias)is str and alias not in actual,'unique good20 alias')
        item,_=checked_source(row['path'],row['bytes'],row['SHA256']);checked.append(dict(item,relative=alias));actual[alias]=(row['bytes'],row['SHA256'])
    C.need(actual==C.OVERLAY_PINS,'exact active good20 alias identities differ')
    C.need(actual[C.PARENT_NAME]==C.PARENT_PIN and actual['good_expert_holdout_runtime_v1.py']==C.RUNTIME_PIN,'exact active parent/runtime identity required')
    return checked


def flat_mapping(entries,raw_by_flat_name=None):
    """SOURCE memory invariant; original target source_mappings is never run."""
    C.need(type(entries)is list and len(entries)==20,'exact active flat20 entries')
    names=set();aliases=set();result=[]
    for row in entries:
        value=row.get('path');alias=row.get('relative')
        C.need(type(value)is str and type(alias)is str and alias in C.OVERLAY_PINS and alias not in aliases,'exact unique active source alias')
        name=value.replace('\\','/').rsplit('/',1)[-1]
        C.need(name not in ('','.','..') and name not in names,'unique normalized flat basename')
        C.need((row.get('bytes'),row.get('SHA256'))==C.OVERLAY_PINS[alias],'active flat20 pin differs')
        names.add(name);aliases.add(alias)
        if raw_by_flat_name is not None:
            C.need(type(raw_by_flat_name)is dict and name in raw_by_flat_name,'basename-keyed flat bytes required, not F provenance path')
            raw=raw_by_flat_name[name]
            C.need(type(raw)is bytes and (len(raw),C.H(raw))==C.OVERLAY_PINS[alias],'whole flat SOURCE bytes differ')
        result.append(dict(relative=alias,flat_name=name,bytes=row['bytes'],SHA256=row['SHA256']))
    C.need(aliases==set(C.OVERLAY_PINS),'all active twenty aliases required')
    if raw_by_flat_name is not None:C.need(set(raw_by_flat_name)==names,'exact flat20 memory payload required')
    return result


def validate_component(index,materializer_index):
    C.need(index.get('kind')=='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_C878_S135_INDEX_V1','unchanged FORMAT kind required')
    revision=index.get('teacher_schema_source_revision',{})
    expected=dict(kind='NEW_COMPLETE_TEACHER_METADATA_SCHEMA_SOURCE_REVISION_V2',revision=2,format_schema_kind_is_unchanged_not_new_artifact_identity=True,source_only=True,component_seal_workspace_relative=BASE.name+'/source_good_holdout_teacher_schema_v2/SOURCE_SEAL.json',actual_native_binding='UNKNOWN')
    C.need(type(revision.get('revision'))is int and revision==expected,'exact NEW component revision, not old FORMAT identity')
    active=dict(workspace_relative=GOOD_INDEX.relative_to(WORKSPACE).as_posix(),bytes=C.INDEX_PIN[0],SHA256=C.INDEX_PIN[1])
    C.need(materializer_index.get('source_index')==active,'D6 must activate NEW21472 component20 index')
    component=dict(workspace_relative=expected['component_seal_workspace_relative'],bytes=COMPONENT_SEAL_PIN[0],SHA256=COMPONENT_SEAL_PIN[1],root_SHA256=COMPONENT_ROOT,files=5)
    C.need(materializer_index.get('teacher_schema_component')==component,'fixed component five plus seal identity')
    old_ref=dict(workspace_relative=(GOOD/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json').relative_to(WORKSPACE).as_posix(),bytes=OLD_GOOD_INDEX_PIN[0],SHA256=OLD_GOOD_INDEX_PIN[1])
    C.need(materializer_index.get('historical_original_overlay_source_index')==old_ref,'old21075 index is historical only')
    mappings=flat_mapping(index.get('overlay_entries'));actual=materializer_index.get('flat_source_dir_complete20_mapping',[])
    C.need(type(actual)is list and len(actual)==20 and {r['relative']:{k:r[k]for k in ('relative','flat_name','bytes','SHA256')}for r in actual}=={r['relative']:r for r in mappings},'active20 paths normalize to flat basenames')
    C.need(C.OVERLAY_PINS['producer_teacher_guard_v1.py']==(9635,'a839ea0ca1a76b19bff1eaf304eafc1c16e54144fe370e40186aa8c07789028c') and C.RUNTIME_PIN==(56370,'7455449db33ef539a7d8517876a36a4c291d57ebaa1c361943af2343b2370ee2'),'strict raw9 guard and runtime tuple binding')
    return dict(active_index=active,component=component,historical_index=old_ref,format_schema_is_not_artifact_identity=True,flat20=mappings,provenance_F_paths_not_dereferenced_by_target_memory_checker=True,actual_source_mappings_executed=False)


def validate_D6_provenance(index):
    C.need(index.get('kind')=='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V6' and type(index.get('source_derivation_version'))is int and index['source_derivation_version']==6,'fixed D6 SOURCE index kind/version required')
    wire=dict(workspace_relative=WIRE_REL,bytes=C.ORIGINAL_PLAN_PIN[0],SHA256=C.ORIGINAL_PLAN_PIN[1]);published=dict(workspace_relative=OLD_PLAN_REL,bytes=C.PUBLISHED_ORIGINAL_PLAN_PIN[0],SHA256=C.PUBLISHED_ORIGINAL_PLAN_PIN[1])
    C.need(index.get('original_group_plan_wire')==wire and index.get('original_group_plan')==published,'distinct raw wire and published identities')
    d=index.get('original_group_plan_wire_identity',{})
    C.need(d.get('runtime_ORIGINAL_PLAN_PIN')==dict(bytes=C.ORIGINAL_PLAN_PIN[0],SHA256=C.ORIGINAL_PLAN_PIN[1]) and d.get('PUBLISHED_ORIGINAL_PLAN_PIN')==dict(bytes=C.PUBLISHED_ORIGINAL_PLAN_PIN[0],SHA256=C.PUBLISHED_ORIGINAL_PLAN_PIN[1]) and d.get('decoded_canonical_SHA256')==C.ORIGINAL_PLAN_CANONICAL_SHA256,'raw/canonical triple differs')
    C.need(d.get('canonical_equivalence_does_not_relax_raw_wire_pin')is True and d.get('whole_decoded_values_equal')is True and d.get('literal_wire_bytes_equal')is False,'canonical equality never replaces raw pin')
    C.need(index.get('wire_identity_diagnosis_source_only')==dict(workspace_relative=DIAG_REL,bytes=REPORT_DECLARATIONS[DIAG_REL][0],SHA256=REPORT_DECLARATIONS[DIAG_REL][1],executed=False),'wire diagnostic is a fixed unread declaration')
    p=index.get('typed_runtime_publication',{})
    C.need(p.get('stage_receipt_kind')==C.STAGE_KIND and type(p.get('source_derivation_version'))is int and p['source_derivation_version']==6 and p.get('COMPLETE_NAME')==C.STAGE_NAME,'strict D6 existing typed publication')
    C.need(p.get('original_plan_wire_pin')==dict(bytes=C.ORIGINAL_PLAN_PIN[0],SHA256=C.ORIGINAL_PLAN_PIN[1]) and p.get('published_original_plan_SOURCE_reference')==published,'existing raw publication identities')
    C.need(p.get('source_receipt')==dict(materialized=True,source_native_enabled=False,staged=False,dispatched=False) and p.get('runtime_plan_changes_only')==dict(enabled=True,staged=True),'SOURCE False versus whole runtime True layers')
    C.need(index.get('canonical_path_correction')==dict(old='runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json',new='E1_CANONICAL_SOURCE_METADATA.json',strict_canonical_equals_role_unchanged=True,generic_role_is_not_an_alias=True,three_actual_before_stage_failures_preserved=True),'strict ROOT correction unchanged')
    correction=dict(old_projection_keys=4,new_raw_keys=9,deepcopy_whole_raw_object=True,no_flags_invented=True,source_container_and_mother_identities_remain_separate=True,four_actual_before_stage_failures_preserved=True,old_RC127_diagnostic_preserved=True)
    C.need(index.get('raw_teacher_correction')==correction,'complete9 versus projection4 SOURCE correction')
    diag=index.get('teacher_identity_actual_source_diagnostic',{});expected=dict(workspace_relative=TEACHER_DIAG_REL,bytes=NEW_REPORT_DECLARATIONS[TEACHER_DIAG_REL][0],SHA256=NEW_REPORT_DECLARATIONS[TEACHER_DIAG_REL][1],parent_original_FINAL_reads_per_role=1,parent_counts_are_historical_not_local_read_counts=True,actual_model_read=False)
    C.need(type(diag.get('parent_original_FINAL_reads_per_role'))is int and diag==expected,'parent FINAL once is history, not local report access')
    historical=index.get('historical_failed_operations_metadata',[])
    C.need(type(historical)is list and len(historical)==2 and {r['workspace_relative']:(r['bytes'],r['SHA256'])for r in historical}=={k:v for k,v in NEW_REPORT_DECLARATIONS.items()if k!=TEACHER_DIAG_REL},'both historical failed-operation declarations')
    return dict(runtime_original_plan=wire,published_SOURCE_reference=published,decoded_canonical_SHA256=C.ORIGINAL_PLAN_CANONICAL_SHA256,canonical_equivalence_relaxes_raw_pin=False,parent_actual_diagnosis_execution_not_reclassified=True,published_plan_or_diagnosis_read_here=False,full_teacher9_source_correction=correction,full_teacher_actual_native_binding='UNKNOWN',actual_original_prepare_or_guard_executed=False)


def canonical_metadata(role,raw):
    """Only SOURCE metadata identity, never full original prepare."""
    C.need(role in C.REQUESTED,'exact selected canonical role');value=json.loads(raw)
    C.need(type(value)is dict and value.get('canonical')==role,'SOURCE ROOT canonical differs from exact role')
    return dict(canonical=value['canonical'],generic_role_field=value.get('role'),kind=value.get('kind'),actual_prepare_executed=False)


def capture_provenance(index,current,verified):
    rows=index.get('root_canonical_metadata',[])
    C.need(len(rows)==2 and {r.get('role')for r in rows}==set(C.REQUESTED),'exact two ROOT SOURCE identities')
    roots=[]
    for row in rows:
        role=row['role'];rel=BASE.name+'/discovery/good_holdout_runtime_root_metadata_v2/'+role+'_E1_CANONICAL_SOURCE_METADATA.json'
        C.need(row==dict(role=role,workspace_relative=rel,bytes=ROOT_PINS[role][0],SHA256=ROOT_PINS[role][1]) and current.get(rel)=={k:v for k,v in row.items()if k!='role'},'fixed ROOT capture pin')
        item,raw=checked_source(WORKSPACE/rel,*ROOT_PINS[role]);roots.append(dict(item,role=role,metadata=canonical_metadata(role,raw)))
    diagnostic=index.get('source_input_diagnostic',{});C.need((diagnostic.get('workspace_relative'),diagnostic.get('bytes'),diagnostic.get('SHA256'))==(INPUT_DIAG_REL,*REPORT_DECLARATIONS[INPUT_DIAG_REL]),'fixed parent diagnostic declaration')
    captures=diagnostic.get('local_captures',[]);prefix=BASE.name+'/discovery/good_holdout_concentrated_source_inputs_v1/roles/'
    expected={prefix+role+'/'+name for role in C.REQUESTED for name in ('TASK.json','INSTALL_MANIFEST.json','worker_sources/native_supermimic_bridge.py','worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py')}
    expected|={prefix+'E3/worker_sources/supermimic_vendor_v2/'+name for name in ('__init__.py','contract.py','geometry.py','learner.py','logging.py','networks.py','replay.py')}
    C.need(len(captures)==15 and {r.get('workspace_relative')for r in captures}==expected,'exact SOURCE core15 capture list')
    for row in captures:C.need(current.get(row['workspace_relative'])==row and row['workspace_relative']in verified,'SOURCE capture pin not independently verified')
    C.need(diagnostic.get('parent_read_once_counts_are_historical_not_local_read_counts')is True and diagnostic.get('source_modules_not_executed_here')is True and diagnostic.get('native_pass_claim')is False,'SOURCE versus parent history scope')
    return dict(root_metadata2=roots,core15_full_SOURCE=[verified[r['workspace_relative']]for r in captures],core15_python_AST_count=sum(r['workspace_relative'].endswith('.py')for r in captures),parent_diagnostic_reference={k:diagnostic[k]for k in ('workspace_relative','bytes','SHA256','parent_reported_status')},parent_report_unread_here=True,parent_once_counts_not_local_once_counts=True,producer_guard_or_full_metadata_validate_executed_here=False)


def build_sources():
    C.require_final_pins()
    index_row,index_blob=checked_source(GOOD_INDEX,*C.INDEX_PIN);component_index=json.loads(index_blob);good20=check_good_overlay(component_index)
    component=checked_seal(COMPONENT/'SOURCE_SEAL.json',COMPONENT_SEAL_PIN,5,COMPONENT_ROOT);original14=checked_seal(GOOD_SEAL,GOOD_SEAL_PIN,14,GOOD_ROOT)
    old_row,old_blob=checked_source(GOOD/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json',*OLD_GOOD_INDEX_PIN);old_index=json.loads(old_blob)
    old_entries={r['relative']:r for r in old_index['overlay_entries']};new_entries={r['relative']:r for r in component_index['overlay_entries']}
    C.need(set(old_entries)==set(new_entries) and {k for k in new_entries if new_entries[k]!=old_entries[k]}=={'producer_teacher_guard_v1.py','good_expert_holdout_runtime_v1.py'},'exactly two NEW overlay rows, other18 fieldwise unchanged')
    C.need({k:v for k,v in old_index.items()if k!='overlay_entries'}=={k:v for k,v in component_index.items()if k not in ('overlay_entries','teacher_schema_source_revision')},'all original non-overlay FORMAT fields unchanged')
    sp=C.STAGER_SOURCE_PINS;stage_dir=Path(sp['seal']['path']).parent;stager=checked_seal(stage_dir/'SOURCE_SEAL.json',(sp['seal']['bytes'],sp['seal']['SHA256']),8,sp['content_root_SHA256']);fixed={}
    for key in ('source','index','mirror'):
        row=sp[key];item,blob=checked_source(row['path'],row['bytes'],row['SHA256']);fixed[key]=item
        if key=='mirror':mirror=json.loads(blob)
        if key=='index':materializer_index=json.loads(blob)
    allowed,declarations=mirror_rows(mirror);provenance=validate_D6_provenance(materializer_index);active=validate_component(component_index,materializer_index);verified={}
    for row in allowed:
        item,_=checked_source(WORKSPACE/row['workspace_relative'],row['bytes'],row['SHA256']);verified[row['workspace_relative']]=dict(item,workspace_relative=row['workspace_relative'],audit_reference_only=row['workspace_relative']in AUDIT_REFERENCES)
    current={r['workspace_relative']:r for r in mirror['files']};prior={}
    for version,count,root in ((2,9,None),(3,10,'1cdd8c72dfdc9fbb3b75f4068f53e8f489d7d558c79a637f39597efae8e765cd'),(4,10,'9a472be4e70e8cf6f9acf31c4bea31557297358dde7c4c59c972c1ffde5cba84'),(5,8,'5e44c1870c0dc11fbe325194a12ddafd2715c977599f601c6a136353943db608')):
        path=BASE/('source_stage_good_expert_holdout_v'+str(version))/'SOURCE_SEAL.json';row=current[path.relative_to(WORKSPACE).as_posix()];prior['D'+str(version)]=checked_seal(path,(row['bytes'],row['SHA256']),count,root)
    _,old_raw=checked_source(BASE/'source_stage_good_expert_holdout_v5/SOURCE_MIRROR_INPUTS.json',32862,'b3c1a0f63c175d0ec344a59c9f89f0b780e0085dde6f2f6f867b63fd91579fe5');previous=json.loads(old_raw)['files']
    C.need(len(previous)==127 and all(current.get(r['workspace_relative'])==r for r in previous),'previous whole127 declaration fields unchanged')
    additions={k:v for k,v in current.items()if k not in {r['workspace_relative']for r in previous}};expected=[]
    for group in (prior['D5'],component):
        for item in group['members']+[group['seal']]:expected.append(dict(workspace_relative=Path(item['path']).relative_to(WORKSPACE).as_posix(),bytes=item['bytes'],SHA256=item['SHA256']))
    expected.extend(dict(workspace_relative=k,bytes=v[0],SHA256=v[1])for k,v in NEW_REPORT_DECLARATIONS.items())
    C.need(len(expected)==18 and additions=={r['workspace_relative']:r for r in expected},'exact new18 = D5nine + component6 + reports3')
    capture=capture_provenance(materializer_index,current,verified);wire_row,wire_raw=checked_source(WORKSPACE/WIRE_REL,*C.ORIGINAL_PLAN_PIN);canonical=json.dumps(json.loads(wire_raw),sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    C.need(C.H(canonical)==C.ORIGINAL_PLAN_CANONICAL_SHA256,'actual SOURCE wire raw and canonical exact')
    provenance.update(wire_full_bytes_verified=wire_row,wire_decoded_canonical_verified=True,published_decoded_equivalence_not_reexecuted_here=True);routes={}
    for version,pin,root in ((1,(2748,'55b4be771d2c50065bd5b95480e296bdbb456d683ca885607cfc61f7c8b37d0c'),'a41453e48df40880a66c7afb9644698df528f6f26d5da062a1ce5e10ad23d2c8'),(2,(2767,'265e24d512e991862087338c3f6fa2525c5a3ad3b90bf08140e3f0b2d4301e5f'),'e9bc7f48651a6020db7abf73b3d6de7222d433712b507408a9330cf82e35c51d'),(3,(2819,'715b7e8c68b749755308a1a009a9e0a4a7c83c06255f9c1babe5da8da15e31d3'),'c22982e6996a6f46ea8a033a8373190a4bcb99c096b742001f64d0165ac1c78d')):
        routes['V'+str(version)]=checked_seal(BASE/('source_good_holdout_lifecycle_routes_v'+str(version))/'SOURCE_SEAL.json',pin,12,root)
    ctrl,_=checked_source(OLD_CONTROLLER,expected_sha=OLD_CONTROLLER_SHA);connector,_=checked_source(CONNECTOR,expected_sha=CONNECTOR_SHA);own,_=checked_source(HERE/'good_holdout_parent_actual_wait_controller_v1.py',*C.CONTROLLER_SOURCE_PIN)
    return dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_INVENTORY_V4',scope='D6_COMPONENT_ACTIVE20_FULL_SOURCE136_NINE_UNREAD_REPORT_DECLARATIONS',good_index=index_row,active_component20=good20,component5_seal=component,original_good14_seal=original14,historical_original_index=old_row,D6_final8_seal=stager,D6_fixed_refs=fixed,prior_materializer_seals=prior,prior_routes12_seals=routes,
        D6_mirror=dict(declared=145,full_allowed_SOURCE_verifications=136,unread_report_declarations=declarations,verified=list(verified.values()),all145_full_bytes_read=False,previous127_fields_unchanged=True,additions18_full_SOURCE=15,additions18_report_declarations=3,additional18=sorted(additions.values(),key=lambda r:r['workspace_relative']),audit_only_prior_last4=[dict(workspace_relative=k,bytes=v[0],SHA256=v[1],active_dependency=False,imported_or_executed=False,full_bytes_verified=k==B2_AUDIT_REL)for k,v in AUDIT_REFERENCES.items()],logical154_is_not_flat20=True),
        D6_active_component=active,D6_raw_provenance=provenance,D6_SOURCE_capture_provenance=capture,original_9595_controller=ctrl,original_connect72_SOURCE_only=connector,own_controller=own,runtime_aliases=20,other18_overlay_rows_unchanged=True,original_runtime_whole_bytes_unchanged=False,runtime30_functions_unchanged_only_guard_tuple_SOURCE_claim=True,original_parent_unchanged=True,old_sealed_sources_unchanged=True,groups_are_not_disjoint_sum=True,
        actual_prepare_preflight_stage_main=False,actual_controller_reader_or_collector=False,actual_SSH_SDK_GPU_Torch=False,actual_model_raw_reports_C_or_lock_access=False,actual_native_binding='UNKNOWN',actual_quality=None,stage2_GO=False)


def verify_sources():
    recorded=json.loads((HERE/'SOURCE_PINS.json').read_bytes());current=build_sources()
    C.need(recorded==current,'SOURCE inventory differs from full allowed text/declaration split')
    return current


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--build',action='store_true');args=parser.parse_args();value=build_sources()if args.build else verify_sources()
    if args.build:
        with(HERE/'SOURCE_PINS.json').open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    print(json.dumps(dict(runtime_aliases=value['runtime_aliases'],full_SOURCE=136,report_declarations_only=9,added_full_SOURCE=15,added_report_declarations=3,actual_entry_or_report_reads=False)))
