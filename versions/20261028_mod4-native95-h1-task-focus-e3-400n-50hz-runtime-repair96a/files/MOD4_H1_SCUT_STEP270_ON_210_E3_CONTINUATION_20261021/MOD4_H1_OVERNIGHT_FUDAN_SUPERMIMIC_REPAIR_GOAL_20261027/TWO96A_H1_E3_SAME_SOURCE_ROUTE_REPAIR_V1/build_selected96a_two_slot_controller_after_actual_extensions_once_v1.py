"""Seal repaired genuine2slot source from existing actual CPU and input receipts."""
from pathlib import Path
import ast,hashlib,json,shutil,sys,time
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
OLD=L/'THREE95_H1_E3_mixed72_source_v1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
HELPER='''"""Exact actual same-source namespace/asset extension. No model access."""
from pathlib import Path
import hashlib,json
def require(v,m):
 if not v:raise ValueError(m)
def validate_value(x,s):
 require(x.get('passed') is True and x.get('kind')=='MOD4_96A_SAME_SOURCE_NAMESPACE_AND_EXACT_ASSET_ROUTE_EXTENSION_V1','actual source-only extension')
 require(x.get('key')==s['key'] and x.get('new_job')==s['job_root'] and x.get('source_SHA')==s['source_SHA'] and x.get('worker_SHA')==s['worker_SHA'],'new target same model/worker')
 require(x.get('base_actual_fullstate_CPU_SHA')==s['source_CPU_SHA'] and x.get('base_actual_waited_proof_SHA')==s['CPU_waited_proof_SHA'],'original actual wholeCPU and waited pins')
 require(x.get('base_actual_fullstate_CPU_path')==s['CPU_path'] and x.get('base_actual_waited_proof_path')==s['CPU_proof_path'],'original CPU paths not a new decode claim')
 require(x.get('no_new_model_decode_or_Torch_SDK_GPU_import') is True and x.get('original95_failed_resource_only_not_model_source') is True and x.get('actual_GPU_fullrestore_native_and_new_policy_still_pending') is True,'scope and original failure preserved')
 require(x.get('payload_manifest_SHA')==s['payload_manifest_SHA'],'new exact input manifest')
 if s['key']=='h1':require(x.get('source_payload_bytes_unchanged') is True,'native source unchanged')
 else:require(x.get('sole_new_relative')=='runtime/assets/import_contract.json' and x.get('added_source_contract_SHA')==x.get('existing_adjacent_mod4_contract_SHA')=='517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49','one exact missing actual USD-parent dependency')
 return True
def load(s):
 p=Path(s['source_namespace_extension_path']);require(p==Path(s['job_root'])/'SAME_SOURCE_96A_NAMESPACE_ASSET_EXTENSION_ACTUAL.json','exact source extension path')
 raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()==s['source_namespace_extension_SHA'],'actual source extension bytes pin')
 x=json.loads(raw);validate_value(x,s);return x
'''
def wrapper(key):
 loader='load_actual_flat_preinstalled_CPU' if key=='h1' else 'load_E3_preinstalled_CPU'
 return '''
# New resource namespace/source dependency proof, original whole-model CPU unchanged.
_base96_validate_spec=validate_spec
_base96_load='''+loader+'''
_base96_ready=nativeflat_valid_ready
_base96_payload=validate_payload
def validate_spec(s):
 _base96_validate_spec(s)
 require(sha(s.get('source_namespace_extension_SHA')) and s.get('source_namespace_extension_path')==JOB+'/SAME_SOURCE_96A_NAMESPACE_ASSET_EXTENSION_ACTUAL.json','actual new namespace source extension pin')
 return True
def '''+loader+'''(s,B):
 e=_base96_load(s,B)
 from source96a_extension_v1 import load
 e['source_namespace_extension']=load(s);e['source_namespace_extension_SHA']=s['source_namespace_extension_SHA'];return e
def nativeflat_valid_ready(row,s):
 try:
  if not _base96_ready(row,s):return False
  e=row['closed_source_CPU'];require(e.get('source_namespace_extension_SHA')==s['source_namespace_extension_SHA'],'actual extension envelope')
  from source96a_extension_v1 import validate_value
  return validate_value(e['source_namespace_extension'],s)
 except (ValueError,KeyError,TypeError):return False
def validate_payload(s,B):
 _base96_payload(s,B)
 from source96a_extension_v1 import load
 load(s);return True
load_actual_flat_preinstalled_CPU='''+loader+'''
'''+('E3_valid_ready=nativeflat_valid_ready\n' if key=='e3' else '')
def main():
 actual=json.loads((B/'MISSING_ONLY_V2/reports/TWO96A_MISSING_ONLY_EXACT_RAW_EXTENSIONS_RETURNED_ACTUAL_V2.json').read_bytes());assert actual['passed']
 old=json.loads((OLD/'reports/TWO95_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());p=json.loads(json.dumps(old));run='TWO96A_REPAIRED_H1_E3_SAME_SOURCE_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO96A_H1_E3_2610v96a'
 for folder in ('owner','node_h1','node_e3'):shutil.copytree(OLD/folder,B/folder)
 # Preserve original node/owner loops; select repaired signed-alias H1 protocol.
 hsource=(L/'native96_H1_GO_alias_binding_source_v1/h1_next72_protocol_signed_alias96_candidate.py').read_text()
 for key in ('h1','e3'):
  s=p['experts'][key];oldjob=s['job_root'];newjob=oldjob.replace('2610v95','2610v96a');ext=actual['extensions'][key]
  s.update(job_root=newjob,run_id=run,source_namespace_extension_SHA=ext['extension_SHA'],source_namespace_extension_path=ext['extension_path'])
  s['payload_manifest_SHA']=ext['extension']['payload_manifest_SHA']
  if key=='h1':
   s['logical_slot']='h1';s['canonical_worker_key']='h1'
   for name in ('payload_manifest_path','source_contract_path'):s[name]=s[name].replace(oldjob,newjob)
  for folder in ('owner','node_h1','node_e3'):
   directory=B/folder;file=directory/('h1_next72_protocol_actual95_v2.py' if key=='h1' else 'E3_next72_protocol_v1.py')
   if not file.exists():continue
   src=hsource if key=='h1' else file.read_text()
   src=src.replace('JOB='+repr(oldjob),'JOB='+repr(newjob))
   src=src.replace("CPU_PATH=JOB+",'CPU_PATH='+repr(oldjob)+'+').replace("WAITED_PATH=JOB+",'WAITED_PATH='+repr(oldjob)+'+')
   if key=='e3':
    src=src.replace("w.get('job_root')==JOB","w.get('job_root')=="+repr(oldjob))
    src=src.replace(old['experts']['e3']['payload_manifest_SHA'],s['payload_manifest_SHA'])
   file.write_text(src+wrapper(key),encoding='utf8');(directory/'source96a_extension_v1.py').write_text(HELPER,encoding='utf8')
 # Root H1 manifest and E3 manifest filenames are ABI; replace their contents only in this NEW source dir.
 for key in ('h1','e3'):
  directory=B/('node_'+key);name='FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json' if key=='h1' else 'E3_NODE_CONTROLLER_MANIFEST_V1.json';(directory/name).unlink()
  rows=[dict(relative=f.name,bytes=f.stat().st_size,SHA=H(f)) for f in sorted(directory.iterdir()) if f.is_file()]
  spec=p['experts'][key];m=dict(key=key,source_SHA=spec['source_SHA'],worker_SHA=spec['worker_SHA'],files=rows)
  if key=='h1':m['source_CPU_SHA']=spec['source_CPU_SHA']
  put(directory/name,m);spec['manifest_SHA']=H(directory/name)
  p['node_roots'][key]=root+'/node_'+key;p['node_sources'][key]=str(directory)
  p['task_templates'][key].update(run_id=run,worker_SHA=spec['worker_SHA'],source_CPU_SHA=spec['source_CPU_SHA'])
  if key=='h1':p['task_templates'][key].update(logical_slot='h1',canonical_worker_key='h1')
 p['task_templates']['e3']['actual_resource_admission']=None
 owner=B/'owner';oldmf=owner/'TWO95_OWNER_COMPLETE_MANIFEST_V1.json';oldmf.unlink()
 rows=[dict(relative=f.name,bytes=f.stat().st_size,SHA=H(f)) for f in sorted(owner.iterdir()) if f.is_file()]
 put(owner/'TWO96A_OWNER_COMPLETE_MANIFEST_V1.json',dict(run_id=run,keys=['h1','e3'],files=rows))
 p.update(run_id=run,owner_root=root+'/owner',owner_source=str(owner),owner_manifest_SHA=H(owner/'TWO96A_OWNER_COMPLETE_MANIFEST_V1.json'),expected_closed_remaining=539450.9840764999)
 put(B/'reports/TWO96A_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',p)
 # Activation original bytecode constants and loop are retained with only exact report source routing.
 entry=(OLD/'activate_two95_actual_CPU_bound_original_single_writer_once_v1.py').read_text().replace('TWO95','TWO96A')
 (B/'activate_two96a_actual_CPU_bound_original_single_writer_once_v1.py').write_text(entry,encoding='utf8')
 for f in B.rglob('*.py'):ast.parse(f.read_bytes())
 print(json.dumps(dict(passed_source_seal=True,run_id=run,activation_SHA=H(B/'activate_two96a_actual_CPU_bound_original_single_writer_once_v1.py'))))
if __name__=='__main__':main()
