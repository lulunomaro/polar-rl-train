"""Pending-final-pin V4 SOURCE derivation template. No prepare/stage/native calls.
Until FINAL_WORKER4 is populated from the parent's exact final sealed receipt,
main raises before creating any derived entry/helper or source seal.
"""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
R=HERE.parent
V3=R/'source_phase1_capture_materializer_v3'
ENTRY_PIN=(42437,'2a4213d95939216f3a91db6c1739a443907aadf33c4f615aa897eace5a915425')
HELPER_PIN=(10078,'11f43dad3d0f29f0fb1b54995c16d3bf2000586481dda7870dd68af6bc9f50c2')
# Exact final worker4 seal bytes/SHA, complete13 root and index bytes/SHA only.
# This is source-generation binding, NOT a new native approval boolean or gate.
FINAL_WORKER4={'seal': (2919, 'ba3409a5450e378ea97eac64f0fec4c3409ac974a4c3378d0c6e6a6cfc405180'), 'root': '758dc867cc4040a6f1eb9f587cc88f69a3866e03a9553290128a1681cda039e8', 'index': (134423, '75e36c0255a3b354dd0efeec33600f9b38d51ca28484de2dbed55db865fc7b2d')}

# Actual candidate index interface read on 2026-11-03. Still no worker4 pins bound.
# This text adds proof-only members within the existing load_sources function.
BOUNDARY_SOURCE_ADDITION='''    boundary=index['boundary_device_source_contract']
    need(boundary['read_only_fixture_source_not_runtime_dependency'] is True
         and boundary['parent_CPU_result']=='NOT_REPRESENTED_BY_THIS_SOURCE_SEAL'
         and boundary['actual_Torch_CPU_executed_here'] is False,'boundary fixture is SOURCE proof only')
    record=boundary['seal'];path=reference_path(source_root,record['path'])
    members,boundary_receipt=verify_package(path.parent,record['SHA256'],8)
    seal,seal_raw=metadata(path)
    need(len(seal_raw)==record['bytes'] and seal.get('frozen') is True and seal.get('source_only') is True,
         'complete frozen SOURCE8 boundary fixture required')
    need(seal['content_root_sha256']==record['content_root_sha256']==canonical(seal['files']),
         'boundary fixture complete8 canonical root differs')
    expected_rows={r['relative']:(r['bytes'],r['SHA256'])for r in record['members']}
    actual_rows={r:(i['bytes'],i['SHA'])for r,(_,i)in members.items()if r!='SOURCE_SEAL.json'}
    need(len(record['members'])==8 and expected_rows==actual_rows,'boundary fixture complete8 member listing differs')
    source_pins,_=metadata(members['SOURCE_PINS.json'][0]);source_receipt,_=metadata(members['SOURCE_RECEIPT.json'][0])
    need(source_pins['files']==[r for r in seal['files']if r['relative']not in('SOURCE_PINS.json','SOURCE_RECEIPT.json')],
         'boundary fixture source pin member listing differs')
    contract=boundary['source_contract']
    need(source_pins['source_contract']==source_receipt['source_contract']==contract,
         'boundary fixture sealed source contract differs from final worker index')
    need(contract['kind']=='PHASE1_BOUNDARY_DEVICE_SOURCE_CONTRACT_V1' and contract['source_only'] is True
         and contract['actual_V3_flags_shape_dtype_device'] is None and contract['actual_env_device_type'] is None
         and source_receipt['actual_Torch_CPU_fixture_executed'] is False and source_receipt['actual_reports_read'] is False,
         'SOURCE fixture is not actual CPU/native flag evidence')
    references=contract['source_paths'];need(set(references)=={'canonical','bridge','worker'},'boundary fixture source reference set differs')
    for name,row in references.items():
        ref=reference_path(source_root,row['path']);info=identity(ref)
        need((info['bytes'],info['SHA'])==(row['bytes'],row['SHA256']),'boundary fixture actual source reference differs: '+name)
        ast.parse(ref.read_bytes())
        alias='phase1_source_proof/boundary_device_references/'+safe_relative(ref.relative_to(source_root).as_posix())
        need(alias not in sources,'boundary fixture source reference alias collision');sources[alias]=(ref,info)
    for rel,value in members.items():
        alias='phase1_source_proof/boundary_device_source_contract/'+safe_relative(rel)
        need(alias not in sources,'boundary fixture source proof alias collision');sources[alias]=value
    boundary_receipt.update(read_only_fixture_source_not_runtime_dependency=True,source_contract_unchanged=True,
        actual_source_references_verified=3,fixture_or_CPU_module_imports=0,parent_CPU_report_dependency=False,
        actual_V3_flags_shape_dtype_device=None,actual_native_binding='UNKNOWN')
'''


def H(raw):return hashlib.sha256(raw).hexdigest()


def replace(text,old,new):
    if text.count(old)!=1:raise ValueError('one exact V4 derivation target required: '+old[:100])
    return text.replace(old,new,1)


