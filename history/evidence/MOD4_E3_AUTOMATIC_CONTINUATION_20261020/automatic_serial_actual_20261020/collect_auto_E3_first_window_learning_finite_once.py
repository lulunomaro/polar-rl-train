"""One bounded read-only connection for actual serial-parent/first-window GO PPO GPU identity."""
from pathlib import Path
import getpass,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';sys.path.insert(0,str(W/'MOD4_AVAILABLE_E2_E3_HOUR18_20261019'));import deploy_available_E2_E3_original_writer_V2_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import sys,json,os,time,psutil,subprocess
B=Path(sys.argv[1]);read=lambda p:json.loads(p.read_bytes());series={p.name:read(p) for p in B.glob('*.json') if p.name.startswith('SERIES_')};current=series.get('SERIES_CURRENT.json',{});active=current.get('active');first=B.parent/'windows/hour0001';active=active or (read(first/'DISPATCH_ACTUAL_NO_TOKEN.json') if (first/'DISPATCH_ACTUAL_NO_TOKEN.json').is_file() else None);owner={};rows={};errors={};CPU={}
if active:
 O=Path(active['owner_root']);N=Path(active['node_root']);owner={p.name:read(p) for p in O.glob('*.json')};paths=[*N.glob('NODE_*.json'),N/'GO_PRODUCTION.json',N/'job0/GO_PRODUCTION.json',N/'job0/production/PPO_POSITIVE_CURRENT.json',N/'job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json',N/'job0/production/latest_complete.json',N/'job0/production/FINAL.json'];rows={p.relative_to(N).as_posix():read(p) for p in paths if p.is_file()};errors={p.relative_to(N).as_posix():read(p) for p in N.glob('job0/production/*ORIGINAL_ERROR*.json')}
if first.is_dir():CPU={p.name:read(p) for p in first.glob('*CPU*ACTUAL.json')}
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','exe','cwd']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B.parent)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),series=series,active=active,owner=owner,rows=rows,errors=errors,source_CPU=CPU,own_processes=own,compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),GPU_snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,utilization.gpu,memory.used,memory.free','--format=csv,noheader,nounits']).decode(),no_PT_or_rawhash_or_canonical_write=True)))
'''
def main():
 dispatch=json.loads((R/'AUTO_E3_SERIAL_SUPERVISOR_DEPLOYED_ACTUAL.json').read_bytes());put('AUTO_E3_FIRST_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,max_wait_seconds=600,actual_alive_only_exclusive_all_training_transport=True));pw=getpass.getpass('72 automatic E3 first actual learning metadata (hidden): ');c=None;begin=time.monotonic();count=0;verified=False
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15)
  while True:
   v=d.a.code(c,d.a.PY,READ,dispatch['root'],timeout=60);count+=1;active=v.get('active') or {};spec=active.get('spec',{});row=v['rows'].get('NODE_CURRENT.json',{}).get('row',{});worker=row.get('worker') or {};ppo=v['rows'].get('job0/production/PPO_POSITIVE_CURRENT.json') or {};go=v['owner'].get('OWNER_CURRENT.json',{}).get('go',{}).get('recovery');parent=v['series'].get('SERIES_IDENTITY.json',{});compute=any(len(t:=x.split(','))>=2 and t[0].strip()==spec.get('GPU_UUID') and t[1].strip()==str(worker.get('pid')) for x in v['compute'].splitlines());ident=any(p['pid']==worker.get('pid') and abs(p['create_time']-worker.get('creation',-1))<.01 and p['cmdline']==worker.get('argv') for p in v['own_processes']);parent_actual=any(p['pid']==parent.get('pid')==dispatch['supervisor']['detached_pid'] and abs(p['create_time']-parent.get('creation',-1))<.01 and p['cmdline'][-1]==dispatch['root']+'/auto_E3_serial_supervisor_v1.py' for p in v['own_processes']);evidence=dict(actual_GO=bool(go and go['source_SHA']==spec.get('source_SHA')==dispatch['source']['SHA'] and go['run_id']==active.get('run_id')),positive_PPO=bool(row.get('phase')=='production' and not v['errors'] and ppo.get('updates',0)>0),matching_UUID_worker_compute=compute,matching_actual_worker_creation_argv=ident,serial_parent_actual_create_argv=parent_actual,worker=worker,GO=go,PPO=ppo,serial_parent=parent);verified=all(evidence[k] for k in ('actual_GO','positive_PPO','matching_UUID_worker_compute','matching_actual_worker_creation_argv','serial_parent_actual_create_argv'))
   with (R/'AUTO_E3_FIRST_METADATA_OBSERVATIONS_JOURNAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(observation=count,actual=v,evidence=evidence))+'\n')
   if verified or v['errors'] or 'SERIES_ORIGINAL_ERROR.json' in v['series'] or 'SERIES_EXIT_ACTUAL.json' in v['series'] or 'NODE_ORIGINAL_ERROR.json' in v['rows'] or 'NODE_EXIT_ACTUAL.json' in v['rows'] or time.monotonic()-begin>=600:break
   time.sleep(15)
  put('AUTO_E3_FIRST_WINDOW_FULL_METADATA_ACTUAL.json',dict(v,metadata_observations=count));put('AUTO_E3_FIRST_WINDOW_GO_PPO_GPU_VERIFIED_OR_PENDING_ACTUAL.json',dict(epoch=time.time(),automatic_E3_first_actual_learning_verified=verified,evidence=evidence,active=active,series_status=v['series'].get('SERIES_CURRENT.json'),actual_finite_transport_returned=True,original_canonical_settled=False,automatic_serial_continuation_authorized=True,no_H1_E2_GO=True,not_whole_model_CPU_or_skill_PASS=True));print(json.dumps(dict(automatic_E3_first_actual_learning_verified=verified,evidence=evidence)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('AUTO_E3_FIRST_METADATA_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_stop_or_canonical_write=True));raise
