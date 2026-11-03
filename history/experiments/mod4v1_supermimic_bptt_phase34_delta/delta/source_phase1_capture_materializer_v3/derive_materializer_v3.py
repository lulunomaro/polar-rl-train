"""Derive NEW V3 SOURCE only from immutable full V2; no prepare/stage/worker execution."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent;R=HERE.parent
V2=R/'source_phase1_capture_materializer_v2'
ENTRY_PIN=(34834,'e39fc8936136f89e708df6a9a26911135d0c1616c641564cf155235ff0d06f6d')
HELPER_PIN=(10078,'11f43dad3d0f29f0fb1b54995c16d3bf2000586481dda7870dd68af6bc9f50c2')
WORKER_SEAL=(2920,'80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da')
WORKER_ROOT='b1b6ec96f93561d201c307cab9b17fbdc8591c6e362cef45a29ee63419f87963'
WORKER_INDEX=(124202,'bdeea3f057fb922bd9ae2670dcbf19188f651ca64ab2cbb0331f56a5a1124797')
B2_SEAL='be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a'
B2_ROUTING={
 'CURB_PROTECTED878':(4814,'671f77ddef5fbd79de8dafc54213ff754cfc70ac5a9d9611680e9c76c021cfc5'),
 'CURB_INDEPENDENT113':(4873,'b906aaacefe79f29e001bee015de1d4c8ee930bf936a9996f79f0a72ee103fd3'),
 'SLOPE135':(5390,'f9a0a42c6b1390e38013a410e454da4a9d63569d47f014c3b6f6ea4ca7615b41'),
 'SLOPE_INDEPENDENT50':(4834,'8ccc2f890c90eeeea652b8b10cd8a96518ba996b52294b20d2f525ea72f716e7')}


def H(raw):return hashlib.sha256(raw).hexdigest()
def replace(text,old,new):
    if text.count(old)!=1:raise ValueError('one exact derivation target required: '+old[:100])
    return text.replace(old,new,1)
def put(name,raw):
    path=HERE/name
    if path.exists():
        if path.read_bytes()!=raw:raise ValueError('existing NEW source differs: '+name)
    else:
        with path.open('xb') as stream:stream.write(raw)
def functions(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}


B2_HELPERS=r'''
def normalize_B2_source_paths(value, source_root):
    """Derived comparison only. Exact explicit roots, never suffix/path/SHA repair."""
    root=lexical(source_root).as_posix().rstrip('/')+'/'
    provenance='F:/RMPOLAR-RL/'+R_NAME+'/'
    def walk(item):
        if type(item) is list:return [walk(v) for v in item]
        if type(item) is dict:
            result={}
            for key,child in item.items():
                if key=='source_path':
                    need(type(child) is str and '\x00' not in child,'manifest source_path must be text')
                    path=child.replace('\\','/')
                    need(not any(p in ('.','..') for p in path.split('/')),'manifest source_path dot traversal')
                    # A test/source mirror may be nested inside the original R.
                    # Its explicitly supplied root wins; never guess by suffix.
                    prefix=root if path.startswith(root) else provenance
                    need(path.startswith(prefix),'manifest source_path is outside explicit R roots')
                    result[key]=safe_relative(path[len(prefix):])
                else:result[key]=walk(child)
            return result
        return item
    return walk(value)


def verify_B2_source_closure(source_root, index):
    """Read full sealed manifest/plant source, call actual B2 SOURCE builder only."""
    source_root=lexical(source_root);record=index['sensor_source_manifest']
    manifest_path=reference_path(source_root,record['path']);manifest,raw=metadata(manifest_path,2*1024*1024)
    need((len(raw),H(raw))==(record['bytes'],record['SHA256'])==(336133,'2801135d1ff028f09a5eb7cd571cc3ca90694b60340d17e62374a42cbe60eaca'),
         'sealed B2 manifest raw identity differs before derived comparison')
    normalized=normalize_B2_source_paths(manifest,source_root);found={};references=0
    def collect(item):
        nonlocal references
        if type(item) is dict:
            if 'source_path' in item or 'source_sha256' in item:
                need({'source_path','source_sha256'}<=set(item),'incomplete B2 source pin')
                rel=safe_relative(item['source_path']);digest=item['source_sha256'];references+=1
                need(is_sha(digest) and (rel not in found or found[rel]==digest),'B2 source pin disagreement')
                found[rel]=digest
            for child in item.values():collect(child)
        elif type(item) is list:
            for child in item:collect(child)
    collect(normalized)
    closure=record['original_source_closure'];need(references==closure['pin_references']==435 and len(found)==closure['unique_full_source_files']==155,
        'complete B2 435 references/155 full source closure required')
    listed={};inputs={}
    for row in closure['sources']:
        path=reference_path(source_root,row['path']);rel=path.relative_to(source_root).as_posix()
        need(rel not in listed and path.suffix=='.py','duplicate/non-Python B2 original source')
        info=identity(path);need((info['bytes'],info['SHA'])==(row['bytes'],row['SHA256']) and found.get(rel)==info['SHA'],
            'actual complete B2 original source pin differs: '+rel)
        ast.parse(path.read_bytes());listed[rel]=info['SHA'];inputs[rel]=(path,info)
    need(listed==found,'B2 source closure is incomplete or has extras')
    # build_manifest actually reads these four entry-routing JSONs in addition to
    # the 155 Python files. Their bytes are pinned separately, never inferred.
    for role,pin in B2_ENTRY_ROUTING_PINS.items():
        rel='discovery/reward_command_audit_v1/'+role+'/E1_CANONICAL_SOURCE_METADATA.json'
        path=reference_path(source_root,rel);value,raw=metadata(path)
        need((len(raw),H(raw))==pin,'B2 source-builder routing JSON differs: '+role)
        inputs[rel]=(path,dict(bytes=len(raw),SHA=H(raw)))
    api_row=next(r for r in index['dependency_sources'] if r['install_relative']=='phase1_deps/sensor/source_api.py')
    api_path=reference_path(source_root,api_row['path']);api_info=identity(api_path)
    need((api_info['bytes'],api_info['SHA'])==(31456,'a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62'),'actual complete B2 source API differs')
    name='_phase1_materializer_v3_original_B2_source_api';before=sys.modules.get(name)
    spec=importlib.util.spec_from_file_location(name,api_path);api=importlib.util.module_from_spec(spec);sys.modules[name]=api
    try:
        spec.loader.exec_module(api)
        rebuilt=api.build_manifest(root=source_root)  # original pure read/AST/compile; no reset/adapter constructor
        need(normalize_B2_source_paths(rebuilt,source_root)==normalized,'actual original B2 whole manifest regeneration differs')
    finally:
        if before is None:sys.modules.pop(name,None)
        else:sys.modules[name]=before
    diagnostics=index['sensor_reset_diagnostic_source_references']
    rows=[diagnostics['final_handoff']]+diagnostics['source_references'];need(len(rows)==5,'complete diagnostic final+4 references required')
    handoff=None
    for row in rows:
        path=reference_path(source_root,row['path']);rel=path.relative_to(source_root).as_posix();info=identity(path)
        need((info['bytes'],info['SHA'])==(row['bytes'],row['SHA256']),'actual diagnostic source pin differs: '+rel)
        if path.suffix=='.py':ast.parse(path.read_bytes())
        inputs[rel]=(path,info)
        if row is diagnostics['final_handoff']:handoff=json.loads(path.read_bytes())
    need(handoff['status']=='PASS' and handoff['B2_source_seal']['sha256']==DEPENDENCY_SEALS['sensor'][1],'diagnostic B2 final handoff differs')
    references_by_rel={reference_path(source_root,r['path']).relative_to(source_root).as_posix():(r['bytes'],r['sha256']) for r in handoff['source_diagnosis_files']}
    expected_by_rel={reference_path(source_root,r['path']).relative_to(source_root).as_posix():(r['bytes'],r['SHA256']) for r in diagnostics['source_references']}
    need(references_by_rel==expected_by_rel,'diagnostic referenced file set differs')
    return inputs,dict(manifest_bytes=record['bytes'],manifest_SHA256=record['SHA256'],
        original_source_pin_references=references,actual_original_Python_files=len(found),extra_entry_routing_JSON_files=4,
        diagnostic_source_references=4,diagnostic_final_handoff=1,source_dependency_files=len(inputs),
        full_manifest_regenerated_equal_after_explicit_R_source_path_normalization=True,
        actual_original_B2_API_called='build_manifest(root=actual_source_mirror_root)',
        other_fields_hashes_numbers_qualnames_statuses_unchanged=True,plant_modules_imported=False,
        reset_or_adapter_or_SDK_constructor_calls=0,actual_runtime_root_binding='UNKNOWN',native_executed=False)
'''


def main():
    raw=(V2/'stage_phase1_capture_v2.py').read_bytes();helper=(V2/'static_source_helpers_v1.py').read_bytes()
    if (len(raw),H(raw))!=ENTRY_PIN or (len(helper),H(helper))!=HELPER_PIN:raise ValueError('immutable V2 source pins differ')
    text=raw.decode()
    text=replace(text,"WORKER_FOLDER='source_phase1_capture_worker_v2'","WORKER_FOLDER='source_phase1_capture_worker_v3'")
    text=replace(text,"WORKER_SEAL_PIN=(2815, 'caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5')",'WORKER_SEAL_PIN='+repr(WORKER_SEAL))
    text=replace(text,"WORKER_ROOT_SHA='83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2'",'WORKER_ROOT_SHA='+repr(WORKER_ROOT))
    text=replace(text,"WORKER_INDEX_PIN=(65961, 'cdb2ca55c08a544cd01e462b7ce27261900f3b6ebaffb4784350717f756b7cf7')",'WORKER_INDEX_PIN='+repr(WORKER_INDEX))
    text=replace(text,"'sensor':(13,'3d5fd4febf9232a8113b4d93dbf8d3d6a19658690e973d6485c1aedc39e18881')","'sensor':(13,"+repr(B2_SEAL)+')')
    text=replace(text,'SOURCE_DERIVATION_VERSION=2','SOURCE_DERIVATION_VERSION=3\nV2_ENTRY_SHA256='+repr(ENTRY_PIN[1])+'\nB2_ENTRY_ROUTING_PINS='+repr(B2_ROUTING))
    text=replace(text,"index.get('source_version')==2,'final SOURCE V2 with preserved typed index required'","index.get('source_version')==3,'final SOURCE V3 with preserved typed index required'")
    needle="    return dict(sources=sources,index=index,source_root=source_root,\n        receipt=dict(kind='ACTUAL_COMPLETE_TEXT_SOURCE_PIN_VERIFICATION_PHASE1_V2',source_derivation_version=2,v1_entry_SHA256=V1_ENTRY_SHA256,worker=worker_receipt,"
    replacement="    B2_inputs,B2_receipt=verify_B2_source_closure(source_root,index)\n    for rel,value in B2_inputs.items():\n        alias='phase1_source_proof/B2_original_dependencies/'+safe_relative(rel)\n        need(alias not in sources,'B2 source proof alias collision');sources[alias]=value\n    return dict(sources=sources,index=index,source_root=source_root,B2_source_inputs=B2_inputs,\n        receipt=dict(kind='ACTUAL_COMPLETE_TEXT_SOURCE_PIN_VERIFICATION_PHASE1_V3',source_derivation_version=3,v1_entry_SHA256=V1_ENTRY_SHA256,v2_entry_SHA256=V2_ENTRY_SHA256,B2_source_closure=B2_receipt,worker=worker_receipt,"
    text=replace(text,needle,replacement)
    text=replace(text,'\ndef native_boundary(native_root):',B2_HELPERS+'\n\ndef native_boundary(native_root):')
    text=replace(text,"kind='REAL_WHOLE_SAFE_CAPTURE_METADATA_IMPORT_CHECK_V2',source_derivation_version=2","kind='REAL_WHOLE_SAFE_CAPTURE_METADATA_IMPORT_CHECK_V3',source_derivation_version=3")
    text=replace(text,"kind='SOURCE_PHASE1_CAPTURE_PREFLIGHT_NOT_ADMISSION_V2'","kind='SOURCE_PHASE1_CAPTURE_PREFLIGHT_NOT_ADMISSION_V3'")
    text=replace(text,"kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V2'","kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V3'")
    new=text.encode();old_functions=functions(raw);new_functions=functions(new)
    changed=sorted(n for n in old_functions if old_functions[n]!=new_functions[n])
    if set(changed)!={'load_sources','metadata_validate','preflight_summary','stage'}:raise ValueError('unexpected V3 function diff: '+repr(changed))
    if set(new_functions)-set(old_functions)!={'normalize_B2_source_paths','verify_B2_source_closure'}:raise ValueError('unexpected V3 helper additions')
    put('static_source_helpers_v1.py',helper);put('stage_phase1_capture_v3.py',new)
    print(json.dumps(dict(kind='PHASE1_V3_NARROW_SOURCE_DERIVED',entry='stage_phase1_capture_v3.py',bytes=len(new),SHA256=H(new),
        changed_functions=changed,unchanged_functions=sorted(set(old_functions)-set(changed)),added_source_only_helpers=sorted(set(new_functions)-set(old_functions)),
        original_complete_helpers=17,wire_V1_unchanged=True,prepare_preflight_stage_dispatch_executed=False),indent=2))

if __name__=='__main__':main()
