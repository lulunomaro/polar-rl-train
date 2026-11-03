"""SOURCE-only passive E3 capture materializer; explicit file operations, never launch.

Inputs: complete original V8 static root, actual Admission2 vendor root, and a
source-only mirror of the local R directory. No model/producer fallback exists.
This module defines prepare/stage; SOURCE tests never call either function.
"""
from __future__ import annotations
from static_source_helpers_v1 import *
import tempfile

HERE=Path(__file__).resolve().parent
R_NAME='mod4v1_supermimic_bptt_20261102'
WORKER_FOLDER='source_phase1_capture_worker_v2'
WORKER_SEAL_PIN=(2815, 'caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5')
WORKER_ROOT_SHA='83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2'
WORKER_INDEX_PIN=(65961, 'cdb2ca55c08a544cd01e462b7ce27261900f3b6ebaffb4784350717f756b7cf7')
ORIGINAL_INDEX_PIN=(6085,'d0519c7a351513a61f4c0c5c055b74bc7df41ac0300ce964207dd9508254f19a')
DEPENDENCY_SEALS={
 'sensor':(13,'3d5fd4febf9232a8113b4d93dbf8d3d6a19658690e973d6485c1aedc39e18881'),
 'actuation':(8,'ed77f3a3b0ce7aea6f904a09be8d038097bfb00729d57bec94feae5ab67bd081'),
 'adapter':(10,'a1290c56bb849647e126457ac71b3ec13ac0d066b3b63b0337bd9f587eac0855'),
 'partition':(9,'e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630')}
ROLES=('E3','W35','CURB_INDEPENDENT113','CURB_PROTECTED878','SLOPE135','SLOPE_INDEPENDENT50','E0','E2')
REQUESTED=('E3',)
CONTROLS=dict(E0=1000,E2=1200,E3=160,W35=1600,CURB_PROTECTED878=750,CURB_INDEPENDENT113=750,SLOPE135=750,SLOPE_INDEPENDENT50=1000)
PURPOSE='NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN'
ROOT_PREFIX='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_'
ORIGINAL_GROUP_ID='MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700'
NATIVE_RUN_ID='MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000'
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
VENDOR_PIN=(7,'ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0')
RETAIN_PREFIX='worker_sources/phase1_retained_original/'
COMPLETE_NAME='STAGE_COMPLETE_PHASE1_CAPTURE_V1.json'
SOURCE_DERIVATION_VERSION=2
V1_ENTRY_SHA256='0ee747167d7c3389e5e3541c527ac5a4f4244a2a91b08e7733f38e6c8d2fda98'
BOOTSTRAP_ORIGINAL_SOURCES={'launch_storage_contract': {'relative': 'worker_sources/parent/launch_storage_contract.py', 'source_relative': 'discovery/phase1_first_startup_failure_v1/worker_sources/parent/launch_storage_contract.py', 'bytes': 117, 'SHA256': 'e40b51db4bca2f322cc2c9b4b0fe011eed292ae605f4f175f268a5bf90326047'}, 'n80_gpu_capacity': {'relative': 'worker_sources/parent/n80_gpu_capacity.py', 'source_relative': 'discovery/phase1_first_startup_failure_v1/worker_sources/parent/n80_gpu_capacity.py', 'bytes': 653, 'SHA256': 'ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc'}}


def canonical(value):
    return H(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode())


def reference_path(source_root, value):
    """Pinned Windows paths are provenance; an explicit source-only R mirror is used."""
    value=str(value).replace('\\','/');marker='/'+R_NAME+'/'
    if marker in value:
        need(value.count(marker)==1,'ambiguous pinned R reference');value=value.split(marker,1)[1]
    need(not any(denied(p) for p in safe_relative(value).split('/')),'non-source reference in pinned index')
    return no_links(lexical(source_root),value)


