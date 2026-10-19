"""Only missing terminal H1 evidence and healthy E3 PPO; no task/worker retry."""
from pathlib import Path
import base64,getpass,hashlib,json,os,sys,time,traceback
import deploy_three_next_closed_source_hours_once as d
import collect_next_three_actual_learning_metadata_finite_once as m
B=d.B;R=d.R
H1=r'''
from pathlib import Path
import base64,hashlib,json,os,psutil,sys,time,fcntl
B=Path(sys.argv[1]);assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());p=B/'job0/production_WORKER.log';own=[]
for v in psutil.process_iter(['pid','cmdline','create_time']):
 try:
  if v.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in v.info['cmdline'] or []):own.append(v.info)
 except psutil.Error:pass
t=json.loads((B/'NODE_TERMINAL_ACTUAL.json').read_bytes());e=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());assert not own and t['row']['original_error'] and t['row']['phase']=='production' and t['row']['terminal_all_own_children_waited'] and e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'];assert not (B/'job0/production/PPO_POSITIVE_CURRENT.json').exists() and not (B/'job0/production/FINAL.json').exists();data=None
if p.is_file():
 assert not p.is_symlink() and p.stat().st_size<20_000_000;data=p.read_bytes()
print(json.dumps(dict(epoch=time.time(),root=str(B),terminal=t,actual_exit=e,actual_own_processes=own,production_files=[dict(path=str(x),bytes=x.stat().st_size) for x in (B/'job0/production').iterdir() if x.is_file()],worker_log=None if data is None else dict(path=str(p),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),exact_bytes_base64=base64.b64encode(data).decode()),no_mid_hour_PT_or_rawhash_or_GPU_replay=True)))
'''
def main():
 assert not (R/'H1_TERMINAL_AND_MISSING_E3_PPO_V2_READER_STARTED_ACTUAL.json').exists()
 first=json.loads((R/'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes());assert not first['three_actual_PPO_learning_verified'] and first['actual_finite_transport_returned']
 v=json.loads((R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());assert v['owner']['detached_pid']==413504
 d.put('H1_TERMINAL_AND_MISSING_E3_PPO_V2_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transport=True,only_missing_H1_terminal_log_and_E3_PPO_no_worker_retry=True))
 pw=getpass.getpass('72 terminal H1 evidence and missing E3 PPO only (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);h=d.a.code(c,d.a.PY,H1,v['roots']['h1'],timeout=90);log=h.get('worker_log')
  if log:
   raw=base64.b64decode(log.pop('exact_bytes_base64'));assert len(raw)==log['bytes'] and hashlib.sha256(raw).hexdigest()==log['SHA'];p=R/'H1_FAILED_ENV_INITIALIZATION_WORKER_EXACT_LOG.txt'
   with p.open('xb') as stream:stream.write(raw)
   log['local_exact_path']=str(p)
  d.put('H1_POST_GO_ENV_INITIALIZATION_FAILURE_TERMINAL_AND_LOG_ACTUAL.json',h);start=time.monotonic();observations=0
  while True:
   target=d.a.code(c,d.a.PY,m.META,json.dumps({'recovery':v['roots']['recovery']}),timeout=90);observations+=1;e=target['experts']['recovery']
   with (R/'MISSING_E3_PPO_V2_OBSERVATIONS_JOURNAL.txt').open('a',encoding='utf8') as stream:stream.write(json.dumps(dict(observation=observations,actual=target))+'\n')
   if m.positive(e) or e['errors'] or 'NODE_ORIGINAL_ERROR.json' in e['rows'] or 'NODE_EXIT_ACTUAL.json' in e['rows'] or time.monotonic()-start>=600:break
   time.sleep(15)
  d.put('MISSING_E3_PPO_V2_TARGET72_METADATA_ACTUAL.json',dict(target,metadata_observations=observations,max_wait_seconds=600));c.close();c=d.a.t.connect();source=d.a.code(c,d.a.t.PY,m.META,json.dumps({'e2':v['roots']['e2']}),timeout=90);d.put('TWO_HEALTHY_PPO_V2_SOURCE210_METADATA_ACTUAL.json',source);owner=d.a.code(c,d.a.t.PY,"from pathlib import Path;import sys,json,time;B=Path(sys.argv[1]);print(json.dumps(dict(epoch=time.time(),rows={p.name:json.loads(p.read_bytes()) for p in B.glob('*.json') if p.name in ('OWNER_IDENTITY.json','OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json')},readonly=True)))",v['source_root'],timeout=90);d.put('PARTIAL_SEVENTEENTH_ORIGINAL_OWNER_V2_ACTUAL_CURRENT.json',owner)
  experts={**target['experts'],**source['experts']};compute=target['compute']+'\n'+source['compute'];go=owner['rows'].get('OWNER_CURRENT.json',{}).get('go',{});evidence={}
  for k,e in experts.items():
   row=e['rows'].get('NODE_CURRENT.json',{}).get('row',{});worker=row.get('worker') or {};uuid=v['specs'][k]['GPU_UUID'];matched=any(len(x.split(','))>=2 and x.split(',')[0].strip()==uuid and x.split(',')[1].strip()==str(worker.get('pid')) for x in compute.splitlines());evidence[k]=dict(actual_GO=k in go,actual_production_log_positive=m.positive(e),actual_matching_GPU_worker_compute=matched,worker=worker,GO=go.get(k),latest_complete=e['rows'].get('job0/production/PPO_POSITIVE_CURRENT.json'))
  good=all(x['actual_GO'] and x['actual_production_log_positive'] and x['actual_matching_GPU_worker_compute'] for x in evidence.values());d.put('TWO_HEALTHY_PPO_AND_H1_POST_GO_ALLOCATION_FAILURE_V2_ACTUAL.json',dict(epoch=time.time(),two_actual_PPO_learning_verified=good,experts=evidence,H1_actual_GO=go.get('h1'),H1_production_updates0_no_new_FINAL=True,H1_terminal_all_own_children_waited=True,H1_failure_report=str(R/'H1_POST_GO_ENV_INITIALIZATION_FAILURE_TERMINAL_AND_LOG_ACTUAL.json'),H1_charge_not_zero_by_assumption_wait_original_owner_settlement=True,all_three_learning=False,current_metadata_not_whole_model_or_skill_PASS=True,no_stop_hotpatch_or_canonical_write=True,actual_finite_transport_returned=True));print(json.dumps(dict(two_actual_PPO=good,experts=evidence,H1_failed_after_GO_before_PPO=True)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:d.put('H1_TERMINAL_MISSING_E3_PPO_V2_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_Task_or_worker_replay=True));raise
