"""Read only the new explicit-PD immutable jobs and independent target contracts."""
from pathlib import Path
import json,hashlib,sys,time
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';W='D:/MOD4_async_eval/closure_episode_clock2500_v15';rows=[]
try:
 with n.open_sftp() as nf,w.open_sftp() as wf:
  for label in ('off','on'):
   jid='clk2500-closure-episode-d3-92-d7-pd-sdk-'+label;m=json.loads(nf.open(E+'/eval_queue/'+jid+'.json').read())
   try:raw=nf.open(E+'/eval_results/'+jid+'/result.json').read()
   except FileNotFoundError:rows.append(dict(id=jid,pending=True));continue
   res=json.loads(raw);folder=R/'windows'/jid;folder.mkdir(parents=True,exist_ok=True);files={}
   for name in ('probe.json','result.json'):
    try:raw=nf.open(E+'/eval_results/'+jid+'/'+name).read();original=wf.open(W+'/jobs/'+jid+'/'+name).read()
    except FileNotFoundError:continue
    assert raw==original;(folder/name).write_bytes(raw);files[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),bridge_bytes_exact=True)
   if res['phase']!='complete':
    for name in ('probe.json.error.txt','probe.log'):
     try:raw=wf.open(W+'/jobs/'+jid+'/'+name).read()
     except FileNotFoundError:continue
     (folder/name).write_bytes(raw)
    rows.append(dict(id=jid,result=res,files=files,accepted=False));continue
   assert not res['errors'] and res['new_learning']==False and res['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']=='df0654a6eaf7c62933b869043a340333391f60b44fae184ef0bb458c1f1fc4e5'
   assert res['runtime_archive_sha256']==m['artifacts']['runtime']['sha256'] and res['num_envs']==10 and res['steps']==300
   p=json.loads((folder/'probe.json').read_bytes());proof=p['D7_actual_explicit_PD_SDK']
   assert proof['controls']==300 and proof['actual_contact_callbacks']==1200 and all(x==1200 for x in proof['action_group_callbacks'].values())
   assert proof['actual_audit']['motor_implicit_drive_stiffness_and_damping_zero'] and proof['actual_audit']['no_PhysX_parameter_setter'] and proof['actual_audit']['no_output_gain_or_hardware_envelope_write']
   assert proof['selected_parent_reset']['selected_episode_once'] and proof['isolated_PD_reset']['mass_inertia_COM_implicit_drives_joint_state_spring_gas_exact']
   assert all(proof['CUDA_disk_roundtrip'][k] for k in ('actual_CUDA_factor_episode_three_private_RNG_disk_roundtrip_exact','next_selected_private_draw_exact','same_tick_actor_joint_state_model_coefficients_exact','global_CPU_CUDA_RNG_and_ticks_exact'))
   assert proof['learning_optimizer_updates']==0 and proof['actual_audit']['enabled']==(label=='on')
   rows.append(dict(id=jid,result=res,files=files,proof=proof,accepted=True))
  try:attention=json.loads(wf.open(W+'/SDK_PREPARATION_ISOLATION_WORKER_ATTENTION.json').read())
  except FileNotFoundError:attention=None
 v=dict(epoch=time.time(),rows=rows,current_evaluator_attention=attention,PD_actual_off_on_SDK_scope_accepted=all(r.get('accepted') for r in rows),no_GPU_PPO_canonical_or_launch_write=True)
 (R/'D7_EXPLICIT_PD_ACTUAL_SDK_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 if v['PD_actual_off_on_SDK_scope_accepted']:
  com=json.loads((R/'CENTRAL_D7_ACTUAL_INTERFACE_SCOPE_REVIEW.json').read_text());assert com['COM_actual_off_on_accepted']
  combined=dict(epoch=time.time(),COM_PD_separate_actual_SDK_scope_accepted=True,COM= com,PD=v,combined_closedloop_and_PPO_still_required=True,source_SHA='df0654a6eaf7c62933b869043a340333391f60b44fae184ef0bb458c1f1fc4e5',new_learning=False)
  target=D.parent/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_COM_PD_ACTUAL_SDK_REVIEW.json';target.write_text(json.dumps(combined,indent=2),encoding='utf8')
 print(json.dumps(dict(accepted=v['PD_actual_off_on_SDK_scope_accepted'],attention=attention,rows=[dict(id=r['id'],pending=r.get('pending'),phase=r.get('result',{}).get('phase'),coefficients=r.get('proof',{}).get('actual_audit',{}).get('actual_model_coefficients')) for r in rows])))
finally:w.close();n.close()