def verify_package(folder, expected_SHA, count, *, worker=False):
    folder=Path(folder);seal_path=no_links(folder,'SOURCE_SEAL.json');seal,raw=metadata(seal_path)
    need(H(raw)==expected_SHA,'sealed package bytes differ: '+folder.name)
    if worker:
        need(len(raw)==WORKER_SEAL_PIN[0] and seal.get('frozen') is True and seal.get('source_only') is True,
             'final worker seal required, not a floating index')
        need(seal.get('content_root_sha256')==WORKER_ROOT_SHA and canonical(seal['files'])==WORKER_ROOT_SHA,
             'worker complete13 canonical root differs')
    rows=seal['files']
    if type(rows) is dict:rows=[dict(relative=k,**v) for k,v in rows.items()]
    need(type(rows) is list and len(rows)==count,'complete sealed package member count differs')
    result={};result['SOURCE_SEAL.json']=(seal_path,dict(bytes=len(raw),SHA=H(raw)))
    for row in rows:
        rel=safe_relative(row['relative']);need(rel not in result,'duplicate sealed package member')
        need(Path(rel).suffix.lower() in ('.py','.json','.md','.txt'),'non-source sealed package member')
        path=no_links(folder,rel);info=identity(path)
        need((info['bytes'],info['SHA'])==(row['bytes'],row.get('sha256',row.get('SHA256'))),'sealed member differs: '+rel)
        if path.suffix=='.py':ast.parse(path.read_bytes())
        result[rel]=(path,info)
    return result,dict(path=str(seal_path),bytes=len(raw),SHA256=H(raw),members=count,
                      content_root_sha256=seal.get('content_root_sha256'),all_actual_source_bytes_verified=True)


def load_sources(source_root):
    """Only fixed textual source packages; no prepare, static bank or model access."""
    source_root=lexical(source_root);folder=source_root/WORKER_FOLDER
    worker,worker_receipt=verify_package(folder,WORKER_SEAL_PIN[1],13,worker=True)
    index,index_raw=metadata(folder/'CAPTURE_SOURCE_INDEX.json',2*1024*1024)
    need((len(index_raw),H(index_raw))==WORKER_INDEX_PIN,'final capture SOURCE index differs')
    need(index.get('kind')=='PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1' and index.get('source_version')==2,'final SOURCE V2 with preserved typed index required')
    original,old_raw=metadata(reference_path(source_root,index['original_index']['path']))
    need((len(old_raw),H(old_raw))==ORIGINAL_INDEX_PIN,'complete original17 index differs')
    old_rows=[dict(path=r['path'],install_relative=r['relative'],bytes=r['bytes'],SHA256=r['SHA256']) for r in original['entries']]
    need(index['original17']==old_rows and len(old_rows)==17 and len(index['new_sources'])==5 and len(index['dependency_sources'])==5,
         'exact original17/new5/dependency5 closure required')
    sources={};receipts={'worker':worker_receipt}
    for row in old_rows+index['new_sources']+index['dependency_sources']:
        alias=safe_relative(row['install_relative']);need(alias not in sources and not any(denied(p) for p in alias.split('/')),'duplicate/non-static source alias')
        path=reference_path(source_root,row['path']);info=identity(path)
        need((info['bytes'],info['SHA'])==(row['bytes'],row['SHA256']),'complete source mapping differs: '+alias)
        if path.suffix=='.py':ast.parse(path.read_bytes())  # whole modules, no body cropping
        sources[alias]=(path,info)
    sources['CAPTURE_SOURCE_INDEX.json']=(folder/'CAPTURE_SOURCE_INDEX.json',dict(bytes=len(index_raw),SHA=H(index_raw)))
    for rel,value in worker.items():sources['phase1_source_proof/worker/'+rel]=value
    need(set(index['dependency_seals'])==set(DEPENDENCY_SEALS),'complete sealed dependency set required')
    for name,(count,expected) in DEPENDENCY_SEALS.items():
        record=index['dependency_seals'][name]
        need(record['SHA256']==expected and len(record['members'])==count,'dependency lineage index differs')
        path=reference_path(source_root,record['path'])
        members,receipt=verify_package(path.parent,expected,count)
        need(members['SOURCE_SEAL.json'][1]['bytes']==record['bytes'],'dependency seal size differs')
        expected_rows={r['relative']:(r['bytes'],r['SHA256']) for r in record['members']}
        actual_rows={r:(i['bytes'],i['SHA']) for r,(_,i) in members.items() if r!='SOURCE_SEAL.json'}
        need(actual_rows==expected_rows,'dependency complete member listing differs')
        receipts[name]=receipt
        for rel,value in members.items():sources['phase1_source_proof/'+name+'/'+rel]=value
    pinned=index['all_actuation_original_sources']
    need(type(pinned) is dict and len(pinned)==index['actuation_original_source_count']==182,'complete original C source pins required')
    for rel,row in pinned.items():
        path=reference_path(source_root,rel);info=identity(path)
        need((info['bytes'],info['SHA'])==(row['bytes'],row['sha256']),'actual original C source pin differs: '+rel)
        if path.suffix=='.py':ast.parse(path.read_bytes())
    bootstrap_text_evidence={}
    listed=index['bootstrap_original_sources']
    need(type(listed) is list and len(listed)==2,'complete original bootstrap source index required')
    by_alias={row['install_relative']:row for row in listed}
    need(set(by_alias)=={row['relative'] for row in BOOTSTRAP_ORIGINAL_SOURCES.values()},'bootstrap source alias set differs')
    for name,row in BOOTSTRAP_ORIGINAL_SOURCES.items():
        indexed=by_alias[row['relative']]
        path=reference_path(source_root,indexed['path']);info=identity(path)
        need(path==reference_path(source_root,row['source_relative']) and (indexed['bytes'],indexed['SHA256'])==(row['bytes'],row['SHA256']),
             'actual final bootstrap source index/provenance differs: '+name)
        need((info['bytes'],info['SHA'])==(row['bytes'],row['SHA256']),
             'complete actual original bootstrap source evidence differs: '+name)
        ast.parse(path.read_bytes())
        bootstrap_text_evidence[name]=dict(path=str(path),relative=row['relative'],bytes=info['bytes'],SHA256=info['SHA'],
                                           evidence_only_not_original_baseline_fallback=True)
    return dict(sources=sources,index=index,source_root=source_root,
        receipt=dict(kind='ACTUAL_COMPLETE_TEXT_SOURCE_PIN_VERIFICATION_PHASE1_V2',source_derivation_version=2,v1_entry_SHA256=V1_ENTRY_SHA256,worker=worker_receipt,
            index_bytes=len(index_raw),index_SHA256=H(index_raw),source_mappings=27,dependency_seals=receipts,
            actual_original_C_source_pins=182,bootstrap_original_source_evidence=bootstrap_text_evidence,source_native_enabled=False,native_executed=False,model_reads=0))


