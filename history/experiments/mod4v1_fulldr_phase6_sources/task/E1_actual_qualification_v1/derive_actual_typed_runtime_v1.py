"""New ACTUAL runtime fork after CPUactual pass; original sourcefinal immutable.
Typed-input cache MUST NOT rerun fourleaf migration. No PT/SDK/model calls here.
"""
from pathlib import Path
import argparse,ast,hashlib,json,difflib,time,traceback
B=Path(__file__).resolve().parent;T=B.parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--canonical',choices=['CURB141','SLOPE135'],required=True);a=p.parse_args();name=a.canonical
 cpu=B/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json');cr=cpu.read_bytes();c=json.loads(cr);assert c['passed'] and c['counts']['original_CPUdecodes']==1
 source=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');root=B/(name+'_ACTUAL_TYPED_SOURCE_V1');root.mkdir(exist_ok=False);inputs=[]
 for path in source.rglob('*'):
  if path.suffix.lower() in ('.pt','.npz','.usd','.zip','.onnx','.safetensors'):continue
  if not path.is_file():continue
  rel=path.relative_to(source);raw=path.read_bytes();dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as f:f.write(raw)
  inputs.append(dict(relative=str(rel),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 rt=root/'runtime/isaac/mod4';changes=[]
 def alter(p,new,why):
  old=p.read_bytes();compile(new,str(p),'exec')
  p.write_text(new,encoding='utf-8',newline='');changes.append(dict(relative=str(p.relative_to(root)),old_SHA=hashlib.sha256(old).hexdigest(),new_SHA=hashlib.sha256(new.encode()).hexdigest(),reason=why))
 def once(s,old,new):
  assert s.count(old)==1,old;return s.replace(old,new,1)
 p=rt/'e1_pinned_source_v1.py';s=p.read_text(encoding='utf-8');s=once(s,'expected_bytes,*,role):','expected_bytes,*,role,original_source_SHA,CPU_receipt_SHA):');s=once(s,'self.original_load=torch.load;self.role=role','self.original_load=torch.load;self.role=role;self.original_source_SHA=original_source_SHA;self.CPU_receipt_SHA=CPU_receipt_SHA')
 s=once(s,"self.original_state=self.original_load(io.BytesIO(self.raw),map_location='cpu',weights_only=False);self.source_decodes+=1\n  self.state,self.migration_receipt=migrate_complete_source(self.original_state,role=role)","self.state=self.original_load(io.BytesIO(self.raw),map_location='cpu',weights_only=False);self.source_decodes+=1\n  from e1_four_leaf_migration_v1 import FOUR_PATHS,NEW_VALUES,leaf\n  if not all(leaf(self.state,p)==v for p,v in zip(FOUR_PATHS,NEW_VALUES)):raise ValueError('Alreadytyped40050 completeinput required; no retyping')\n  if self.state['independent_terrain_expert']!=role or self.state['spring_pressure_state']['n']!=20000 or self.state['feedback_delay_recipe']['control_period_us']!=10000:raise ValueError('ExacttypedE1role/20k/100Hzfeedback required')\n  self.migration_receipt=dict(kind='ALREADY_TYPED_COMPLETE_NO_RETYPE',original_source_SHA=original_source_SHA,actual_CPU_receipt_SHA=CPU_receipt_SHA,typed_source_SHA=self.SHA,original_four_leaf_inverse_actual_proof_is_external=True,migration_calls_in_SDK=0,checkpoint_metadata_keys_added=0)")
 s=once(s,'original_source_SHA=self.SHA,source_bytes=','original_source_SHA=self.original_source_SHA,source_SHA=self.SHA,source_bytes=');s=s.replace('original_complete_pytree_unmodified=True','selected_typed_complete_pytree_unmodified=True');alter(p,s,'Alreadytypedselected input; onecacheload, zero retype; externalactualCPUproof binding')
 # Shared boot isolation mechanism only; true E1 factory unchanged.
 launcher='''from pathlib import Path
import os
from isaaclab.app import AppLauncher
class E1IsolatedAppLauncher(AppLauncher):
 def _create_app(self):
  job=Path(os.environ['MOD4V1_E1_ACTUAL_JOB_ROOT']).resolve();root=Path(os.environ['MOD4V1_E1_KIT_STORAGE_ROOT']).resolve()
  if root!=job/'kit_isolation' or not root.is_dir():raise ValueError('New ownE1 Kitstorage required')
  self._sim_app_config['enable_crashreporter']=False
  self._sim_app_config['extra_args']=['--/crashreporter/preserveDump=true','--/crashreporter/enabled=false','--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false','--portable-root',str(root),'--/app/userConfigPath='+str(root/'data/user.config.json'),'--/UJITSO/datastore/localCachePath='+str(root/'DerivedDataCache')]
  super()._create_app()
'''
 with (rt/'launcher_mod4v1_e1_actual.py').open('x',encoding='utf-8') as f:f.write(launcher)
 meta=json.loads((root/'E1_CANONICAL_SOURCE_METADATA.json').read_bytes());p=rt/meta['entry'];s=p.read_text(encoding='utf-8');s=once(s,'from isaaclab.app import AppLauncher  # noqa: E402','from launcher_mod4v1_e1_actual import E1IsolatedAppLauncher as AppLauncher  # noqa: E402');alter(p,s,'Only proven bootstorage isolation; E1factory/reward/phase unchanged')
 oldworker=(source/'prepared_e1_native24_noupdate_worker_v1.py').read_text(encoding='utf-8');s=oldworker;s=once(s,'import argparse,copy,importlib,json,os,runpy,sys,time,traceback','import argparse,copy,hashlib,importlib,json,os,runpy,sys,time,traceback')
 s=once(s,"assert task['canonical']==meta['canonical'] and task['source_SHA']==meta['original_source_SHA'] and task['source_read_purpose']","CPUraw=(root/'CPU_FOUR_LEAF_ACTUAL_COMPLETE.json').read_bytes();CPU=json.loads(CPUraw);assert CPU['passed'] and CPU['canonical']==meta['canonical']\n assert task['canonical']==meta['canonical'] and task['original_source_SHA']==meta['original_source_SHA']==CPU['original_source']['SHA'] and task['source_SHA']==CPU['new_typed_source']['SHA'] and task['source_read_purpose']")
 s=s.replace("task['selected_original_source_path']","task['selected_typed_source_path']")
 s=once(s,"sys.path[:0]=[str(mod),str(root/'runtime'),str(root/'lib')]","sys.path[:0]=[str(mod),str(root/'runtime'),str(root/'lib')]\n os.environ.update(MOD4V1_E1_ACTUAL_JOB_ROOT=str(root),MOD4V1_E1_KIT_STORAGE_ROOT=str(root/'kit_isolation'))\n storage=root/'kit_isolation';storage.mkdir();(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')")
 s=once(s,"role=meta['role'])","role=meta['role'],original_source_SHA=task['original_source_SHA'],CPU_receipt_SHA=hashlib.sha256(CPUraw).hexdigest())")
 anchor="   before=core();audit_before=env._mild_dr.audit();assert audit_before['actual_parameters_pass']"
 extra='''   def core_digest(value):
    leaves=[]
    def walk(v,path=''):
     if torch.is_tensor(v):
      x=v.detach().cpu().contiguous();leaves.append(dict(path=path,dtype=str(x.dtype),shape=list(x.shape),SHA=hashlib.sha256(x.numpy().tobytes()).hexdigest()))
     elif isinstance(v,dict):
      for k in sorted(v,key=str):walk(v[k],path+'/'+str(k))
     elif isinstance(v,(tuple,list)):
      for i,x in enumerate(v):walk(x,path+'/'+str(i))
     else:leaves.append(dict(path=path,value=v))
    walk(value);return dict(tree_SHA=hashlib.sha256(json.dumps(leaves,sort_keys=True).encode()).hexdigest(),leaves=leaves)
'''
 s=once(s,anchor,extra+anchor+"\n   core_before_digest=core_digest(before);put('E1_CORE_BEFORE.json',dict(core=core_before_digest,forbidden_calls=forbidden,source_cache=cache.receipt()))")
 s=once(s,"   counts=cache.receipt();assert", "   core_after_digest=core_digest(core());assert core_after_digest==core_before_digest;put('E1_CORE_AFTER.json',dict(core=core_after_digest,core_before_after_exact=True,forbidden_calls=forbidden,source_cache=cache.receipt()))\n   counts=cache.receipt();assert")
 def loop(v):
  nodes=[n for n in ast.walk(ast.parse(v)) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range' and any(isinstance(a,ast.Constant) and a.value==24 for a in n.iter.args)];assert len(nodes)==1;return ast.dump(nodes[0],include_attributes=False)
 assert loop(oldworker)==loop(s);compile(s,'actualE1native24','exec')
 with (root/'worker_n20k_typed_noupdate.py').open('x',encoding='utf-8') as f:f.write(s)
 fresh=(B/'e1_fresh80_actual_worker_v1.template.py').read_bytes();compile(fresh,'fresh80E1','exec')
 with (root/'worker_fresh80_noPT.py').open('xb') as f:f.write(fresh)
 with (root/'CPU_FOUR_LEAF_ACTUAL_COMPLETE.json').open('xb') as f:f.write(cr)
 interface=[]
 for filename in ['worker_fresh80_noPT.py','worker_n20k_typed_noupdate.py']:
  tree=ast.parse((root/filename).read_bytes());names=sorted({n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='put' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str)})
  interface.append(dict(worker=filename,rows=[dict(worker_put=n,parent_expected_read='gpu1/out/'+n,collector_expected_read='gpu1/out/'+n,basename_equal=True) for n in names]))
 with (root/'ACTUAL_BASENAME_INTERFACE_TABLE_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='EXACT_FULL_FILENAME_INTERFACE_BEFORE_DISPATCH',canonical=name,interfaces=interface,all_basenames_equal=True,no_global_role_substring_replace=True),f,indent=2)
 with (root/'ACTUAL_TYPED_RUNTIME_DERIVATION_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='NEW_ACTUAL_RUNTIME_NOT_OLD_SOURCEFINAL_HOTPATCH',canonical=name,upstream_sourcefinal=str(source/'FINAL_SOURCE_INDEX.json'),upstream_SHA=hashlib.sha256((source/'FINAL_SOURCE_INDEX.json').read_bytes()).hexdigest(),CPU_actual_receipt_path=str(cpu),CPU_actual_receipt_SHA=hashlib.sha256(cr).hexdigest(),original_input_rows=inputs,changes=changes,native24_for_AST_exact=True,native24_AST_SHA=hashlib.sha256(loop(s).encode()).hexdigest(),typed_only_SDK_migration_calls=0,PT_SDK_operations_in_builder=0),f,indent=2)
 print(json.dumps(dict(actual_source_root=str(root),canonical=name,typed_source=c['new_typed_source'],original_sourcefinal_unmodified=True,for24AST_exact=True,PT_SDK_operations=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('ACTUAL_TYPED_DERIVATION_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
  raise
