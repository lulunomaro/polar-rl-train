"""V3 SOURCE inventory only; no actual reports or producer/runtime entry calls.

127 external references are 121 allowed full texts plus six unread declarations.
Old92 and new35 are accounted independently; none is a flat20 payload or SDK proof.
"""
from pathlib import Path, PurePosixPath
import ast
import json
import good_holdout_contract as C

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
WORKSPACE=BASE.parent
GOOD=BASE/'source_good_expert_holdout_subset_v1'
GOOD_INDEX=GOOD/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json'
GOOD_SEAL=GOOD/'GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json'
GOOD_SEAL_PIN=(2876,'f4fe8185efb87f079f1b9ff00e20391e366dd96f8f4c0fc6f459d41f68fb6ae0')
GOOD_ROOT='032c431b844aedc02bffad76549b9516f92e5cfd06cce6194e47d5f4451c7534'
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
    C.need(type(rows)is list and len(rows)==127 and type(mirror.get('files_count'))is int and mirror['files_count']==127 and mirror.get('kind')=='COMPLETE_GOOD_HOLDOUT_V5_PINNED_TEXT_MIRROR_INPUTS','whole fixed D5 mirror127 required')
    seen=set();allowed=[];declarations=[]
    for row in rows:
        value=row.get('workspace_relative');C.need(type(value)is str and value not in seen,'unique workspace SOURCE reference');seen.add(value)
        path=PurePosixPath(value)
        C.need(not path.is_absolute() and str(path)==value and '..'not in path.parts and '\\'not in value and ':'not in value,'lexical workspace SOURCE reference')
        C.need(type(row.get('bytes'))is int and row['bytes']>0 and C.sha(row.get('SHA256')),'complete mirror SOURCE identity')
        if 'reports'in(p.lower()for p in path.parts):
            C.need(value in REPORT_DECLARATIONS and (row['bytes'],row['SHA256'])==REPORT_DECLARATIONS[value],'only six exact report declarations without report access')
            declarations.append(dict(row,verification='PUBLISHED_SOURCE_DECLARATION_ONLY',full_bytes_verified=False,actual_file_stat_or_read=False,audit_reference_only=value in AUDIT_REFERENCES))
        else:
            source_path(WORKSPACE/value)
            allowed.append(row)
    C.need(len(allowed)==121 and len(declarations)==6 and {r['workspace_relative']for r in declarations}==set(REPORT_DECLARATIONS),'D5 full121/declaration6 split differs')
    return allowed,declarations


def check_good_overlay(index):
    rows=index.get('overlay_entries')
    C.need(type(rows)is list and len(rows)==20,'whole original good20 required')
    actual={};checked=[]
    for row in rows:
        alias=row.get('relative');C.need(type(alias)is str and alias not in actual,'unique good20 alias')
        item,_=checked_source(row['path'],row['bytes'],row['SHA256']);checked.append(dict(item,relative=alias));actual[alias]=(row['bytes'],row['SHA256'])
    C.need(actual==C.OVERLAY_PINS,'exact original good20 alias identities differ')
    C.need(actual[C.PARENT_NAME]==C.PARENT_PIN and actual['good_expert_holdout_runtime_v1.py']==C.RUNTIME_PIN,'original good parent/runtime changed')
    return checked