def native_boundary(native_root):
    """Only actual closed root provenance; no producer FINAL/checkpoint path is used."""
    root=lexical(native_root)
    plan,plan_raw=metadata(root/'OWNER_PLAN.json');exit_value,exit_raw=metadata(root/'OWNER_EXIT_ACTUAL.json');cohort,cohort_raw=metadata(root/'COHORT_FINAL.json')
    run=plan.get('run_id')
    need(run==root.name==NATIVE_RUN_ID and exit_value.get('run_id')==cohort.get('run_id')==run,'exact Admission2 source root identity required')
    need(all(exit_value.get(k) is True for k in ('all_own_children_waited','original_cost_settled','original_leases_released'))
         and exit_value.get('errors')==[] and exit_value.get('H1_excluded') is True,'native source boundary not closed')
    need(cohort.get('all_own_children_waited') is True and cohort.get('original_cost_settled') is True
         and cohort.get('errors')==[] and cohort.get('H1_excluded') is True,'native source cohort not normally closed')
    need(not(root/'OWNER_ORIGINAL_ERROR.json').exists(),'native original source parent error exists')
    entries=plan.get('entries');need(type(entries) is list and len(entries)==8 and {e['role'] for e in entries}==set(ROLES),'native complete8 catalog required')
    rows,go=cohort.get('rows'),cohort.get('go')
    need(type(rows) is dict and type(go) is dict and rows and set(rows)==set(go),'all actual source GO keys must be terminal')
    keys={e['role_key']:e for e in entries};need(len(keys)==8 and set(rows)<=set(keys),'source role keys differ')
    for key,row in rows.items():
        semantic_success(row)
        need(row.get('key')==key and row.get('role')==keys[key]['role'] and go[key].get('role_key')==key
             and go[key].get('run_id')==run and go[key].get('role')==keys[key]['role'],'source terminal/GO identity differs')
    e3=next(e for e in entries if e['role']=='E3')
    need(e3['role_key'] in rows and lexical(e3['job_root'])==root/'roles'/'E3','actual waited E3 runtime source required')
    return dict(native_root=str(root),run_id=run,OWNER_PLAN_SHA=H(plan_raw),OWNER_EXIT_SHA=H(exit_raw),COHORT_FINAL_SHA=H(cohort_raw),
                original_closed_metadata_only_not_new_admission=True,producer_FINAL_reads=0,model_stat_hash_open_decode=0,
                actual_canonical_ledger_read_or_written=False)