def put(name,raw):
    path=HERE/name
    if path.exists():
        if path.read_bytes()!=raw:raise ValueError('existing NEW source differs: '+name)
    else:
        with path.open('xb')as stream:stream.write(raw)


def functions(raw):
    return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}


def main():
    if FINAL_WORKER4 is None:raise ValueError('PENDING_FINAL_WORKER4_PINS; no entry, mirror, seal or ready claim generated')
    pins=FINAL_WORKER4
    if set(pins)!={'seal','root','index'}:raise ValueError('exact final worker4 source pin schema required')
    raw=(V3/'stage_phase1_capture_v3.py').read_bytes()
    helper=(V3/'static_source_helpers_v1.py').read_bytes()
    if (len(raw),H(raw))!=ENTRY_PIN or (len(helper),H(helper))!=HELPER_PIN:raise ValueError('immutable V3 full source inputs differ')
    text=raw.decode()
    text=replace(text,"WORKER_FOLDER='source_phase1_capture_worker_v3'","WORKER_FOLDER='source_phase1_capture_worker_v4'")
    text=replace(text,"WORKER_SEAL_PIN=(2920, '80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da')",'WORKER_SEAL_PIN='+repr(pins['seal']))
    text=replace(text,"WORKER_ROOT_SHA='b1b6ec96f93561d201c307cab9b17fbdc8591c6e362cef45a29ee63419f87963'",'WORKER_ROOT_SHA='+repr(pins['root']))
    text=replace(text,"WORKER_INDEX_PIN=(124202, 'bdeea3f057fb922bd9ae2670dcbf19188f651ca64ab2cbb0331f56a5a1124797')",'WORKER_INDEX_PIN='+repr(pins['index']))
    text=replace(text,'SOURCE_DERIVATION_VERSION=3','SOURCE_DERIVATION_VERSION=4\nV3_ENTRY_SHA256='+repr(ENTRY_PIN[1]))
    text=replace(text,"index.get('source_version')==3,'final SOURCE V3 with preserved typed index required'","index.get('source_version')==4,'final SOURCE V4 with preserved typed index required'")
    text=replace(text,"kind='ACTUAL_COMPLETE_TEXT_SOURCE_PIN_VERIFICATION_PHASE1_V3',source_derivation_version=3", "kind='ACTUAL_COMPLETE_TEXT_SOURCE_PIN_VERIFICATION_PHASE1_V4',source_derivation_version=4")
    text=replace(text,'    B2_inputs,B2_receipt=verify_B2_source_closure(source_root,index)',BOUNDARY_SOURCE_ADDITION+'    B2_inputs,B2_receipt=verify_B2_source_closure(source_root,index)')
    text=replace(text,'v2_entry_SHA256=V2_ENTRY_SHA256,B2_source_closure=B2_receipt','v2_entry_SHA256=V2_ENTRY_SHA256,v3_entry_SHA256=V3_ENTRY_SHA256,boundary_device_source_contract=boundary_receipt,B2_source_closure=B2_receipt')
    text=replace(text,"kind='REAL_WHOLE_SAFE_CAPTURE_METADATA_IMPORT_CHECK_V3',source_derivation_version=3", "kind='REAL_WHOLE_SAFE_CAPTURE_METADATA_IMPORT_CHECK_V4',source_derivation_version=4")
    text=replace(text,"kind='SOURCE_PHASE1_CAPTURE_PREFLIGHT_NOT_ADMISSION_V3'","kind='SOURCE_PHASE1_CAPTURE_PREFLIGHT_NOT_ADMISSION_V4'")
    text=replace(text,"kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V3'","kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V4'")
    new=text.encode();old_functions=functions(raw);new_functions=functions(new)
    changed=sorted(name for name in old_functions if old_functions[name]!=new_functions[name])
    if set(changed)!={'load_sources','metadata_validate','preflight_summary','stage'}:raise ValueError('unexpected V4 source function diff: '+repr(changed))
    if set(new_functions)!=set(old_functions):raise ValueError('V4 adds no new runtime or closure helper')
    for protected in ('normalize_B2_source_paths','verify_B2_source_closure','native_boundary','prepare','retain_originals','validate_preservation','main'):
        if old_functions[protected]!=new_functions[protected]:raise ValueError('protected V3 complete function changed: '+protected)
    put('static_source_helpers_v1.py',helper);put('stage_phase1_capture_v4.py',new)
    print(json.dumps(dict(kind='PHASE1_V4_MINIMAL_SOURCE_DERIVED',entry='stage_phase1_capture_v4.py',bytes=len(new),SHA256=H(new),
        changed_functions=changed,unchanged_functions=sorted(set(old_functions)-set(changed)),added_helpers=0,
        full_original_helpers=17,wire_V1_unchanged=True,actual_prepare_preflight_stage_dispatch_executed=False),indent=2))


if __name__=='__main__':main()
