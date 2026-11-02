"""Source-only E1runtime fork from exact424/404. No runtime imports or binary I/O."""
from pathlib import Path
import ast,hashlib,json,difflib,time,traceback
B=Path(__file__).resolve().parent;T=B.parent.parent;H=T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V2';HR=H/'job0/runtime/isaac/mod4';RT='runtime/isaac/mod4/'

def SHA(raw):return hashlib.sha256(raw).hexdigest()
def once(s,a,z,label):
 if s.count(a)!=1:raise ValueError('Exact source anchor '+label+' count='+str(s.count(a)))
 return s.replace(a,z,1)
def add_import(s):
 a=ast.parse(s);last=0
 if a.body and isinstance(a.body[0],ast.Expr) and isinstance(a.body[0].value,ast.Constant) and isinstance(a.body[0].value.value,str):last=a.body[0].end_lineno
 for n in a.body:
  if isinstance(n,ast.ImportFrom) and n.module=='__future__':last=n.end_lineno
 lines=s.splitlines(keepends=True);lines.insert(last,'from e1_pinned_source_v1 import cached_load,cached_H,cached_source_owns,runner_source_load_scope\n');return ''.join(lines)
def cache_adapter(s,rel):
 # AST byte columns applied on UTF8 bytes; preserve original source everywhere else.
 raw=s.encode();lines=raw.splitlines(keepends=True);offset=[0]
 for line in lines:offset.append(offset[-1]+len(line))
 changes=[]
 for n in ast.walk(ast.parse(s)):
  if not isinstance(n,ast.Call):continue
  st=offset[n.lineno-1]+n.col_offset;end=offset[n.end_lineno-1]+n.end_col_offset;old=raw[st:end].decode()
  if isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='torch' and n.func.attr=='load':
   new='cached_load('+old[len('torch.load('):-1]+',purpose='+repr(rel+':'+str(n.lineno))+')';changes.append((st,end,old,new))
  elif isinstance(n.func,ast.Attribute) and n.func.attr=='hexdigest' and isinstance(n.func.value,ast.Call):
   h=n.func.value
   if isinstance(h.func,ast.Attribute) and isinstance(h.func.value,ast.Name) and h.func.value.id=='hashlib' and h.func.attr=='sha256' and len(h.args)==1:
    r=h.args[0]
    if isinstance(r,ast.Call) and isinstance(r.func,ast.Attribute) and r.func.attr=='read_bytes':
     receiver=ast.get_source_segment(s,r.func.value);new='cached_H('+receiver+',purpose='+repr(rel+':source_identity:'+str(n.lineno))+')';changes.append((st,end,old,new))
 for st,en,old,new in sorted(changes,reverse=True):raw=raw[:st]+new.encode()+raw[en:]
 out=raw.decode();out=add_import(out) if changes else out
 reverse=out.replace('from e1_pinned_source_v1 import cached_load,cached_H,cached_source_owns,runner_source_load_scope\n','',1)
 for st,en,old,new in changes:reverse=reverse.replace(new,old,1)
 assert ast.dump(ast.parse(reverse),include_attributes=False)==ast.dump(ast.parse(s),include_attributes=False)
 return out,[dict(original=old,derived=new,line_hint=rel) for _,_,old,new in changes]

