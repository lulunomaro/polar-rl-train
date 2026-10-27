"""New R5 source namespaces after R4 original precontrol SDK ProxyArray failure."""
from pathlib import Path
import ast,json,hashlib,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
BASE_SHA='677d500672162d9bdc04b417c726b0d61edc839e0396cb3faf15316fbca28067'
PHYSX_SHA='43a31992353ad3a500024d0ec908d5b253ada7a0aac9a1cd2261466e10bda4ff'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def copy(src,dst):
 dst=Path(dst);assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def main():
 q=read(R/'AVAILABLE_TWO_NATIVE87R4_SOURCE_PREPARED_ACTUAL.json');D=N/'payloads_r5';C=N/'controllers_r5';assert not D.exists() and not C.exists()
 A=L/'native87_SDK_tensor_ingress_fix_v1';V=L/'native87_available_two_r5_source'
 # A frozen complete helper is required, never use an active partial source.
 index=read(A/'INDEX.json');assert index['source_only'] is True and index['actual_execution'] is False and index['frozen_UTC']
 for row in index['files']:
  p=A/row['path'];assert p.is_file() and p.stat().st_size==row['bytes'] and H(p)==row['SHA']
 assert read(A/'SOURCE_CPU_ACTUAL.json')['passed'] is True
 assert H(A/'native_wheel_leg_bridge_v4.py')=='46bc32bb6eb5af197b339920b7589426b101c0353695803dc121e2b9819f5bb7'
 assert H(A/'native87_sdk_tensor_ingress_cpu_v1.py')=='b3ad34ec1649f4fbb229fbea093f0fbb43a65e4ae87d9a55ff5ed057432ca9bf'
 for name in ('native_wheel_leg_bridge_v4.py','native87_sdk_tensor_ingress_cpu_v1.py'):assert (A/name).is_file()
 assert read(V/'SOURCE_CPU_ACTUAL.json')['passed'] is True
 additions={'source/native_wheel_leg_bridge_v4.py':A/'native_wheel_leg_bridge_v4.py',
 'source/native87_sdk_tensor_ingress_cpu_v1.py':A/'native87_sdk_tensor_ingress_cpu_v1.py',
 'target_native87_source_sdk_cpu_v1.py':V/'target_native87_source_sdk_cpu_v1.py'}
 for src in additions.values():ast.parse(src.read_bytes())
 cost_report=R/'CURRENT_ACTUAL87R4_GO_BUT_PRECONTROL_PROXYARRAY_FAILURE_CLOSED_ORIGINAL_COST_WORK_ORDER.json';cost=read(cost_report)
 assert cost['closing_remaining_snapshot']==576771.2963469028 and cost['owner_nodes_children_out_and_original_fee_settled'] and cost['sum_once']==145.239182472229
 D.mkdir();C.mkdir()
 for p in (N/'controllers_r4').iterdir():
  if p.is_file():copy(p,C/p.name)
 # Original owner, control, charge, source guard and schedule remain byteexact.
 specs={};payloads={};roots={k:v.replace('2610v87r4/','2610v87r5/') for k,v in q['roots'].items()}
 for key in ('h1','recovery'):
  old=Path(q['payloads'][key]);P=D/key;P.mkdir();m=read(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');old_rows={x['relative']:x for x in m['files']}
  for row in m['files']:
   src=old/row['relative'];assert src.stat().st_size==row['bytes'];copy(src,P/row['relative'])
  changed={}
  for rel,src in additions.items():
   p=P/rel
   if p.exists():copy(p,P/'prebind87R5_exact_history'/(rel+'.original_bytes.txt'));p.write_bytes(src.read_bytes())
   else:copy(src,p)
   changed[rel]=H(p)
  c=read(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json');copy(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json',P/'prebind87R5_exact_history/NATIVE87_SOURCE_CONTRACT_ACTUAL.json.original_bytes.txt')
  c['candidate_pins']=dict(c['candidate_pins'],**changed);c['expected_actual_SDK_base_articulation_data_SHA']=BASE_SHA;c['expected_actual_SDK_physx_articulation_data_SHA']=PHYSX_SHA
  c['approved_python']={p.relative_to(P).as_posix():H(p) for p in P.rglob('*.py')}
  c['source_repair_R5']='Only normalize SDK root/joint/torque read-only torch views before existing typed pack; actual source SHA and real bridge/static/queue CPU required'
  (P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json').write_text(json.dumps(c,indent=2),'utf8')
  t=read(P/'job0/TASK.json');copy(P/'job0/TASK.json',P/'prebind87R5_exact_history/TASK.json.original_bytes.txt')
  t['id']='H1_OWN_FUDAN_NATIVE87R5_'+key;t['native87_contract_SHA']=H(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json');t['expected_actual_SDK_base_articulation_data_SHA']=BASE_SHA;t['expected_actual_SDK_physx_articulation_data_SHA']=PHYSX_SHA;t['actual_SDK_tensor_ingress_CPU_admission_required']=True
  (P/'job0/TASK.json').write_text(json.dumps(t,indent=2),'utf8');changed.update({'NATIVE87_SOURCE_CONTRACT_ACTUAL.json':H(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json'),'job0/TASK.json':H(P/'job0/TASK.json')})
  rows=[]
  for p in sorted(P.rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(P).as_posix()
   if rel in old_rows and rel not in changed:
    row=old_rows[rel];assert row['bytes']==p.stat().st_size;rows.append(row)
   else:rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=H(p)))
   if p.suffix=='.py':ast.parse(p.read_bytes())
  m['files']=rows;m['source_migration_version']='native87R5_actual_SDK_readonly_tensor_ingress';put(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',m)
  specs[key]=dict(q['specs'][key],candidate_pins=c['candidate_pins'],native87_contract_SHA=t['native87_contract_SHA'],manifest_SHA=H(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),expected_actual_SDK_base_articulation_data_SHA=BASE_SHA,expected_actual_SDK_physx_articulation_data_SHA=PHYSX_SHA);payloads[key]=str(P)
  assert H(P/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json')=='14271a0c033e98c88b434513fff7ad614996a94386e4a6fbbd6b926f319fd621' if key=='h1' else True
 new=dict(q,epoch=time.time(),specs=specs,payloads=payloads,roots=roots,controllers_relative='controllers_r5',owner_root=q['owner_root'].replace('2610v87r4/','2610v87r5/'),previous_failed_R4_roots=q['roots'],previous_failed_R4_owner=q['owner_root'],previousR4costreportSHA=H(cost_report),launch_remaining_snapshot=576771.2963469028,sole72_finite_balance_snapshot=576771.2963469028,source_scope='R5 new unused namespaces; R4 failed before native controls, errors and full original fees retained; no same-root rearm',actual_target_CPU_or_GPU_or_GO=False,SDK_tensor_ingress_source_API_probe_required=True,old_model_reread_or_hash_for_Git=False)
 put(R/'AVAILABLE_TWO_NATIVE87R5_SOURCE_PREPARED_ACTUAL.json',new)
 print(json.dumps(dict(passed=True,source_only=True,roots=roots,current_original_balance=576771.2963469028)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('NATIVE87R5_LOCAL_BIND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote_or_GO=True));raise
