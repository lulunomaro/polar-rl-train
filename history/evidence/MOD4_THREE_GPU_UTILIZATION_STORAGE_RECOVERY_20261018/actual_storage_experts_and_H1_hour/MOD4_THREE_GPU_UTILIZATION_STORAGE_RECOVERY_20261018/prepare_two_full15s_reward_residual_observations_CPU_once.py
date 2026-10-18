"""Prepare unused full15s diagnostics after recorded native source/physics CPU review."""
from pathlib import Path
import json,time,hashlib,shutil,zipfile,ast,traceback
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 reports={'E2':R/'E2_LINUX_NATIVE120_RECORDED_PHYSICS_REWARD_CPU_ACTUAL.json','E3':R/'E3_LINUX_NATIVE120_RECORDED_PHYSICS_REWARD_CPU_V2_ACTUAL.json'};payloads=[]
 for kind,rp in reports.items():
  proof=json.loads(rp.read_bytes());assert proof['passed_recorded_native_data_source_physics_CPU'] and proof['actual_parent_children_out_and_private_fcntl_free'];old=B/(kind+'_linux_reward_frame_v4');Q=B/(kind+'_linux_full15s_reward_frame_v1');shutil.copytree(old,Q,ignore=shutil.ignore_patterns('LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json','__pycache__'));m=json.loads((old/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json').read_bytes());worker=Q/'linux_expert_frozen_reward_diagnostic_worker_v1.py';s=worker.read_text('utf8');assert "config['steps']==120" in s and 'steps=120,num_envs=' in s;s=s.replace("config['steps']==120","config['steps']==1500").replace("O=B/'native120_observation'","O=B/'full1500_observation'").replace('steps=120,num_envs=','steps=1500,num_envs=').replace('controls=120,physical_callbacks=480','controls=1500,physical_callbacks=6000');worker.write_text(s,encoding='utf8');parent=Q/'linux_expert_finite_observation_parent_v1.py';parent.write_text(parent.read_text('utf8').replace('native120_observation/','full1500_observation/'),encoding='utf8')
  if kind=='E3':
   p=Q/'e3_native_witness_v1.py';s=p.read_text('utf8');needle="w.phase.update({'E3_'+key:cpu(v) for key,v in e.e3_frame.items()});e.e3_frame=None";assert needle in s;s=s.replace(needle,"w.phase.update({'E3_'+key:cpu(v) for key,v in e.e3_frame.items()});w.phase.update({'E3_phase_'+name:cpu(getattr(e.recovery,name)) for name in ('recipe','age','stable','credited','request','peak')});e.e3_frame=None");p.write_text(s,encoding='utf8')
  rows=[]
  for p in sorted(x for x in Q.rglob('*') if x.is_file()):
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  m.update(version='full15s-v1',steps=1500,files=rows,recorded_native_CPU=dict(path=str(rp),SHA=H(rp),source_SHA=proof['source_SHA']),not_claim_original_missing_internal_counter_fields_were_saved_in_native=True,full_E3_adds_only_readonly_internal_phase_counters=True,no_reward_actor_command_DR_physics_or_threshold_change=True);mp=Q/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json';mp.write_text(json.dumps(m,indent=2));zp=B/(kind+'_linux_full15s_reward_frame_v1.zip')
  with zipfile.ZipFile(zp,'x',compression=zipfile.ZIP_DEFLATED) as z:
   for p in Q.rglob('*'):
    if p.is_file():z.write(p,p.relative_to(Q).as_posix())
  payloads.append(dict(expert=kind,payload=str(Q),manifest_SHA=H(mp),source_SHA=m['source_SHA'],worker_SHA=H(worker),native_CPU_SHA=H(rp),package=dict(path=str(zp),bytes=zp.stat().st_size,SHA=H(zp))))
 with (R/'TWO_FULL15S_NEW_LINUX_REWARD_FRAME_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),payloads=payloads,scope='unused full15s diagnostic on each new Linux backend, not paid PPO or original Windows course qualification',native_recorded_source_and_physics_CPU_passed=True,missing_native_E3_internal_fields_not_fabricated=True,full_E3_passive_counter_readout_added=True,no_reward_STD_LR_command_physics_threshold_change=True,no_target_dispatch_yet=True),f,indent=2)
 print(json.dumps(dict(prepared=[x['expert'] for x in payloads],full_steps=1500,only_new_measurements_no_PPO=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('FULL15S_PAYLOAD_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_target_or_GPU_change=True),f,indent=2)
  raise
