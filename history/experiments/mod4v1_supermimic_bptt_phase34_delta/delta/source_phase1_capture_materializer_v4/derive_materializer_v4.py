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
FINAL_WORKER4=None


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
    text=replace(text,'v2_entry_SHA256=V2_ENTRY_SHA256,B2_source_closure=B2_receipt','v2_entry_SHA256=V2_ENTRY_SHA256,v3_entry_SHA256=V3_ENTRY_SHA256,B2_source_closure=B2_receipt')
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