def validate_D5_provenance(index):
    C.need(index.get('kind')=='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V5' and type(index.get('source_derivation_version'))is int and index['source_derivation_version']==5,'fixed D5 SOURCE index kind/version required')
    expected_wire=dict(workspace_relative=WIRE_REL,bytes=C.ORIGINAL_PLAN_PIN[0],SHA256=C.ORIGINAL_PLAN_PIN[1])
    expected_published=dict(workspace_relative=OLD_PLAN_REL,bytes=C.PUBLISHED_ORIGINAL_PLAN_PIN[0],SHA256=C.PUBLISHED_ORIGINAL_PLAN_PIN[1])
    C.need(index.get('original_group_plan_wire')==expected_wire and index.get('original_group_plan')==expected_published,'distinct actual wire and published SOURCE identities required')
    d=index.get('original_group_plan_wire_identity',{})
    C.need(d.get('runtime_ORIGINAL_PLAN_PIN')==dict(bytes=C.ORIGINAL_PLAN_PIN[0],SHA256=C.ORIGINAL_PLAN_PIN[1]) and d.get('PUBLISHED_ORIGINAL_PLAN_PIN')==dict(bytes=C.PUBLISHED_ORIGINAL_PLAN_PIN[0],SHA256=C.PUBLISHED_ORIGINAL_PLAN_PIN[1]) and d.get('decoded_canonical_SHA256')==C.ORIGINAL_PLAN_CANONICAL_SHA256,'D5 complete raw/canonical provenance differs')
    C.need(d.get('canonical_equivalence_does_not_relax_raw_wire_pin')is True and d.get('whole_decoded_values_equal')is True and d.get('literal_wire_bytes_equal')is False,'canonical equality is not raw identity')
    C.need(index.get('wire_identity_diagnosis_source_only')==dict(workspace_relative=DIAG_REL,bytes=REPORT_DECLARATIONS[DIAG_REL][0],SHA256=REPORT_DECLARATIONS[DIAG_REL][1],executed=False),'fixed diagnosis SOURCE declaration differs')
    p=index.get('typed_runtime_publication',{})
    C.need(p.get('stage_receipt_kind')==C.STAGE_KIND and type(p.get('source_derivation_version'))is int and p['source_derivation_version']==5 and p.get('COMPLETE_NAME')==C.STAGE_NAME,'D5 typed publication provenance differs')
    C.need(p.get('original_plan_wire_pin')==dict(bytes=C.ORIGINAL_PLAN_PIN[0],SHA256=C.ORIGINAL_PLAN_PIN[1]) and p.get('published_original_plan_SOURCE_reference')==expected_published,'D5 published versus wire pin conflated')
    C.need(p.get('source_receipt')==dict(materialized=True,source_native_enabled=False,staged=False,dispatched=False) and p.get('runtime_plan_changes_only')==dict(enabled=True,staged=True),'existing two-flag publication differs')
    rows=index.get('flat_source_dir_complete20_mapping',[])
    C.need(len(rows)==20 and len({r.get('flat_name')for r in rows})==20 and {r['relative']:(r['bytes'],r['SHA256'])for r in rows}==C.OVERLAY_PINS,'logical mirror127 is not original flat20 mapping')
    C.need(index.get('canonical_path_correction')==dict(old='runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json',new='E1_CANONICAL_SOURCE_METADATA.json',strict_canonical_equals_role_unchanged=True,generic_role_is_not_an_alias=True,three_actual_before_stage_failures_preserved=True),'fixed ROOT canonical correction differs')
    return dict(runtime_original_plan=expected_wire,published_SOURCE_reference=expected_published,decoded_canonical_SHA256=C.ORIGINAL_PLAN_CANONICAL_SHA256,canonical_equivalence_relaxes_raw_pin=False,parent_actual_diagnosis_execution_not_reclassified=True,published_plan_or_diagnosis_read_here=False,flat_source_mapping_count=20,canonical_path='E1_CANONICAL_SOURCE_METADATA.json',generic_role_not_an_alias=True)


def canonical_metadata(role,raw):
    """Only SOURCE metadata identity; never a substitute for full original prepare."""
    C.need(role in C.REQUESTED,'exact selected canonical role')
    value=json.loads(raw)
    C.need(type(value)is dict and value.get('canonical')==role,'SOURCE ROOT canonical differs from exact role')
    return dict(canonical=value['canonical'],generic_role_field=value.get('role'),kind=value.get('kind'),actual_prepare_executed=False)