def retain_originals(originals, sources, *, original_root, original_plan_SHA, native_root):
    """Preserve every independently inventoried old byte, relocating only true alias conflicts."""
    materials=dict(originals);relocations={};origin=[];baseline=[]
    for rel,(path,info) in sorted(originals.items()):
        alias=rel
        if rel in sources and sources[rel][1]!=info:
            alias=RETAIN_PREFIX+safe_relative(rel)
            need(alias not in originals and alias not in sources and alias not in materials,'retained original alias collides')
            materials[alias]=(path,info);relocations[rel]=alias
        origin.append(dict(relative=rel,bytes=info['bytes'],SHA256=info['SHA'],input_path=str(path),bytes_read=info['bytes']))
        baseline.append(dict(relative=alias,bytes=info['bytes'],SHA256=info['SHA']))
    materials.update(sources);baseline.sort(key=lambda r:r['relative'])
    logical=[{k:r[k] for k in ('relative','bytes','SHA256')} for r in origin]
    inventory=dict(kind='COMPLETE_ORIGINAL_STATIC_TREE_REFERENCE_V1',baseline=baseline,installed=copy.deepcopy(baseline),
        SHA256=canonical(baseline),vendor7_SHA256=VENDOR_PIN[1],installed_status='PLANNED_HASH_IDENTITIES_NOT_ACTUAL_MATERIALIZATION',
        baseline_provenance=dict(kind='INDEPENDENT_COMPLETE_INPUT_TREE_BYTE_INVENTORY_V1',original_root=str(original_root),
            original_plan_SHA256=original_plan_SHA,native_root=str(native_root),original_logical_rows=origin,
            original_logical_tree_SHA256=canonical(logical),source_to_retained=relocations,
            all_original_input_files_read=len(origin),operational_raw_model_names_excluded_before_classification=True))
    validate_preservation(inventory,materials,originals=originals)
    return materials,inventory


def validate_preservation(inventory, materials, *, originals=None, observed=None):
    """Not two self-reported equal arrays: bind full independently read origin and actual bytes."""
    proof=inventory['baseline_provenance'];origin=proof['original_logical_rows'];moves=proof['source_to_retained']
    need(origin and len({r['relative'] for r in origin})==len(origin),'unique full original input inventory required')
    logical=[{k:r[k] for k in ('relative','bytes','SHA256')} for r in origin]
    need(logical==sorted(logical,key=lambda r:r['relative']) and canonical(logical)==proof['original_logical_tree_SHA256'],
         'independent original logical tree digest differs')
    if originals is not None:
        actual=[dict(relative=k,bytes=i['bytes'],SHA256=i['SHA']) for k,(_,i) in sorted(originals.items())]
        need(logical==actual,'provenance is not the complete independently read input tree')
        need(all(r['input_path']==str(originals[r['relative']][0]) and r['bytes_read']==r['bytes'] for r in origin),
             'actual input path/read-byte provenance differs')
    need(proof['all_original_input_files_read']==len(origin) and set(moves)<=set(r['relative'] for r in origin),'source relocation domain differs')
    expected=[]
    for row in origin:
        old=safe_relative(row['relative']);alias=moves.get(old,old)
        if old in moves:need(alias==RETAIN_PREFIX+old,'only exact retained-original namespace relocation permitted')
        info=materials.get(alias,(None,None))[1]
        need(info==dict(bytes=row['bytes'],SHA=row['SHA256']),'original byte lost/changed under retained alias: '+alias)
        expected.append(dict(relative=alias,bytes=row['bytes'],SHA256=row['SHA256']))
    expected.sort(key=lambda r:r['relative'])
    need(len({r['relative'] for r in expected})==len(expected) and inventory['baseline']==expected,'retained baseline is incomplete or duplicates')
    installed=expected if observed is None else [dict(relative=r['relative'],bytes=observed[r['relative']]['bytes'],SHA256=observed[r['relative']]['SHA']) for r in expected]
    need(inventory['installed']==installed==expected and inventory['SHA256']==canonical(expected),'installed retained bytes differ from independent original baseline')
    need(all(any(r['relative'].startswith('runtimes/'+role+'/') for r in expected) for role in ROLES),'all8 complete source runtimes required')
    need(any(r['relative'].startswith('pinned_assets/') for r in expected) and any(r['relative'].startswith('worker_sources/') for r in expected),'original asset/worker trees required')
    need(len([r for r in expected if r['relative'].startswith('supermimic_vendor_v2/')])==7
         and inventory['vendor7_SHA256']==VENDOR_PIN[1],'full original vendor7 retention required')
    return True


