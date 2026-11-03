"""SOURCE-only narrow derive from sealed V1. No prepare/stage/main/native call.

Final V2 worker pins come from its owner's frozen final seal receipt.
An unset or floating seal emits no derived entry. Writes stay in this NEW folder.
"""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
R=HERE.parent
OLD=R/'source_phase1_capture_materializer_v1'
V1_ENTRY_PIN=(31219,'0ee747167d7c3389e5e3541c527ac5a4f4244a2a91b08e7733f38e6c8d2fda98')
HELPER_PIN=(10078,'11f43dad3d0f29f0fb1b54995c16d3bf2000586481dda7870dd68af6bc9f50c2')
FINAL_WORKER_SEAL_PIN=(2815,'caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5')
FINAL_WORKER_ROOT_SHA='83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2'
FINAL_WORKER_INDEX_PIN=(65961,'cdb2ca55c08a544cd01e462b7ce27261900f3b6ebaffb4784350717f756b7cf7')
BOOTSTRAP_ORIGINAL_SOURCES={
 'launch_storage_contract':dict(relative='worker_sources/parent/launch_storage_contract.py',
     source_relative='discovery/phase1_first_startup_failure_v1/worker_sources/parent/launch_storage_contract.py',
     bytes=117,SHA256='e40b51db4bca2f322cc2c9b4b0fe011eed292ae605f4f175f268a5bf90326047'),
 'n80_gpu_capacity':dict(relative='worker_sources/parent/n80_gpu_capacity.py',
     source_relative='discovery/phase1_first_startup_failure_v1/worker_sources/parent/n80_gpu_capacity.py',
     bytes=653,SHA256='ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc')}


def need(value,message):
    if not value:raise ValueError(message)


def H(raw):return hashlib.sha256(raw).hexdigest()


def change(text,old,new):
    need(text.count(old)==1,'exact V1 derivation anchor differs: '+old[:100])
    return text.replace(old,new,1)


def put_same(name,raw):
    need(not (HERE/'SOURCE_SEAL.json').exists(),'NEW V2 sealed; do not rewrite')
    path=HERE/name
    if path.exists():need(path.read_bytes()==raw,'existing NEW derivative differs: '+name)
    else:
        with path.open('xb') as stream:stream.write(raw)


