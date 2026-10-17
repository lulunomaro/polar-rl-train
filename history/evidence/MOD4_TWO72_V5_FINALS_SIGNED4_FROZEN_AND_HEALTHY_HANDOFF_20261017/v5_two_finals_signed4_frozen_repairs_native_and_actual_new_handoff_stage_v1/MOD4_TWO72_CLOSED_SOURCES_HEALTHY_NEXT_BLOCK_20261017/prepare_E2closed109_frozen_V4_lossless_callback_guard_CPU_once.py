"""Preserve sealed V3; bind exact new desktop identities and lossless callback witness before GPU."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,sys,time,types,zipfile
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';N=W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017';E=D/'e2_closed109_frozen_prepared_v4';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not E.exists()
signature=json.loads((R/'E2_CLOSED109_249_CHANGED_DESKTOP_EXACT_SIGNATURES_0820_READONLY_ACTUAL.json').read_bytes())
publishers={'gameviewerserver.exe':'NetEase','gameviewer.exe':'NetEase','deepseek harness.exe':'DeepSeek','workbuddy.exe':'Tencent','qq.exe':'Tencent','copilotapp.exe':'Microsoft','copilotapphost.exe':'Microsoft'}
expected={};negatives=[]
for row in signature['exact_new_desktop_roles']:
 name=row['name'];assert row['authenticode']['Status']=='Valid' and publishers[name] in row['authenticode']['Subject']
 assert not any(Path(c['exe'].replace('\\','/')).name.lower().startswith(('python','kit.exe','jupyter')) for c in row['children']+row['parent_children'])
 if name in ('deepseek harness.exe','workbuddy.exe','qq.exe','copilotapp.exe'):assert '--type=gpu-process' in row['process']['argv'] and not any(a.startswith('--type=') for a in row['parent']['argv'])
 if name=='copilotapphost.exe':assert 'connect-to-browser' in row['process']['argv'] and '--browser-owned' in row['process']['argv'] and Path(row['parent']['exe'].replace('\\','/')).name.lower()=='copilotapp.exe'
 expected[name]={k:row[k] for k in ('process','parent','binary_SHA')}
 for field in ('pid','creation','exe','parent','hash','argv'):
  bad=copy.deepcopy(expected[name])
  if field=='hash':bad['binary_SHA']='0'*64
  elif field=='parent':bad['parent']=None if bad['parent'] else {'pid':0}
  elif field=='argv':bad['process']['argv'].append('unexpected-worker.py')
  elif field in ('pid','creation'):bad['process'][field]+=1
  else:bad['process']['exe']='C:/untrusted/worker.exe'
  assert bad!=expected[name];negatives.append(name+':'+field)
assert len(expected)==5
transport=(N/'curb275_final87_frozen3060_v1/transport_249_fresh_signed_desktop_exact_0112_v8.py').read_text('utf8')
transport=transport.replace("Path(__file__).resolve().parent.parent/'reports/ACTUAL_3060_FRESH_EXACT_DESKTOP_ROLE_SIGNATURES_0109_READONLY.json'","Path(__file__).resolve().parent/'reports/E2_CLOSED109_249_CHANGED_DESKTOP_EXACT_SIGNATURES_0820_READONLY_ACTUAL.json'")
assert transport.count('E2_CLOSED109_249_CHANGED_DESKTOP_EXACT_SIGNATURES_0820_READONLY_ACTUAL.json')==1
ast.parse(transport);(D/'transport_249_E2closed109_exact_desktop_0820_v4.py').write_text(transport,encoding='utf8',newline='\n')
E.mkdir();shutil.copytree(D/'e2_closed109_frozen_prepared_v3/payload',Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
p=Q/'retention_native_witness_v8.py';s=p.read_text('utf8');historical=Q/'historical_original_components/V3_retention_native_witness_v8.py';shutil.copy2(p,historical)
s=s.replace('from e2_frozen_prefix_guard_v3 import','from e2_frozen_prefix_guard_v4 import')
old="h=actual_substep_hardware_and_COM(e);check_physics(h);r=e.scene['robot']";assert s.count(old)==1;s=s.replace(old,"h=actual_substep_hardware_and_COM(e);r=e.scene['robot']")
line=next(x for x in s.splitlines() if 'self.sub.append(dict(force=' in x);assert s.count(line)==1;s=s.replace(line,line+'\n   check_physics(h)')
old="e=ChassisPDMod4Env(cfg=cfg);CONTEXT['env']=e;e._retention_native_witness=Witness(e,args);return e";assert s.count(old)==1
new="""e=ChassisPDMod4Env(cfg=cfg);CONTEXT['env']=e
 actual=dict(mimic=float(e.termination_manager.get_term_cfg('mimic').params['threshold']),closure=float(e.termination_manager.get_term_cfg('closure').params['threshold']),physics_dt=float(e.cfg.sim.dt),decimation=int(e.cfg.decimation),episode_seconds=float(e.cfg.episode_length_s),num_envs=int(e.num_envs))
 assert actual['mimic']==.01 and actual['closure']==.002 and actual['physics_dt']==.0025 and actual['decimation']==4 and actual['episode_seconds']>=15 and actual['num_envs']==88
 CONTEXT['actual_eval_integrity_guard']=actual;CONTEXT['save']('ACTUAL_RUNTIME_CONFIG_READBACK.json',dict(declared=CONTEXT['declared_eval_integrity_guard'],actual=actual,no_actor_or_rng_sampling=True))
 e._retention_native_witness=Witness(e,args);return e"""
s=s.replace(old,new);marker="report=dict(case_id=self.args.case_id,";assert s.count(marker)==1;s=s.replace(marker,"report=dict(actual_eval_integrity_guard=CONTEXT['actual_eval_integrity_guard'],declared_eval_integrity_guard=CONTEXT['declared_eval_integrity_guard'],case_id=self.args.case_id,")
ast.parse(s);p.write_text(s,encoding='utf8',newline='\n')
shutil.copy2(D/'e2_frozen_prefix_guard_v3.py',Q/'e2_frozen_prefix_guard_v4.py')
worker=(D/'e2_frozen_worker_v3.py').read_text('utf8').replace('E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V3.json','E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V4.json').replace('E2_CLOSED109_SIGNED4_FROZEN_V3_20261017','E2_CLOSED109_SIGNED4_FROZEN_V4_20261017').replace('e2_frozen_prefix_guard_v3','e2_frozen_prefix_guard_v4');ast.parse(worker);(Q/'e2_frozen_worker_v4.py').write_text(worker,encoding='utf8',newline='\n')
parent=(Q/'e2_frozen_parent_v3.py').read_text('utf8').replace('e2_frozen_worker_v3.py','e2_frozen_worker_v4.py').replace('E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V3.json','E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V4.json').replace("(O/'ORIGINAL_ERROR.json').exists()","any((O/n).exists() for n in ('ORIGINAL_ERROR.json','ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json','APP_CLOSE_ORIGINAL_ERROR.json'))")
ast.parse(parent);(Q/'e2_frozen_parent_v4.py').write_text(parent,encoding='utf8',newline='\n')
# Execute the actual nested callback's statement order with CPU fake sensor/arrays, not a mirror implementation.
tree=ast.parse(s);measured=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='measured');assert ast.unparse(measured).index('self.sub.append')<ast.unparse(measured).index('check_physics(h)')
subset=ast.Module(body=[measured],type_ignores=[]);scope={};ns={}
sys.path.insert(0,str(Q));from e2_frozen_prefix_guard_v4 import check_physics,save_failed_prefix
class Sensor:
 def get_net_contact_forces(self,**kwargs):return self
 def view(self,*a):return np.zeros((1,2,3))
class Robot:
 data=types.SimpleNamespace(body_link_pose_w=np.zeros((1,2,7)),body_com_pose_b=np.zeros((1,2,7)),body_com_vel_w=np.zeros((1,2,6)),body_link_vel_w=np.zeros((1,2,6)))
 def find_bodies(self,*a,**k):return [0,1],None
fake=types.SimpleNamespace(active=True,cap=types.SimpleNamespace(sensor=types.SimpleNamespace(contact_view=Sensor()),dt=.0025),sub=[],rows=[],args=types.SimpleNamespace(steps=120))
ns.update(self=fake,capture=lambda dt:None,e=types.SimpleNamespace(num_envs=1,scene={'robot':Robot()}),wp=types.SimpleNamespace(vec3=object(),to_torch=lambda x:x),actual_substep_hardware_and_COM=lambda e:dict(arrays={'force':np.array([float('nan')])},COM_frame_error_m=0.,mass_weighted_COM_world=np.zeros((1,3))),check_physics=check_physics,cpu=lambda x:x,tensor=lambda x:x,np=np)
exec(compile(subset,'<actual measured callback CPU failure ordering>','exec'),ns)
try:ns['measured'](.0025)
except AssertionError:assert len(fake.sub)==1 and np.isnan(fake.sub[0]['force']).any()
else:raise AssertionError('Actual callback accepted NaN')
fixture=E/'CPU_actual_callback_failure_fixture';fixture.mkdir();saved={};pv=save_failed_prefix(dict(env=types.SimpleNamespace(_retention_native_witness=fake)),fixture,lambda n,v:saved.setdefault(n,v));assert pv['actual_control_rows']==0 and pv['actual_physics_rows']==1
with np.load(pv['raw']['path'],allow_pickle=False) as z:assert np.isnan(z['physical_force']).any()
(fixture/'CPU_ONLY_ORIGINAL_CALLBACK_FAILURE_SCOPE.json').write_text(json.dumps(dict(CPU_fake_arrays_not_robot_or_GPU=True,actual_original_nested_callback_executed=True,prefix=pv),indent=2),encoding='utf8')
oldmanifest=json.loads((Q/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V3.json').read_bytes());rows=[]
for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc'):
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
 rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
mf=Q/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V4.json';manifest={**oldmanifest,'version':4,'files':rows,'package_files_v8':[dict(relative=x['relative'],bytes=x['bytes'],sha256=x['SHA']) for x in rows],'V4_callback_failure_row_preserved_before_guard':True,'actual_config_readback_required':True};mf.write_text(json.dumps(manifest,indent=2),encoding='utf8')
bundle=E/'E2_CLOSED109_COMPLETE_FROZEN_PAYLOAD_V4.zip'
with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for row in rows:z.write(Q/row['relative'],row['relative'])
 z.write(mf,mf.name)
out=dict(epoch=time.time(),passed_complete_payload_CPU_only=True,source=manifest['source'],manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),files=len(rows),worker=dict(path=str(Q/'e2_frozen_worker_v4.py'),SHA=H(Q/'e2_frozen_worker_v4.py')),parent=dict(path=str(Q/'e2_frozen_parent_v4.py'),SHA=H(Q/'e2_frozen_parent_v4.py')),exact_desktop_roles=list(expected),identity_negative_cases=negatives,actual_nested_callback_nonfinite_failure_row_saved_CPU_test=True,CPU_fixture_not_GPU_or_robot=True,sealed_V3_and_resource_identity_rejection_preserved=True,no_target_upload_Task_lease_GPU_or_budget_yet=True)
with (R/'E2_CLOSED109_COMPLETE_FROZEN_V4_CALLBACK_ORDER_ACTUAL_CONFIG_CPU_PREPARED.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(CPU_passed=True,files=len(rows),identity_negatives=len(negatives),actual_callback_bad_row_preserved=True,package_bytes=bundle.stat().st_size,no_GPU=True)))
