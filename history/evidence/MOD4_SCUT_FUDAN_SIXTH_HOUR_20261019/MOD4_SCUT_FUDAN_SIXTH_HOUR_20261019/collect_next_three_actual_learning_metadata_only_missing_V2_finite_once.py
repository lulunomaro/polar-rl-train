"""Actual GO/log/compute evidence only; no mid-hour PT or behavioral audit."""
import deploy_three_next_closed_source_hours_once as d
import os,sys,json,time,getpass,traceback
META=r'''
from pathlib import Path
import sys,json,time,psutil,os,subprocess
roots=json.loads(sys.argv[1]);experts={}
for key,root in roots.items():
 B=Path(root);rows={}
 for p in [*B.glob('NODE_*.json'),B/'GO_PRODUCTION.json',B/'job0/GO_PRODUCTION.json',B/'job0/production/PPO_POSITIVE_CURRENT.json',B/'job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json',B/'job0/production/latest_complete.json',B/'job0/production/FINAL.json',B/'job0/production/SCUT_FUDAN_LOADED_REWARD_RECIPE_ACTUAL.json',B/'job0/production/SCUT_FUDAN_JUMP_REWARD_CURRENT.json',*B.glob('NATIVE_ONLY*.json')]:
  if p.is_file():rows[p.relative_to(B).as_posix()]=json.loads(p.read_bytes())
 errors={str(p.relative_to(B)):json.loads(p.read_bytes()) for p in B.glob('job0/production/*ORIGINAL_ERROR*.json')};own=[]
 for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
  try:
   if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
  except psutil.Error:pass
 experts[key]=dict(root=str(B),rows=rows,errors=errors,own_processes=own)
print(json.dumps(dict(epoch=time.time(),experts=experts,compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),GPU_snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,utilization.gpu,memory.used,memory.free','--format=csv,noheader,nounits']).decode(),read_only_no_PT_or_rawhash_or_heavy_audit=True)))
'''
def positive(e):
 row=e['rows'].get('NODE_CURRENT.json',{}).get('row',{});p=e['rows'].get('job0/production/PPO_POSITIVE_CURRENT.json') or {};return row.get('phase')=='production' and not e['errors'] and p.get('updates',0)>0 and bool(row.get('worker'))
def main():
 dispatch=json.loads((d.R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());d.put('THREE_REAL_LEARNING_METADATA_FINITE_COLLECTOR_V2_ONLY_MISSING_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transports=True,same72_connection_max600_metadata_then_one_source210=True,no_mid_hour_model_or_behavior_audit=True));pw=getpass.getpass('72 actual three expert learning metadata only (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);begin=time.monotonic();observations=0;targetroots={k:dispatch['roots'][k] for k in ('h1','recovery')}
  while True:
   target=d.a.code(c,d.a.PY,META,json.dumps(targetroots),timeout=90);observations+=1
   with (d.R/'LEARNING_METADATA_OBSERVATIONS_JOURNAL.txt').open('a',encoding='utf8') as journal:journal.write(json.dumps(dict(reader='V2_only_missing_after_actual10054return',observation=observations,actual=target))+'\n')
   if (all(positive(x) for x in target['experts'].values())) or any(x['errors'] or 'NODE_ORIGINAL_ERROR.json' in x['rows'] or 'NODE_EXIT_ACTUAL.json' in x['rows'] for x in target['experts'].values()) or time.monotonic()-begin>=600:break
   time.sleep(15)
  d.put('THREE_REAL_LEARNING_TARGET72_NATIVE_OR_PRODUCTION_BOUND_METADATA_ACTUAL.json',dict(target,metadata_observations=observations));c.close();c=d.a.t.connect();source=d.a.code(c,d.a.t.PY,META,json.dumps({'e2':dispatch['roots']['e2']}),timeout=90);d.put('THREE_REAL_LEARNING_SOURCE210_METADATA_ACTUAL.json',source);owner=d.a.code(c,d.a.t.PY,"from pathlib import Path;import sys,json,time;B=Path(sys.argv[1]);print(json.dumps(dict(epoch=time.time(),rows={p.name:json.loads(p.read_bytes()) for p in B.glob('*.json') if p.name in ('OWNER_IDENTITY.json','OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json')},readonly=True)))",dispatch['source_root'],timeout=90);d.put('THREE_REAL_LEARNING_ONE_ORIGINAL_OWNER_ACTUAL_CURRENT.json',owner)
  experts={**target['experts'],**source['experts']};evidence={};computes=target['compute']+'\n'+source['compute'];go=owner['rows'].get('OWNER_CURRENT.json',{}).get('go',{})
  for k,e in experts.items():
   row=e['rows'].get('NODE_CURRENT.json',{}).get('row',{});w=row.get('worker') or {};gpu=dispatch['specs'][k]['GPU_UUID'];compute=any(gpu in s and str(w.get('pid','NONE')) in s.split(',') for s in []) if False else any(s.split(',')[0].strip()==gpu and len(s.split(','))>=2 and s.split(',')[1].strip()==str(w.get('pid')) for s in computes.splitlines());evidence[k]=dict(actual_GO=k in go,actual_production_log_positive=positive(e),actual_matching_GPU_worker_compute=compute,worker=w,latest_complete=e['rows'].get('job0/production/PPO_POSITIVE_CURRENT.json'),GO=go.get(k))
  all3=all(x['actual_GO'] and x['actual_production_log_positive'] and x['actual_matching_GPU_worker_compute'] for x in evidence.values());d.put('THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json',dict(epoch=time.time(),three_actual_PPO_learning_verified=all3,experts=evidence,H1_loaded_SCUT_Fudan_recipe=experts['h1']['rows'].get('job0/production/SCUT_FUDAN_LOADED_REWARD_RECIPE_ACTUAL.json'),H1_actual_SCUT_Fudan_public4_rows_readout=experts['h1']['rows'].get('job0/production/SCUT_FUDAN_JUMP_REWARD_CURRENT.json'),current_metadata_not_whole_model_CPU_or_skill_qualification=True,no_heavy_mid_hour_checkpoint_or_behavior_audit=True,no_runtime_stop_or_canonical_write=True,actual_finite_transport_returned=True));print(json.dumps(dict(all_three_actual_learning=all3,experts=evidence)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:d.put('THREE_REAL_LEARNING_FINITE_COLLECTOR_V2_ONLY_MISSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_stop=True));raise