def capture_provenance(index,current,verified):
    root_rows=index.get('root_canonical_metadata',[])
    C.need(len(root_rows)==2 and {r.get('role')for r in root_rows}==set(C.REQUESTED),'exact two ROOT capture identities required')
    roots=[]
    for row in root_rows:
        role=row['role'];rel=BASE.name+'/discovery/good_holdout_runtime_root_metadata_v2/'+role+'_E1_CANONICAL_SOURCE_METADATA.json'
        C.need(row==dict(role=role,workspace_relative=rel,bytes=ROOT_PINS[role][0],SHA256=ROOT_PINS[role][1]) and current.get(rel)=={k:v for k,v in row.items()if k!='role'},'fixed ROOT capture pin differs')
        item,raw=checked_source(WORKSPACE/rel,*ROOT_PINS[role]);roots.append(dict(item,role=role,metadata=canonical_metadata(role,raw)))
    diagnostic=index.get('source_input_diagnostic',{})
    C.need((diagnostic.get('workspace_relative'),diagnostic.get('bytes'),diagnostic.get('SHA256'))==(INPUT_DIAG_REL,*REPORT_DECLARATIONS[INPUT_DIAG_REL]),'fixed parent diagnostic declaration differs')
    captures=diagnostic.get('local_captures',[]);prefix=BASE.name+'/discovery/good_holdout_concentrated_source_inputs_v1/roles/'
    expected={prefix+role+'/'+name for role in C.REQUESTED for name in ('TASK.json','INSTALL_MANIFEST.json','worker_sources/native_supermimic_bridge.py','worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py')}
    expected|={prefix+'E3/worker_sources/supermimic_vendor_v2/'+name for name in ('__init__.py','contract.py','geometry.py','learner.py','logging.py','networks.py','replay.py')}
    C.need(len(captures)==15 and {r.get('workspace_relative')for r in captures}==expected,'complete exact SOURCE core15 capture list required')
    for row in captures:C.need(current.get(row['workspace_relative'])==row and row['workspace_relative']in verified,'capture15 is not a fresh remote or unverified reference')
    C.need(diagnostic.get('parent_read_once_counts_are_historical_not_local_read_counts')is True and diagnostic.get('source_modules_not_executed_here')is True and diagnostic.get('native_pass_claim')is False,'SOURCE versus parent diagnostic scope differs')
    return dict(root_metadata2=roots,core15_full_SOURCE=[verified[r['workspace_relative']]for r in captures],core15_python_AST_count=sum(r['workspace_relative'].endswith('.py')for r in captures),parent_diagnostic_reference={k:diagnostic[k]for k in ('workspace_relative','bytes','SHA256','parent_reported_status')},parent_report_unread_here=True,parent_once_counts_not_local_once_counts=True,producer_guard_or_full_metadata_validate_executed_here=False)


