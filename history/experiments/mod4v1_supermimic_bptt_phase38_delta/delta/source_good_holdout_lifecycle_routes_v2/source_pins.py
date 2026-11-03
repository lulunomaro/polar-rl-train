"""SOURCE-only inventory: full allowed text SHA/AST; old actual plan NOT opened.

No producer imports, native calls, stage, collector, report/model/lock/ledger I/O.
The old actual plan and diagnosis are exact declarations, never report reads.
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
WIRE_REL='mod4v1_supermimic_bptt_20261102/discovery/good_holdout_original_plan_wire_v1/ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json'
DIAG_REL='mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_ORIGINAL_PLAN_WIRE_VS_PUBLISHED_DIAGNOSIS_V1.json'
DIAG_PIN=(1459,'673398d112f60f084b9c945a747d0d13625e43487291549d9d4dfca0a3991b38')
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
    C.need(type(rows)is list and len(rows)==92 and mirror.get('files_count')==92 and mirror.get('kind')=='COMPLETE_GOOD_HOLDOUT_V4_PINNED_TEXT_MIRROR_INPUTS','whole fixed D4 mirror92 required')
    seen=set();allowed=[];declarations=[]
    for row in rows:
        value=row.get('workspace_relative');C.need(type(value)is str and value not in seen,'unique workspace SOURCE reference');seen.add(value)
        path=PurePosixPath(value)
        C.need(not path.is_absolute() and str(path)==value and '..'not in path.parts and '\\'not in value and ':'not in value,'lexical workspace SOURCE reference')
        C.need(type(row.get('bytes'))is int and row['bytes']>0 and C.sha(row.get('SHA256')),'complete mirror SOURCE identity')
        if 'reports'in(p.lower()for p in path.parts):
            expected={OLD_PLAN_REL:C.PUBLISHED_ORIGINAL_PLAN_PIN,DIAG_REL:DIAG_PIN}
            C.need(value in expected and (row['bytes'],row['SHA256'])==expected[value],'only the two exact published declarations are admitted without report access')
            declarations.append(dict(row,verification='PUBLISHED_SOURCE_DECLARATION_ONLY',full_bytes_verified=False,actual_file_stat_or_read=False))
        else:
            source_path(WORKSPACE/value)  # lexical/path guards run before any content I/O.
            allowed.append(row)
    C.need(len(allowed)==90 and len(declarations)==2 and {r['workspace_relative']for r in declarations}=={OLD_PLAN_REL,DIAG_REL},'D4 mirror full90/declaration2 split differs')
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


def validate_D4_provenance(index):
    C.need(index.get('kind')=='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V4' and type(index.get('source_derivation_version'))is int and index['source_derivation_version']==4,'fixed D4 SOURCE index kind/version required')
    expected_wire=dict(workspace_relative=WIRE_REL,bytes=C.ORIGINAL_PLAN_PIN[0],SHA256=C.ORIGINAL_PLAN_PIN[1])
    expected_published=dict(workspace_relative=OLD_PLAN_REL,bytes=C.PUBLISHED_ORIGINAL_PLAN_PIN[0],SHA256=C.PUBLISHED_ORIGINAL_PLAN_PIN[1])
    C.need(index.get('original_group_plan_wire')==expected_wire and index.get('original_group_plan')==expected_published,'distinct actual wire and published SOURCE identities required')
    d=index.get('original_group_plan_wire_identity',{})
    C.need(d.get('runtime_ORIGINAL_PLAN_PIN')==dict(bytes=C.ORIGINAL_PLAN_PIN[0],SHA256=C.ORIGINAL_PLAN_PIN[1]) and d.get('PUBLISHED_ORIGINAL_PLAN_PIN')==dict(bytes=C.PUBLISHED_ORIGINAL_PLAN_PIN[0],SHA256=C.PUBLISHED_ORIGINAL_PLAN_PIN[1]) and d.get('decoded_canonical_SHA256')==C.ORIGINAL_PLAN_CANONICAL_SHA256,'D4 complete raw/canonical provenance differs')
    C.need(d.get('canonical_equivalence_does_not_relax_raw_wire_pin')is True and d.get('whole_decoded_values_equal')is True and d.get('literal_wire_bytes_equal')is False,'canonical equality is not raw identity')
    C.need(index.get('wire_identity_diagnosis_source_only')==dict(workspace_relative=DIAG_REL,bytes=DIAG_PIN[0],SHA256=DIAG_PIN[1],executed=False),'fixed diagnosis SOURCE declaration differs')
    p=index.get('typed_runtime_publication',{})
    C.need(p.get('stage_receipt_kind')==C.STAGE_KIND and type(p.get('source_derivation_version'))is int and p['source_derivation_version']==4 and p.get('COMPLETE_NAME')==C.STAGE_NAME,'D4 typed publication provenance differs')
    C.need(p.get('original_plan_wire_pin')==dict(bytes=C.ORIGINAL_PLAN_PIN[0],SHA256=C.ORIGINAL_PLAN_PIN[1]) and p.get('published_original_plan_SOURCE_reference')==expected_published,'D4 published versus wire pin conflated')
    rows=index.get('flat_source_dir_complete20_mapping',[])
    C.need(len(rows)==20 and len({r.get('flat_name')for r in rows})==20 and {r['relative']:(r['bytes'],r['SHA256'])for r in rows}==C.OVERLAY_PINS,'logical mirror92 does not replace original flat20 mapping')
    return dict(runtime_original_plan=expected_wire,published_SOURCE_reference=expected_published,decoded_canonical_SHA256=C.ORIGINAL_PLAN_CANONICAL_SHA256,canonical_equivalence_relaxes_raw_pin=False,diagnosis_SOURCE_executed_field=False,parent_actual_diagnosis_execution_not_reclassified=True,published_plan_or_diagnosis_read_here=False,flat_source_mapping_count=20)


def build_sources():
    C.require_final_pins()
    index_row,index_blob=checked_source(GOOD_INDEX,*C.INDEX_PIN);good20=check_good_overlay(json.loads(index_blob))
    good_seal=checked_seal(GOOD_SEAL,GOOD_SEAL_PIN,14,GOOD_ROOT)
    sp=C.STAGER_SOURCE_PINS;stage_dir=Path(sp['seal']['path']).parent
    stager=checked_seal(stage_dir/'SOURCE_SEAL.json',(sp['seal']['bytes'],sp['seal']['SHA256']),10,sp['content_root_SHA256'])
    fixed={}
    for key in ('source','index','mirror'):
        row=sp[key];item,blob=checked_source(row['path'],row['bytes'],row['SHA256']);fixed[key]=item
        if key=='mirror':mirror=json.loads(blob)
        if key=='index':materializer_index=json.loads(blob)
    allowed,declarations=mirror_rows(mirror)
    provenance=validate_D4_provenance(materializer_index)
    verified=[]
    for row in allowed:
        item,_=checked_source(WORKSPACE/row['workspace_relative'],row['bytes'],row['SHA256']);verified.append(dict(item,workspace_relative=row['workspace_relative']))
    # V2 nine and old good14 preservation are independent complete seals, not
    # replaced by a directory name or an aggregate "79 files read" claim.
    v2=BASE/'source_stage_good_expert_holdout_v2/SOURCE_SEAL.json'
    v2row=next(r for r in allowed if r['workspace_relative']==v2.relative_to(WORKSPACE).as_posix())
    v2seal=checked_seal(v2,(v2row['bytes'],v2row['SHA256']),9)
    d3=BASE/'source_stage_good_expert_holdout_v3/SOURCE_SEAL.json'
    d3row=next(r for r in allowed if r['workspace_relative']==d3.relative_to(WORKSPACE).as_posix())
    d3seal=checked_seal(d3,(d3row['bytes'],d3row['SHA256']),10,'1cdd8c72dfdc9fbb3b75f4068f53e8f489d7d558c79a637f39597efae8e765cd')
    old_mirror=json.loads((d3.parent/'SOURCE_MIRROR_INPUTS.json').read_bytes())
    current={r['workspace_relative']:r for r in mirror['files']}
    C.need(len(old_mirror['files'])==79 and all(current.get(r['workspace_relative'])==r for r in old_mirror['files']),'previous whole79 SOURCE declarations changed')
    wire_row,wire_raw=checked_source(WORKSPACE/WIRE_REL,*C.ORIGINAL_PLAN_PIN)
    wire=json.loads(wire_raw);canonical=json.dumps(wire,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
    C.need(C.H(canonical)==C.ORIGINAL_PLAN_CANONICAL_SHA256,'actual SOURCE wire decoded canonical differs')
    provenance.update(wire_full_bytes_verified=wire_row,wire_decoded_canonical_verified=True,published_decoded_equivalence_not_reexecuted_here=True)
    previous_routes=checked_seal(BASE/'source_good_holdout_lifecycle_routes_v1/SOURCE_SEAL.json',(2748,'55b4be771d2c50065bd5b95480e296bdbb456d683ca885607cfc61f7c8b37d0c'),12,'a41453e48df40880a66c7afb9644698df528f6f26d5da062a1ce5e10ad23d2c8')
    old_controller,_=checked_source(OLD_CONTROLLER,expected_sha=OLD_CONTROLLER_SHA)
    connector,_=checked_source(CONNECTOR,expected_sha=CONNECTOR_SHA)
    own_controller,_=checked_source(HERE/'good_holdout_parent_actual_wait_controller_v1.py',*C.CONTROLLER_SOURCE_PIN)
    return dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_INVENTORY_V2',scope='FULL_ALLOWED_SOURCE_TEXT_SHA_AST_NO_ACTUAL_REPORT',good_index=index_row,good20=good20,good14_seal=good_seal,
        D664_final10_seal=stager,D664_fixed_refs=fixed,D664_mirror=dict(declared=92,full_allowed_SOURCE_verifications=90,actual_plan_and_diagnosis_declarations_only=2,verified=verified,unread_report_declarations=declarations,all92_full_bytes_read=False,previous79_unchanged=True),
        old_V2_9_seal=v2seal,previous_D3_10_seal=d3seal,previous_routes_V1_12_seal=previous_routes,D4_raw_provenance=provenance,original_9595_controller=old_controller,original_connect72_SOURCE_only=connector,own_controller=own_controller,
        runtime_aliases=20,original_runtime_unchanged=True,original_parent_unchanged=True,old_sealed_sources_unchanged=True,
        actual_stage=False,actual_controller_or_collector=False,actual_SSH_SDK_GPU_Torch=False,actual_model_raw_reports_C_or_lock_access=False,
        actual_native_binding='UNKNOWN',actual_quality=None,stage2_GO=False)


def verify_sources():
    recorded=json.loads((HERE/'SOURCE_PINS.json').read_bytes());current=build_sources()
    C.need(recorded==current,'SOURCE inventory differs from immutable full allowed text/declaration split')
    return current


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--build',action='store_true');args=parser.parse_args()
    value=build_sources() if args.build else verify_sources()
    if args.build:
        C.need(not(HERE/'SOURCE_PINS.json').exists(),'new SOURCE inventory already exists')
        with(HERE/'SOURCE_PINS.json').open('x',encoding='utf-8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
    print(json.dumps(dict(runtime_aliases=value['runtime_aliases'],full_mirror_SOURCE=90,report_declarations_only=2,old_actual_plan_opened=False,old_sealed_sources_unchanged=True)))
