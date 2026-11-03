"""SOURCE-only V4: one existing device argument; no physical/resource changes."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
V3=ROOT/'source_phase1_capture_worker_v3'
V2=ROOT/'source_phase1_capture_worker_v2'
BOUNDARY=ROOT/'source_phase1_boundary_device_contract_v1'
V3_SEAL='80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da'
V3_ROOT='b1b6ec96f93561d201c307cab9b17fbdc8591c6e362cef45a29ee63419f87963'
BOUNDARY_SEAL='c9fae49e96b7042863372e7fb681c7c93fd8ce733646908222c9af6f7d306bdc'
BOUNDARY_ROOT='5b4d0134e8ec0d828adef1fae8156d195ede032eacea2476457a403162e9e106'
INHERITED=('phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py','worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py')
OLD='boundary=core().OriginalEpisodeBoundary(torch,env.device,n=80)'
NEW='boundary=core().OriginalEpisodeBoundary(torch,bridge.device,n=80)'


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def identity(path):
    path=Path(path)
    if path.suffix.lower() not in ('.py','.json','.md','.txt'):raise ValueError('SOURCE suffix required')
    raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw,filename=str(path))
    return dict(bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def check_row(row,path=None):
    path=Path(path if path is not None else row['path'])
    actual=identity(path)
    if actual!=dict(bytes=row['bytes'],SHA256=row.get('SHA256',row.get('sha256'))):raise ValueError('full SOURCE pin mismatch: '+str(path))
    return dict(path=str(path),**actual)


def sealed_pack(folder,digest,count,root):
    path=folder/'SOURCE_SEAL.json';info=identity(path)
    if info['SHA256']!=digest:raise ValueError('upstream SOURCE seal differs')
    value=json.loads(path.read_text(encoding='utf-8'))
    if len(value['files'])!=count or value['content_root_sha256']!=root or hashlib.sha256(canonical(value['files'])).hexdigest()!=root:
        raise ValueError('upstream SOURCE full root/count differs')
    members=[]
    for row in value['files']:
        rel=Path(row['relative'])
        if rel.is_absolute() or '..' in rel.parts:raise ValueError('upstream member path escape')
        item=check_row(row,folder/rel);members.append(dict(relative=row['relative'],bytes=item['bytes'],SHA256=item['SHA256']))
    return dict(path=str(path),**info,members=members,content_root_sha256=root)


def full_source_import(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    try:spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name,None);raise
    return module


def upstream():
    sealed_pack(V3,V3_SEAL,13,V3_ROOT)
    return full_source_import(V3/'prepare_sources.py','_phase1_v4_full_frozen_V3_source_preparer')


def verify_v3():
    sealed=sealed_pack(V3,V3_SEAL,13,V3_ROOT);p=upstream()
    p.verify_frozen_v2();sensor,manifest=p.verify_B2();diagnostics=p.verify_diagnostics()
    old=json.loads((V3/'CAPTURE_SOURCE_INDEX.json').read_text(encoding='utf-8'))
    if old['dependency_seals']['sensor']!=sensor or old['sensor_source_manifest']!=manifest or old['sensor_reset_diagnostic_source_references']!=diagnostics:
        raise ValueError('retained full B2/diagnostics closure differs')
    for row in old['original17']+old['new_sources']+old['dependency_sources']+old['bootstrap_original_sources']:check_row(row)
    for name in INHERITED:
        before=(V3/name).read_bytes();after=(HERE/name).read_bytes()
        expected=before
        if name=='worker_passive_interface_v1.py':
            if before.count(OLD.encode())!=1:raise ValueError('exact single old boundary constructor required')
            expected=before.replace(OLD.encode(),NEW.encode())
            if after.count(NEW.encode())!=1 or OLD.encode() in after:raise ValueError('exact single new boundary constructor required')
        if expected!=after:raise ValueError('V4 candidate diff exceeds one device argument: '+name)
    return sealed,old


def verify_boundary_contract():
    sealed=sealed_pack(BOUNDARY,BOUNDARY_SEAL,8,BOUNDARY_ROOT)
    module=full_source_import(BOUNDARY/'boundary_device_contract.py','_phase1_v4_full_boundary_source_contract')
    evidence=module.verify_source_contract()
    receipt=json.loads((BOUNDARY/'SOURCE_RECEIPT.json').read_text(encoding='utf-8'))
    if receipt['actual_Torch_CPU_fixture_executed'] or receipt['actual_V3_root_cause_confirmed']:raise ValueError('SOURCE fixture scope differs')
    return dict(seal=sealed,source_contract=evidence,read_only_fixture_source_not_runtime_dependency=True,
                parent_CPU_result='NOT_REPRESENTED_BY_THIS_SOURCE_SEAL',actual_Torch_CPU_executed_here=False)


def build_index():
    if (HERE/'SOURCE_SEAL.json').exists():raise RuntimeError('frozen V4; new lineage required')
    v3,old=verify_v3();boundary=verify_boundary_contract();index=copy.deepcopy(old)
    index['source_version']=4
    for row in index['new_sources']:
        path=HERE/row['install_relative'];row.update(path=str(path),**identity(path))
    index['source_derivation']=dict(kind='PHASE1_CAPTURE_WORKER_V4_EXISTING_BRIDGE_DEVICE_ARGUMENT_ONLY',source_version=4,
        v3_frozen_seal=v3,inherited_v3_source_derivation=old['source_derivation'],
        actual_bootstrap_source_evidence=old['source_derivation']['actual_bootstrap_source_evidence'],
        candidate_logic_diff_count=1,worker_main_diff_count=1,old_call=OLD,new_call=NEW,
        unchanged_V3_candidate_files=[name for name in INHERITED if name!='worker_passive_interface_v1.py'],
        preserved_V1_typed_protocol=True,parent_source_unchanged=True,
        canonical_boundary_unchanged=True,original_bridge_bool_unchanged=True,new_SDK_getters=0,
        cause_status='SOURCE_CANDIDATE_NOT_ACTUAL_V3_ROOT_CAUSE_CONFIRMED',actual_V3_flags_shape_dtype_device=None,
        actual_reports_read_here=False,actual_V4_native_or_resource_run=False)
    index['boundary_device_source_contract']=boundary
    projection=copy.deepcopy(index);projection['source_version']=3;projection['source_derivation']=old['source_derivation']
    projection['new_sources']=old['new_sources'];projection.pop('boundary_device_source_contract')
    if projection!=old:raise ValueError('V4 metadata diff exceeds one candidate source and readonly source contract')
    path=HERE/'CAPTURE_SOURCE_INDEX.json';text=json.dumps(index,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    if path.exists():
        if path.read_text(encoding='utf-8')!=text:path.write_text(text,encoding='utf-8',newline='\n')
    else:
        with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(text)
    return dict(index=identity(path),source_version=4,original17=len(index['original17']),new_sources=len(index['new_sources']),
                dependencies=len(index['dependency_sources']),dependency_sealed_members={name:len(row['members']) for name,row in index['dependency_seals'].items()},
                B2_original_source_files=155,B2_original_pin_references=435,boundary_contract_sealed_members=8,
                candidate_logic_diff_count=1,new_SDK_getters=0,actual_Torch_CPU_or_native_or_resource=False)


if __name__=='__main__':print(json.dumps(build_index(),indent=2))