def build_sources():
    C.require_final_pins()
    index_row,index_blob=checked_source(GOOD_INDEX,*C.INDEX_PIN);good20=check_good_overlay(json.loads(index_blob))
    good_seal=checked_seal(GOOD_SEAL,GOOD_SEAL_PIN,14,GOOD_ROOT)
    sp=C.STAGER_SOURCE_PINS;stage_dir=Path(sp['seal']['path']).parent
    stager=checked_seal(stage_dir/'SOURCE_SEAL.json',(sp['seal']['bytes'],sp['seal']['SHA256']),8,sp['content_root_SHA256'])
    fixed={}
    for key in ('source','index','mirror'):
        row=sp[key];item,blob=checked_source(row['path'],row['bytes'],row['SHA256']);fixed[key]=item
        if key=='mirror':mirror=json.loads(blob)
        if key=='index':materializer_index=json.loads(blob)
    allowed,declarations=mirror_rows(mirror);provenance=validate_D5_provenance(materializer_index)
    verified={}
    for row in allowed:
        item,_=checked_source(WORKSPACE/row['workspace_relative'],row['bytes'],row['SHA256']);verified[row['workspace_relative']]=dict(item,workspace_relative=row['workspace_relative'],audit_reference_only=row['workspace_relative']in AUDIT_REFERENCES)
    current={r['workspace_relative']:r for r in mirror['files']}
    prior_seals={}
    for version,count,root in ((2,9,None),(3,10,'1cdd8c72dfdc9fbb3b75f4068f53e8f489d7d558c79a637f39597efae8e765cd'),(4,10,'9a472be4e70e8cf6f9acf31c4bea31557297358dde7c4c59c972c1ffde5cba84')):
        path=BASE/('source_stage_good_expert_holdout_v'+str(version))/'SOURCE_SEAL.json';row=current[path.relative_to(WORKSPACE).as_posix()]
        prior_seals['D'+str(version)]=checked_seal(path,(row['bytes'],row['SHA256']),count,root)
    old_mirror=json.loads((BASE/'source_stage_good_expert_holdout_v4/SOURCE_MIRROR_INPUTS.json').read_bytes());old=old_mirror['files']
    C.need(len(old)==92 and all(current.get(r['workspace_relative'])==r for r in old),'previous whole92 declaration fields changed')
    additions={k:v for k,v in current.items()if k not in {r['workspace_relative']for r in old}}
    expected=[]
    d4_dir=BASE/'source_stage_good_expert_holdout_v4'
    for item in prior_seals['D4']['members']+[prior_seals['D4']['seal']]:expected.append(dict(workspace_relative=Path(item['path']).relative_to(WORKSPACE).as_posix(),bytes=item['bytes'],SHA256=item['SHA256']))
    for row in materializer_index['root_canonical_metadata']:expected.append({k:v for k,v in row.items()if k!='role'})
    expected+=materializer_index['historical_input_audit_source_only']+materializer_index['source_input_diagnostic']['local_captures']
    expected.append(dict(workspace_relative=INPUT_DIAG_REL,bytes=REPORT_DECLARATIONS[INPUT_DIAG_REL][0],SHA256=REPORT_DECLARATIONS[INPUT_DIAG_REL][1]))
    expected.extend(dict(workspace_relative=k,bytes=v[0],SHA256=v[1])for k,v in AUDIT_REFERENCES.items())
    C.need(len(expected)==35 and additions=={r['workspace_relative']:r for r in expected},'exact D5 additional35 identities differ')
    capture=capture_provenance(materializer_index,current,verified)
    wire_row,wire_raw=checked_source(WORKSPACE/WIRE_REL,*C.ORIGINAL_PLAN_PIN)
    canonical=json.dumps(json.loads(wire_raw),sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
    C.need(C.H(canonical)==C.ORIGINAL_PLAN_CANONICAL_SHA256,'actual SOURCE wire canonical differs')
    provenance.update(wire_full_bytes_verified=wire_row,wire_decoded_canonical_verified=True,published_decoded_equivalence_not_reexecuted_here=True)
    routes={}
    for version,pin,root in ((1,(2748,'55b4be771d2c50065bd5b95480e296bdbb456d683ca885607cfc61f7c8b37d0c'),'a41453e48df40880a66c7afb9644698df528f6f26d5da062a1ce5e10ad23d2c8'),(2,(2767,'265e24d512e991862087338c3f6fa2525c5a3ad3b90bf08140e3f0b2d4301e5f'),'e9bc7f48651a6020db7abf73b3d6de7222d433712b507408a9330cf82e35c51d')):
        routes['V'+str(version)]=checked_seal(BASE/('source_good_holdout_lifecycle_routes_v'+str(version))/'SOURCE_SEAL.json',pin,12,root)
    old_controller,_=checked_source(OLD_CONTROLLER,expected_sha=OLD_CONTROLLER_SHA);connector,_=checked_source(CONNECTOR,expected_sha=CONNECTOR_SHA)
    own_controller,_=checked_source(HERE/'good_holdout_parent_actual_wait_controller_v1.py',*C.CONTROLLER_SOURCE_PIN)
    return dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_INVENTORY_V3',scope='FULL_ALLOWED_SOURCE_TEXT_SHA_AST_SIX_UNREAD_REPORT_DECLARATIONS',good_index=index_row,good20=good20,good14_seal=good_seal,D5_final8_seal=stager,D5_fixed_refs=fixed,prior_materializer_seals=prior_seals,prior_routes_12_seals=routes,
        D5_mirror=dict(declared=127,full_allowed_SOURCE_verifications=121,unread_report_declarations=declarations,verified=list(verified.values()),all127_full_bytes_read=False,previous92_fields_unchanged=True,additions35_full_SOURCE=31,additions35_report_declarations=4,additional35=sorted(additions.values(),key=lambda r:r['workspace_relative']),audit_only_last4=[dict(workspace_relative=k,bytes=v[0],SHA256=v[1],active_dependency=False,imported_or_executed=False,full_bytes_verified=k==B2_AUDIT_REL)for k,v in AUDIT_REFERENCES.items()],logical136_is_not_flat20=True),
        D5_raw_provenance=provenance,D5_SOURCE_capture_provenance=capture,original_9595_controller=old_controller,original_connect72_SOURCE_only=connector,own_controller=own_controller,runtime_aliases=20,original_runtime_unchanged=True,original_parent_unchanged=True,old_sealed_sources_unchanged=True,groups_are_not_disjoint_sum=True,
        actual_prepare_preflight_stage_main=False,actual_controller_or_collector=False,actual_SSH_SDK_GPU_Torch=False,actual_model_raw_reports_C_or_lock_access=False,actual_native_binding='UNKNOWN',actual_quality=None,stage2_GO=False)


def verify_sources():
    recorded=json.loads((HERE/'SOURCE_PINS.json').read_bytes());current=build_sources()
    C.need(recorded==current,'SOURCE inventory differs from full allowed text/declaration split')
    return current


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--build',action='store_true');args=parser.parse_args()
    value=build_sources()if args.build else verify_sources()
    if args.build:
        with(HERE/'SOURCE_PINS.json').open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    print(json.dumps(dict(runtime_aliases=value['runtime_aliases'],full_SOURCE=121,report_declarations_only=6,added_full_SOURCE=31,added_report_declarations=4,actual_stage_or_report_reads=False)))
