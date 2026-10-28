from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;R=B/'reports'

def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def main():
 manifest=B/'W35_FROZEN_PROFILES_COMPLETE_INPUT_MANIFEST_V1.json';raw=manifest.read_bytes();m=json.loads(raw);changes=[]
 for row in m['files']:
  if row['index_kind'] not in {'new_frozen_evaluation_source'}:continue
  p=Path(row['local_path']);actual=H(p)
  if actual!=row['SHA']:changes.append(dict(relative=row['relative'],old_bytes=row['bytes'],old_SHA=row['SHA'],new_bytes=len(p.read_bytes()),new_SHA=actual));row['bytes']=len(p.read_bytes());row['SHA']=actual
 if changes:
  put(B/'PRESEAL_COMPLETE_INPUT_MANIFEST_BEFORE_ORIGINAL_HEALTH_STOP_REFRESH.json',json.loads(raw));put(R/'PRESEAL_SOURCE_ONLY_EVAL_HASH_REFRESH_ACTUAL.json',dict(epoch=time.time(),changes=changes,no_network_or_model_CPU_or_GPU_before_freeze=True,original_health_observer_stop_retained=True))
  manifest.write_text(json.dumps(m,indent=2),encoding='utf8')
 compiled=[];embedded=[]
 for p in sorted(B.glob('*.py')):
  tree=ast.parse(p.read_bytes());compile(tree,str(p),'exec');compiled.append(p.name)
  if p.name.startswith('install_admit_launch_'):
   values={n.targets[0].id:n.value.value for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)}
   old=json.loads((B/'ORIGINAL_E0_PASSED_OWNER_PRE_CPU_INTERFACE_TEXT_WITNESS.json').read_bytes());assert values['OWNER']==old['OWNER'] and values['PRE']==old['PRE']
   for k in ['OWNER','PRE','RUN']:compile(ast.parse(values[k]),'<embedded '+k+'>','exec');embedded.append(k)
 for row in m['files']:
  if 'not_reread' in row.get('index_kind',''):continue
  p=Path(row['local_path']);assert len(p.read_bytes())==row['bytes'] and H(p)==row['SHA']
 report=dict(epoch=time.time(),passed_source_AST_and_manifest_only=True,compiled=compiled,embedded_AST=embedded,original_E0_actualpass_OWNER_PRE_literal_unchanged=True,input_files=len(m['files']),payload_bytes=sum(r['bytes'] for r in m['files']),input_manifest_SHA=H(manifest),binary_and_model_producer_metadata_only_not_rehashed=True,no_model_SDK_GPU_or_network_run=True,not_skill_acceptance=True)
 put(R/'W35_SOURCE210_MINIMUM_AST_COMPLETE_INPUTS_CPU_ACTUAL.json',report)
 files=[]
 for p in sorted(B.rglob('*')):
  if p.is_file() and p.name!='FROZEN_W35_210_BOUNDED_PROFILE_SOURCE_INDEX_V1.json':files.append(dict(path=str(p),bytes=len(p.read_bytes()),SHA=H(p)))
 entry=B/'install_admit_launch_detached_W35_210_frozen_profiles_UNUSED_once_v1.py';index=dict(epoch=time.time(),status='FROZEN_SOURCE_UNUSED_REMOTE_EVAL',selected_entry=str(entry),entry_SHA=H(entry),complete_manifest_SHA=H(manifest),files=files,actual_GPU_fullrestore_native24_coverage_and_acceptance_pending=True,Git='root ordinary supplement pending')
 put(B/'FROZEN_W35_210_BOUNDED_PROFILE_SOURCE_INDEX_V1.json',index);print(json.dumps({k:index[k] for k in ['status','selected_entry','entry_SHA','complete_manifest_SHA']}))

if __name__=='__main__':main()