def main():
    need(FINAL_WORKER_SEAL_PIN is not None and FINAL_WORKER_ROOT_SHA is not None and FINAL_WORKER_INDEX_PIN is not None,
         'PENDING_FINAL_WORKER_V2_SEAL: no floating PIN accepted; derivative not emitted')
    folder=R/'source_phase1_capture_worker_v2';raw=(folder/'SOURCE_SEAL.json').read_bytes();seal=json.loads(raw)
    need((len(raw),H(raw))==FINAL_WORKER_SEAL_PIN and seal.get('frozen') is True and seal.get('source_only') is True,
         'owner final V2 worker seal differs')
    root=H(json.dumps(seal['files'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
    need(root==seal['content_root_sha256']==FINAL_WORKER_ROOT_SHA and len(seal['files'])==13,'owner complete V2 worker13 root differs')
    for row in seal['files']:
        data=(folder/row['relative']).read_bytes()
        need((len(data),H(data))==(row['bytes'],row['sha256']),'final V2 worker member differs: '+row['relative'])
    data=(folder/'CAPTURE_SOURCE_INDEX.json').read_bytes()
    need((len(data),H(data))==FINAL_WORKER_INDEX_PIN,'owner final V2 source index differs')
    for row in BOOTSTRAP_ORIGINAL_SOURCES.values():
        data=(R/row['source_relative']).read_bytes()
        need((len(data),H(data))==(row['bytes'],row['SHA256']),'actual closed-V1 original helper evidence differs')
        ast.parse(data)
    data=(OLD/'static_source_helpers_v1.py').read_bytes()
    need((len(data),H(data))==HELPER_PIN,'sealed V1 complete17 helper bytes differ')
    put_same('static_source_helpers_v1.py',data)
    raw=(OLD/'stage_phase1_capture_v1.py').read_bytes()
    need((len(raw),H(raw))==V1_ENTRY_PIN,'sealed V1 materializer entry differs')
    text=raw.decode('utf-8')
    text=change(text,"WORKER_FOLDER='source_phase1_capture_worker_v1'","WORKER_FOLDER='source_phase1_capture_worker_v2'")
    text=change(text,"WORKER_SEAL_PIN=(2537,'3f713457c5d66c44ad1fe962ff954e6f65f87afedfef1d6e5bb7fa608e76bea7')",'WORKER_SEAL_PIN='+repr(FINAL_WORKER_SEAL_PIN))
    text=change(text,"WORKER_ROOT_SHA='d792dce3f110fe5fdfe30ded8840da657c22c72eaac42f60093cbe814c095028'",'WORKER_ROOT_SHA='+repr(FINAL_WORKER_ROOT_SHA))
    text=change(text,"WORKER_INDEX_PIN=(57198,'234f8a3d0baf2a84338e9a0bf2170510f99d33c416654bf23b47bc3b5b5aa5ad')",'WORKER_INDEX_PIN='+repr(FINAL_WORKER_INDEX_PIN))
    text=change(text,"COMPLETE_NAME='STAGE_COMPLETE_PHASE1_CAPTURE_V1.json'", "COMPLETE_NAME='STAGE_COMPLETE_PHASE1_CAPTURE_V1.json'\nSOURCE_DERIVATION_VERSION=2\nV1_ENTRY_SHA256="+repr(V1_ENTRY_PIN[1])+"\nBOOTSTRAP_ORIGINAL_SOURCES="+repr(BOOTSTRAP_ORIGINAL_SOURCES))
    text=change(text,"kind='ACTUAL_COMPLETE_TEXT_SOURCE_PIN_VERIFICATION_PHASE1_V1'","kind='ACTUAL_COMPLETE_TEXT_SOURCE_PIN_VERIFICATION_PHASE1_V2',source_derivation_version=2,v1_entry_SHA256=V1_ENTRY_SHA256")
    text=change(text,"need(index.get('kind')=='PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1','NEW source index required')",
        "need(index.get('kind')=='PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1' and index.get('source_version')==2,'final SOURCE V2 with preserved typed index required')")
    text=change(text,'    return dict(sources=sources,index=index,source_root=source_root,',
        """    bootstrap_text_evidence={}
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
    return dict(sources=sources,index=index,source_root=source_root,""")
    text=change(text,'actual_original_C_source_pins=182,source_native_enabled=False,native_executed=False,model_reads=0)',
        'actual_original_C_source_pins=182,bootstrap_original_source_evidence=bootstrap_text_evidence,source_native_enabled=False,native_executed=False,model_reads=0)')
    text=change(text,"kind='SOURCE_PHASE1_CAPTURE_PREFLIGHT_NOT_ADMISSION_V1'","kind='SOURCE_PHASE1_CAPTURE_PREFLIGHT_NOT_ADMISSION_V2'")
    text=change(text,"kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V1'","kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V2'")
    # The old pure-source view omitted the original bootstrap files. They must
    # come from independent original materials, never from a synthetic overlay.
    anchor="""        else:root=Path(actual_root)
        sys.path.insert(0,str(root));sys.dont_write_bytecode=True;builtins.__import__=imported"""
    replacement="""        else:root=Path(actual_root)
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
        sys.path.insert(0,str(root));sys.dont_write_bytecode=True;builtins.__import__=imported"""
    text=change(text,anchor,replacement)
    text=change(text,"'frozen_a1_raw35_v1','pose_cache_runtime_adapter_v3','app_close_semantics_v5','resume_runtime_contracts_v3')",
        "'frozen_a1_raw35_v1','pose_cache_runtime_adapter_v3','app_close_semantics_v5','resume_runtime_contracts_v3',\n        'launch_storage_contract','n80_gpu_capacity')")
    text=change(text,'        for n in watched:sys.modules.pop(n,None)',
        "        for n in watched:\n            if n not in BOOTSTRAP_ORIGINAL_SOURCES:sys.modules.pop(n,None)")
    text=change(text,"        importlib.import_module('phase1_capture_observer');importlib.import_module('worker_passive_interface_v1')",
        """        importlib.import_module('phase1_capture_observer');worker=importlib.import_module('worker_passive_interface_v1')
        bootstrap=worker.bootstrap_original_helpers(root)
        origin=bootstrap['origin_evidence']
        need(origin['source_version']==2 and origin['parent_five_storage_calls']==origin['capacity_ctor_calls']==origin['SDK_constructor_calls']==0,
             'bootstrap import must not call storage/capacity/SDK constructors')
        need({r['relative'] for r in origin['sources']}=={r['relative'] for r in BOOTSTRAP_ORIGINAL_SOURCES.values()},
             'bootstrap actual full source origin set differs')""")
    text=change(text,"kind='REAL_WHOLE_SAFE_CAPTURE_METADATA_IMPORT_CHECK_V1',passed=True", "kind='REAL_WHOLE_SAFE_CAPTURE_METADATA_IMPORT_CHECK_V2',source_derivation_version=2,original_helper_bootstrap=origin,passed=True")
    ast.parse(text)
    old_funcs={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
    new_funcs={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    need(set(old_funcs)==set(new_funcs),'unrelated production function addition/removal')
    changed={name for name in old_funcs if old_funcs[name]!=new_funcs[name]}
    need(changed=={'load_sources','metadata_validate','preflight_summary','stage'},'minimal V1 function whitelist differs: '+str(changed))
    put_same('stage_phase1_capture_v2.py',text.encode())
    print(json.dumps(dict(kind='SOURCE_ONLY_MINIMAL_V2_DERIVED_NOT_PREPARED',entry_bytes=len(text.encode()),entry_SHA256=H(text.encode()),
                         unchanged_complete17_helper_SHA256=HELPER_PIN[1],changed_V1_functions=sorted(changed),worker_root_sha256=FINAL_WORKER_ROOT_SHA)))


if __name__=='__main__':main()