def prepare(original_group_root, source_root, native_root, new_root, group_id, gpu_uuid, *, controls=64):
    original_group_root,new_root=lexical(original_group_root),lexical(new_root)
    need(type(controls) is int and controls in (64,128),'capture controls must be64 or128')
    need(not new_root.is_symlink() and not new_root.exists(),'new-root must be absent; no overwrite/retry')
    need(group_id==new_root.name and group_id.startswith(ROOT_PREFIX) and re.fullmatch('[A-Za-z0-9_]+',group_id),'explicit NEW passive capture root prefix required')
    need(re.fullmatch('GPU-[0-9a-f-]+',gpu_uuid) is not None,'explicit original GPU UUID required')
    for old in (original_group_root,lexical(source_root),lexical(native_root)):
        need(not new_root.is_relative_to(old) and not old.is_relative_to(new_root),'new-root overlaps an input')
    bundle=load_sources(source_root);boundary=native_boundary(native_root)
    old,old_raw=metadata(original_group_root/'GROUP_PLAN.json')
    need(old.get('group_id')==original_group_root.name==ORIGINAL_GROUP_ID and old.get('asset_SHA')==USD and old.get('contract_SHA')==CONTRACT,'exact original V8 group/assets required')
    rows=old.get('roles');need(type(rows) is list and len(rows)==9 and {r['role'] for r in rows}==set(ROLES)|{'H1_normal'},'original complete9-to8 catalog differs')
    originals={}
    for directory in ('worker_sources','pinned_assets'):
        for rel,value in tree(original_group_root/directory).items():originals[directory+'/'+rel]=value
    files=old.get('worker_files');need(type(files) is list and files and len({r['relative'] for r in files})==len(files),'complete unique original worker_files required')
    for item in files:
        rel=safe_relative(item['relative']);need(not any(denied(p) for p in rel.split('/')),'non-static original worker file')
        path=no_links(original_group_root,rel);info=identity(path)
        need(info=={k:item[k] for k in ('bytes','SHA')},'actual original worker file differs: '+rel);originals[rel]=(path,info)
    plan=dict(kind='PHASE1_PASSIVE_CAPTURE_E3_ONLY_PLAN_V1',batch_purpose=PURPOSE,policy_variant='EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY',
        group_id=group_id,GPU_UUID=gpu_uuid,asset_SHA=USD,contract_SHA=CONTRACT,capture_controls=controls,
        requested_roles=['E3'],deferred_roles=list(ROLES[1:]),paired_reset_protocol=paired_plan(),roles=[],comparison=None,
        overall_eight_pass_rate=None,source_native_enabled=False,staged=False,dispatched=False,actual_SDK_executed=False,
        gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
    by_role={r['role']:r for r in rows}
    for role in ROLES:
        row=copy.deepcopy(by_role[role]);need(row.get('controls')==CONTROLS[role],'original role control definition differs')
        runtime=lexical(row['runtime_root']);need(runtime==original_group_root/'runtimes'/role,'original runtime escaped complete role tree')
        for rel,value in tree(runtime).items():originals['runtimes/'+role+'/'+rel]=value
        asset=lexical(row['asset_dir']);need(asset.is_relative_to(runtime),'original asset directory escaped runtime')
        historical={k:row.pop(k) for k in list(row) if k.startswith('source_') or k in ('teacher_path','checkpoint','a1_producer')}
        row.update(runtime_root=str(new_root/'runtimes'/role),asset_dir=str(new_root/'runtimes'/role/asset.relative_to(runtime)),
                   historical_source_metadata_not_opened=historical,num_envs=80,seed=20260928)
        if role=='E3':row.update(worker='worker_passive_interface_v1.py',capture_controls=controls)
        plan['roles'].append(row)
    vendor=tree(Path(native_root)/'roles'/'E3'/'worker_sources'/'supermimic_vendor_v2');observed=digest_tree(vendor)
    need((observed['files'],observed['SHA'])==VENDOR_PIN,'actual complete native vendor7 source tree differs')
    need({'__init__.py','learner.py','networks.py','geometry.py','replay.py','contract.py'}<=set(vendor)
         and all('/' not in rel and rel.endswith('.py') for rel in vendor),'complete flat vendor7 required')
    init=ast.parse(vendor['__init__.py'][0].read_bytes())
    need(len(init.body)==1 and isinstance(init.body[0],ast.Expr) and isinstance(init.body[0].value,ast.Constant)
         and type(init.body[0].value.value) is str,'original vendor init must remain complete docstring, not stub')
    for rel,value in vendor.items():
        alias='supermimic_vendor_v2/'+rel
        need(alias not in originals or originals[alias][1]==value[1],'native vendor overlaps a different original static alias: '+alias)
        originals[alias]=value
    for alias,value in bundle['sources'].items():
        if alias.startswith('supermimic_vendor_v2/'):need(originals[alias][1]==value[1],'actual vendor/index source mismatch')
    helper=bundle['index']['original_capacity_helper']
    need(any(Path(rel).name=='n80_gpu_capacity.py' and (info['bytes'],info['SHA'])==(helper['bytes'],helper['SHA256']) for rel,(_,info) in originals.items()),
         'exact original full capacity helper missing from complete static tree')
    materials,inventory=retain_originals(originals,bundle['sources'],original_root=original_group_root,original_plan_SHA=H(old_raw),native_root=native_root)
    plan['retained_static_inventory']=inventory
    aliases={r['relative'] for r in files}|set(bundle['sources'])|{'supermimic_vendor_v2/'+r for r in vendor}
    plan['worker_files']=[dict(relative=rel,**materials[rel][1]) for rel in sorted(aliases)]
    bundle=dict(bundle,materials=materials,originals=originals)
    need(len(json.dumps(plan,allow_nan=False).encode())<=64*1024*1024,'full inventory exceeds actual runtime metadata64MiB bound')
    validation=metadata_validate(bundle,plan)
    return dict(plan=plan,materials=materials,originals=originals,source_bundle=bundle,new_root=new_root,boundary=boundary,
                original_plan_SHA=H(old_raw),native_vendor=observed,metadata_validation=validation)


def metadata_validate(bundle, plan, *, actual_root=None):
    """Full actual safe modules and task protocol; no actor/model/SDK/resource calls."""
    old_path=list(sys.path);old_bytecode=sys.dont_write_bytecode;old_import=builtins.__import__
    old_open,old_io_open,old_stat,old_lstat=builtins.open,io.open,os.stat,os.lstat
    def filesystem(function):
        def call(path,*a,**kw):
            need(not model_path(path) and (isinstance(path,int) or ('budget' not in Path(os.fspath(path)).name.lower()
                 and Path(os.fspath(path)).suffix.lower()!='.lock')),'metadata import attempted model/C/lock filesystem access')
            return function(path,*a,**kw)
        return call
    watched=('phase1_capture_contract','phase1_capture_runtime','phase1_capture_observer','worker_passive_interface_v1',
        'source_api','passive_capture','phase1_sealed_actuation_tap','_phase1_capture_pinned_a1_core',
        'frozen_a1_raw35_v1','pose_cache_runtime_adapter_v3','app_close_semantics_v5','resume_runtime_contracts_v3',
        'launch_storage_contract','n80_gpu_capacity')
    before={n:sys.modules.get(n) for n in watched};temporary=None
    blocked={'torch','numpy','isaaclab','isaacsim','omni','pxr','warp','psutil','fcntl','paramiko'}
    def imported(name,*a,**kw):
        need(name.split('.')[0] not in blocked,'metadata import attempted native/resource package: '+name)
        return old_import(name,*a,**kw)
    try:
        if actual_root is None:
            temporary=tempfile.TemporaryDirectory(prefix='phase1_capture_metadata_');root=Path(temporary.name)
            for alias,(source,info) in bundle['sources'].items():
                raw=source.read_bytes();need((len(raw),H(raw))==(info['bytes'],info['SHA']),'source changed before metadata import')
                target=root/safe_relative(alias);target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as stream:stream.write(raw)
        else:root=Path(actual_root)
        for name,row in BOOTSTRAP_ORIGINAL_SOURCES.items():
            alias=row['relative'];source,info=bundle['originals'][alias]
            need(bundle['materials'][alias]==(source,info) and alias not in bundle['sources'],
                 'bootstrap must use complete original baseline, not an overlay: '+name)
            need((info['bytes'],info['SHA'])==(row['bytes'],row['SHA256']),
                 'independent original bootstrap helper PIN differs: '+name)
            if actual_root is None:
                raw=source.read_bytes();need((len(raw),H(raw))==(info['bytes'],info['SHA']),
                    'complete original bootstrap source changed before metadata import: '+name)
                target=root/safe_relative(alias);target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as stream:stream.write(raw)
        sys.path.insert(0,str(root));sys.dont_write_bytecode=True;builtins.__import__=imported
        builtins.open,io.open,os.stat,os.lstat=filesystem(old_open),filesystem(old_io_open),filesystem(old_stat),filesystem(old_lstat)
        for n in watched:
            if n not in BOOTSTRAP_ORIGINAL_SOURCES:sys.modules.pop(n,None)
        close=verify_close_dependency_imports(root/'app_close_semantics_v5.py',root/'resume_runtime_contracts_v3.py')
        contract=importlib.import_module('phase1_capture_contract');runtime=importlib.import_module('phase1_capture_runtime')
        selected=contract.validate_plan(plan,bundle['index'])
        validate_preservation(plan['retained_static_inventory'],bundle['materials'],originals=bundle['originals'])
        need(runtime.source_index()==bundle['index'],'runtime actual full installed source_index differs')
        core=runtime.core();core_raw=Path(core.__file__).read_bytes()
        need((len(core_raw),H(core_raw))==(37927,'7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e'),'actual full canonical7a092 alias differs')
        runtime.dependency('source_api','phase1_deps/sensor/source_api.py');runtime.dependency('passive_capture','phase1_deps/sensor/passive_capture.py')
        runtime.dependency('phase1_sealed_actuation_tap','phase1_deps/actuation/actuation_tap.py')
        importlib.import_module('phase1_capture_observer');worker=importlib.import_module('worker_passive_interface_v1')
        bootstrap=worker.bootstrap_original_helpers(root)
        origin=bootstrap['origin_evidence']
        need(origin['source_version']==2 and origin['parent_five_storage_calls']==origin['capacity_ctor_calls']==origin['SDK_constructor_calls']==0,
             'bootstrap import must not call storage/capacity/SDK constructors')
        need({r['relative'] for r in origin['sources']}=={r['relative'] for r in BOOTSTRAP_ORIGINAL_SOURCES.values()},
             'bootstrap actual full source origin set differs')
        importlib.import_module('pose_cache_runtime_adapter_v3');importlib.import_module('frozen_a1_raw35_v1')
        task=runtime.make_task(selected[0],plan,2000.,[101,102])  # placeholders only, validate_task not fstat/admission
        need(task['controls']==plan['capture_controls'] and task['model_PT_reads']==0 and not any(k in task for k in ('teacher_path','source_path','checkpoint','a1_producer')),'synthetic task carries model fallback')
        negatives=0
        for key,value in (('controls',160),('seed',20260929),('requested_roles',['E3','W35']),('checkpoint','NO_FILE_MODEL_DESCRIPTOR')):
            bad=copy.deepcopy(task);bad[key]=value
            try:contract.validate_task(bad)
            except ValueError:negatives+=1
            else:raise ValueError('capture task negative unexpectedly passed: '+key)
        need(not any(n.split('.')[0] in blocked for n in sys.modules),'native/resource module leaked into metadata import')
        return dict(kind='REAL_WHOLE_SAFE_CAPTURE_METADATA_IMPORT_CHECK_V2',source_derivation_version=2,original_helper_bootstrap=origin,passed=True,purpose=PURPOSE,requested_roles=['E3'],
                    task_controls=task['controls'],negative_tasks_rejected=negatives,placeholder_fds_not_inspected=True,
                    complete_AppV6_Base=close,canonical7a092_whole_module=True,full_safe_module_names=list(watched),
                    native_worker_main_executed=False,native_layer='COMPLETE_PIN_AST_RETAINED_NOT_IMPORTED',
                    actual_SDK_binding=None,gate1='UNKNOWN',capture_interface_passed=False,resource_operations=0,model_reads=0)
    finally:
        builtins.__import__=old_import;sys.path[:]=old_path;sys.dont_write_bytecode=old_bytecode
        builtins.open,io.open,os.stat,os.lstat=old_open,old_io_open,old_stat,old_lstat
        for n,value in before.items():
            if value is None:sys.modules.pop(n,None)
            else:sys.modules[n]=value
        if temporary is not None:
            need(lexical(temporary.name).parent==lexical(tempfile.gettempdir()) and Path(temporary.name).name.startswith('phase1_capture_metadata_'),'metadata temporary cleanup target differs')
            temporary.cleanup()


def preflight_summary(prepared):
    inv=prepared['plan']['retained_static_inventory']
    return dict(kind='SOURCE_PHASE1_CAPTURE_PREFLIGHT_NOT_ADMISSION_V2',purpose=PURPOSE,group_id=prepared['plan']['group_id'],
        new_root=str(prepared['new_root']),requested_roles=['E3'],deferred_roles=list(ROLES[1:]),capture_controls=prepared['plan']['capture_controls'],
        materials=len(prepared['materials']),original_static_files=len(inv['baseline']),baseline_SHA256=inv['SHA256'],
        original_logical_tree_SHA256=inv['baseline_provenance']['original_logical_tree_SHA256'],
        source_to_retained=inv['baseline_provenance']['source_to_retained'],native_boundary=prepared['boundary'],
        source_pins=prepared['source_bundle']['receipt'],metadata_validation=prepared['metadata_validation'],
        materialized=False,source_native_enabled=False,staged=False,dispatched=False,parent_launches=0,
        model_reads=0,actual_SDK_executed=False,gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)


def stage(prepared):
    root=prepared['new_root'];need(not root.is_symlink() and not root.exists(),'actual stage root already exists')
    root.mkdir(parents=False,exist_ok=False)
    put_json(root/'STAGE_BEGIN_PHASE1_CAPTURE_V1.json',preflight_summary(prepared))
    try:
        written={}
        for rel,(source,info) in sorted(prepared['materials'].items()):
            target=root/safe_relative(rel);target.parent.mkdir(parents=True,exist_ok=True)
            digest=hashlib.sha256();count=0
            with source.open('rb') as incoming,target.open('xb') as outgoing:
                for chunk in iter(lambda:incoming.read(1024*1024),b''):
                    outgoing.write(chunk);digest.update(chunk);count+=len(chunk)
                outgoing.flush();os.fsync(outgoing.fileno())
            observed=dict(bytes=count,SHA=digest.hexdigest());need(observed==info,'source changed after preflight: '+rel);written[rel]=observed
        plan=copy.deepcopy(prepared['plan']);inv=plan['retained_static_inventory']
        inv['installed']=[dict(relative=r['relative'],bytes=written[r['relative']]['bytes'],SHA256=written[r['relative']]['SHA']) for r in inv['baseline']]
        inv['installed_status']='ACTUAL_STREAM_HASH_VERIFIED_STATIC_FILES'
        validate_preservation(inv,prepared['materials'],originals=prepared['originals'],observed=written)
        raw=(json.dumps(plan,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();need(len(raw)<=64*1024*1024,'full inventory plan exceeds actual runtime metadata64MiB bound')
        put_once(root/'GROUP_PLAN.json',raw)
        validation=metadata_validate(prepared['source_bundle'],plan,actual_root=root)
        put_json(root/'MATERIALIZED_STATIC_FILES_PHASE1_CAPTURE_V1.json',dict(files=[dict(relative=r,**i) for r,i in sorted(written.items())],
             source_pins=prepared['source_bundle']['receipt'],baseline_SHA256=inv['SHA256'],original_logical_tree_SHA256=inv['baseline_provenance']['original_logical_tree_SHA256']))
        receipt=dict(kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V2',purpose=PURPOSE,materialized=True,parent_launches=0,
            group_id=plan['group_id'],root=str(root),requested_roles=['E3'],capture_controls=plan['capture_controls'],files=len(written),
            GROUP_PLAN_bytes=len(raw),GROUP_PLAN_SHA256=H(raw),baseline_SHA256=inv['SHA256'],source_to_retained=inv['baseline_provenance']['source_to_retained'],
            metadata_validation=validation,source_native_enabled=False,staged=False,dispatched=False,actual_SDK_executed=False,
            model_reads=0,resource_operations=0,gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
        put_json(root/COMPLETE_NAME,receipt);return receipt
    except BaseException:
        put_json(root/'STAGE_ERROR_PHASE1_CAPTURE_V1.json',dict(error=traceback.format_exc(),materialized=False,
            root_consumed_no_same_root_retry=True,parent_launches=0,actual_SDK_executed=False))
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('original-group-root','source-root','native-root','new-root'):parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--group-id',required=True);parser.add_argument('--gpu-uuid',required=True)
    parser.add_argument('--controls',type=int,choices=(64,128),default=64)
    modes=parser.add_mutually_exclusive_group(required=True);modes.add_argument('--preflight-only',action='store_true');modes.add_argument('--stage',action='store_true')
    args=parser.parse_args();prepared=prepare(args.original_group_root,args.source_root,args.native_root,args.new_root,args.group_id,args.gpu_uuid,controls=args.controls)
    print(json.dumps(stage(prepared) if args.stage else preflight_summary(prepared),indent=2,allow_nan=False))


if __name__=='__main__':main()