def main():
 # Shared mechanism files ONLY, not any H1task/phase/reward/factory replacement.
 hguard=(HR/'mod4v1_fresh_dr_guard.py').read_bytes();oldgashelper=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027\NORMAL_H1_PPO86B_400N50_NEW86_RUNTIME_SOURCE_V1\candidate_payload\job0\runtime\isaac\mod4\gas400_reset_bank_exact_compatibility_v1.py').read_bytes()
 hbank=(HR/'mod4v1_h1_reset_bank_compat.py').read_text(encoding='utf-8');hbank=hbank.replace('require_mod4v1_h1_reset_bank','require_mod4v1_e1_reset_bank').replace('H1_MOD4V1_EXACT_COMPOSED_RESETBANK_COMPATIBILITY_V2','E1_MOD4V1_EXACT_COMPOSED_RESETBANK_COMPATIBILITY_V1').replace('Exact original adjacent H1 bank','Exact original adjacent E1 bank')
 # Original exact helper evidence JSON from H1proven source mechanism, geometry samepinnedasset.
 old400=(HR/'H1_TYPED400_ORIGINAL_IMPORT_CONTRACT_EXACT.json').read_bytes();old700src=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027\NORMAL_H1_PPO86B_400N50_NEW86_RUNTIME_SOURCE_V1\candidate_payload\job0\runtime\isaac\mod4\RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json');old700=old700src.read_bytes()
 fb=(HR/'feedback_delay_runtime.py').read_text(encoding='utf-8');ft=ast.parse(fb);installer=next(n for n in ast.walk(ft) if isinstance(n,ast.FunctionDef) and n.name=='_install_feedback_100hz_sampling');install_method='\n'.join('    '+line for line in ast.get_source_segment(fb,installer).splitlines())+'\n\n'
 # Source-only templates import math/stdlib only until future cache instantiation.
 pure=(B/'e1_four_leaf_migration_v1.template.py').read_bytes();cache=(B/'e1_pinned_source_v1.template.py').read_bytes()
 for name,role,entry,extra in [('CURB141','E1_CURB','train_curb20_direction_resume_ppo.py',['curb20_entry_full_checkpoint.py','curb20_direction_full_checkpoint.py']),('SLOPE135','E1_SLOPE','train_slope5_snapshot_reviewed_resume_ppo.py',['slope5_full_checkpoint.py'])]:
  root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');original={};derived={};changes=[];proofs=[]
  def get(rel):
   if rel not in original:original[rel]=(root/rel).read_bytes()
   return original[rel].decode('utf-8-sig')
  def put(rel,text,why):
   raw=text.encode() if isinstance(text,str) else text
   if rel.endswith('.py'):compile(ast.parse(raw),rel,'exec')
   derived[rel]=raw;changes.append(dict(relative=rel,reason=why,old_SHA=SHA(original[rel]) if rel in original else None,new_SHA=SHA(raw)))
  for rel in ['runtime/physics_clock.py','runtime/physics_clock2000.py',RT+'physics_clock.py']:
   s=get(rel)
   for a,z in [('control_s=.01','control_s=.02'),('control_s-.01','control_s-.02'),('decimation=10000//us','decimation=20000//us'),('decimation*us!=10000','decimation*us!=20000'),('policy_hz=100.','policy_hz=50.')]:s=once(s,a,z,rel+':'+a)
   put(rel,s,'Only policyperiod20ms/50Hz; physics2.5ms and5ms bin fragments unchanged')
  # Delivery fixedSI contract: only policyHz changes; no export reorder/motor/scale.
  rel='runtime/train/deploy/contract_rm2025_later.json';raw=get(rel);delivery=json.loads(raw);assert delivery['policy_hz']==100;delivery['policy_hz']=50;put(rel,json.dumps(delivery,indent=2)+'\n','Only delivery policy_hz100->50, fixedSI/export mapping allsame')
  rel=RT+'action_delay_physics_queue.py';s=get(rel)
  for a,z in [('control_us=10000','control_us=20000'),('control_us==10000','control_us==20000'),("state['control_us']==10000","state['control_us']==20000"),('control_period_us=10000','control_period_us=20000')]:s=once(s,a,z,rel+':'+a)
  put(rel,s,'Only20ms command period; physicalticks and0/2500/5000us due/issue/history logic unchanged')
  rel=RT+'action_delay_sdk_adapter.py';s=get(rel);s=once(s,'env.step_dt==.01 and env.cfg.decimation==4','env.step_dt==.02 and env.cfg.decimation==8','actionSDKclock');put(rel,s,'8physicalcallbacks/50Hz; no target/action physics changes')
  rel=RT+'feedback_delay_runtime.py';s=get(rel);s=once(s,'tick = env.common_step_counter',"tick = getattr(env, '_feedback_100hz_tick', env.common_step_counter)",'feedbackactual100tick');s=once(s,'        super().__init__(**kwargs)',"        self._feedback_100hz_tick = 0\n        super().__init__(**kwargs)\n        self._install_feedback_100hz_sampling()",'install_feedback_once');s=once(s,'    def clean_policy(self):',install_method+'    def clean_policy(self):','feedback_sampler_method');s=once(s,'tick = int(self.common_step_counter)',"tick = int(getattr(self, '_feedback_100hz_tick', self.common_step_counter))",'feedbackaudit_tick');put(rel,s,'Original recipe/history0/10000us unchanged; proven 4phys samplinghook yields100Hz independently of50Hz policy')
  for filename,a,z in [('spring_pressure_index_runtime.py','self.nominal=torch.tensor([3500.,3500.]','self.nominal=torch.tensor([2000.,2000.]'),('spring_pressure_audit_runtime.py','(nominal==3500)','(nominal==2000)'),('spring_nominal_sdk_readback.py',"(values['physx_stiffness_N_m']==3500)","(values['physx_stiffness_N_m']==2000)")]:
   rel=RT+filename;s=get(rel);s=once(s,a,z,filename+'nominal');put(rel,s,'New2000N/m nominal only; original factors/streams/PD/damping3/forcecap2000 retained')
  rel=RT+'spring_pressure_training_env.py';s=get(rel);s=once(s,'nominal_stiffness_N_m=3500','nominal_stiffness_N_m=2000','D5recipe nominal');s=once(s,'actual_stiffness_bounds_N_m=[3150,3850]','actual_stiffness_bounds_N_m=[1800,2200]','D5recipe bounds');put(rel,s,'Recipe matches exactfourleaf migration')
  for file in ['clock_training_health.py','e1_terrain_training_health.py']:
   rel=RT+file;s=get(rel);s=s.replace('round(.01/self.env.physics_dt)','int(self.env.cfg.decimation)').replace('round(.01/env.physics_dt)','int(env.cfg.decimation)');s=s.replace('closure_2mm_still_resets_only_this_environment=True','closure_10mm_resets_only_this_environment=True');s=s.replace('ordinary_task_thresholds_unchanged=True','ordinary_task_thresholds_except_new10mm_closure_unchanged=True');put(rel,s,'Actualdecimation forclockreport/check; originallegacy2mm diagnostic remains separately named; closureonlynewcfg10mm')
  # Exact full-state chain adapters; reverse adapters AST-proved equal to each original.
  helpers=['sensor_resume_contract.py','feedback_delay_checkpoint.py','action_delay_checkpoint.py','spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py','sensor_a0_runtime.py']+extra
  for filename in helpers:
   rel=RT+filename;old=get(rel);s,sites=cache_adapter(old,rel);put(rel,s,'All logical originalsource reads/hashes share one future cache; ownnew diskroundtrips real I/O');proofs.append(dict(relative=rel,reverse_adapter_AST_exact=True,purpose_sites=sites))
  # Full original E1entry stays ownfactory/reward/phase. Only timing/sourceroute wrapper changes.
  rel=RT+entry;s=get(rel);s=once(s,'gamma=0.99','gamma=0.9801','physicaltime gamma50Hz');s=once(s,'lam=0.95','lam=0.9025','physicaltime GAE50Hz');s=once(s,'        runner.load(warm)','        with runner_source_load_scope():\n            runner.load(warm)','runnercachedsource');s=once(s,'    def _sha256(path):\n        import hashlib','    def _sha256(path):\n        if cached_source_owns(path):return cached_H(path,purpose="E1.run_manifest.original_selected_source_SHA")\n        import hashlib','entrysourceSHA');s=add_import(s);put(rel,s,'OriginalE1entry ownfactory;50Hz equivalent physical discount, sourceonlyrouting no STDreset')
  for filename,raw in [('e1_four_leaf_migration_v1.py',pure),('e1_pinned_source_v1.py',cache),('mod4v1_fresh_dr_guard.py',hguard),('gas400_reset_bank_exact_compatibility_v1.py',oldgashelper),('mod4v1_e1_reset_bank_compat.py',hbank.encode()),('H1_TYPED400_ORIGINAL_IMPORT_CONTRACT_EXACT.json',old400),('RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json',old700)]:put(RT+filename,raw,'Puremigration/sharedguard/exactbankcompat mechanism, not H1task substitute')
  # Exact originalflat133 check -> explicit composed identity, unchangedq/selection/writes.
  rel=RT+'scut_flat_rescue.py';s=get(rel);s=once(s,"        if actual!=raw['contract_sha256']:raise RuntimeError('reset-bank contract hash mismatch')","        if actual!=raw['contract_sha256']:\n            from mod4v1_e1_reset_bank_compat import require_mod4v1_e1_reset_bank\n            env._mod4v1_e1_flat_bank_compatibility=require_mod4v1_e1_reset_bank(source,task.MOD4_ISAAC/'import_contract.json',raw,actual_contract_SHA=actual)",'flatbankidentity');put(rel,s,'Exact700->517->bae identitycomposition; original133/height74/randomselector/q/root resetwrites unchanged')
  # Do not write ANY derived runtime until all anchors and compilation pass.
  allrows=[]
  for rel,raw in derived.items():
   p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row=dict(relative=rel,bytes=len(raw),SHA=SHA(raw))
   if rel.endswith('.py'):row['AST_SHA']=SHA(ast.dump(ast.parse(raw),include_attributes=False).encode())
   allrows.append(row)
  for file,value in [('E1_RUNTIME_DERIVATION_INPUTS_AND_CHANGES_V1.json',dict(kind='SOURCE_ONLY_NOT_ACTUAL_SDK',role=role,entry=entry,changes=changes,original_input_SHA=[dict(relative=k,SHA=SHA(v),bytes=len(v)) for k,v in original.items()],shared_mechanism_sources=dict(H1_guard_SHA=SHA(hguard),H1_bank_adapter_source=str(HR/'mod4v1_h1_reset_bank_compat.py')),outputs=allrows,PT_SDK_GPU_SSH_operations=0)),('E1_FULLSTATE_REVERSE_CACHE_ADAPTER_AST_PROOF_V1.json',dict(kind='SOURCE_AST_ONLY_NOT_TARGETPASS',role=role,checks=proofs,full_original_restore_one_sensor_reset_retained=True,no_unknown_extra_state_removed=True))]:
   with (root/file).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)
  patch=''
  for rel,old in original.items():
   if rel in derived and old!=derived[rel]:patch+=''.join(difflib.unified_diff(old.decode('utf-8-sig').splitlines(keepends=True),derived[rel].decode().splitlines(keepends=True),fromfile='original/'+rel,tofile='derived/'+rel))
  with (root/'E1_RUNTIME_MINIMAL_DIFF_V1.patch').open('x',encoding='utf-8') as f:f.write(patch)
  print(name,'derived source-only',len(derived),'files,',len(helpers),'reverse-cache ASTproofs; remaining roughbank/worker interface staged separately')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('E1_RUNTIME_GENERATOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_SSH_GPU_operations=0),f,indent=2)
  raise
