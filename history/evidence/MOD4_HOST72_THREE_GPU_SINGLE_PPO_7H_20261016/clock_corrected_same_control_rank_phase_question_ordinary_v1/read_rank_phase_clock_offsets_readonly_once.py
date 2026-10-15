"""Bounded existing rank-log/phase read with clock-offset intervals; no profiling injection."""
from pathlib import Path
import getpass,hashlib,json,re,shlex,sys,time,paramiko
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import json,re,sys,time
B=Path(sys.argv[1]);rows=[]
for p in sorted(B.glob('rank*/logs/*/CLOCK_TRAINING_HEALTH.json')):
 x=json.loads(p.read_bytes());rank=int(p.parts[-4][4:]);log=B/('rank'+str(rank))/'train_worker.log';tail=''
 if log.exists():
  with log.open('rb') as f:f.seek(max(0,log.stat().st_size-30000));tail=f.read().decode(errors='replace')
 tail=re.sub(r'\x1b\[[0-9;]*m','',tail);metrics=[]
 for m in re.finditer(r'Learning iteration\s+(\d+)\s*/\s*(\d+).*?(?=Learning iteration|\Z)',tail,re.S):
  row=dict(iteration=int(m.group(1)))
  for k,pat in [('collection',r'Collection time:\s*([\d.]+)s'),('learning',r'Learning time:\s*([\d.]+)s'),('total',r'Iteration time:\s*([\d.]+)s')]:
   q=re.search(pat,m.group(0))
   if q:row[k]=float(q.group(1))
  if len(row)==4:metrics.append(row)
 rows.append(dict(rank=rank,health_epoch=x['epoch'],controls=x['control_steps'],callbacks=x['actual_physics_callbacks'],ordinary=x['ordinary_episode_reset_events'],integrity=x['integrity_task_reset_events'],unknown=x['unknown_task_reset_events'],nonfinite=x['nonfinite_observed'],STOP=x['stop_reason'],existing_log_metrics=metrics[-6:],log_bytes=log.stat().st_size if log.exists() else None))
print(json.dumps(dict(epoch=time.time(),rows=rows)))
'''
def read(c,py,root):
 clocks=[]
 for _ in range(3):
  a=time.time();si,so,se=c.exec_command('date +%s.%N',timeout=10);raw=so.read();err=se.read();rc=so.channel.recv_exit_status();b=time.time();assert rc==0,err.decode();remote=float(raw)
  clocks.append(dict(local_before=a,local_after=b,remote_epoch=remote,offset_low=remote-b,offset_high=remote-a,offset_mid=remote-(a+b)/2,roundtrip_s=b-a))
 si,so,se=c.exec_command(shlex.quote(py)+' -B - '+shlex.quote(root),timeout=25);si.write(CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
 v['clock_samples']=clocks;v['clock_offset_estimate']=min(clocks,key=lambda x:x['roundtrip_s'])
 offset=v['clock_offset_estimate']
 for row in v['rows']:
  row['health_local_epoch_estimate']=row['health_epoch']-offset['offset_mid'];row['offset_halfwidth_s']=(offset['offset_high']-offset['offset_low'])/2
 return v
def main():
 p=R/'RANK_SAME_CONTROL_CLOCK_OFFSET_PHASE_READONLY_ACTUAL.json';assert not p.exists();nodes=[];c=None
 try:c=t.connect();nodes.append(read(c,t.PY,'/mnt/mod4_linux_durable_20261013/'+D.name))
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  nodes.append(read(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name))
 finally:pw=None;c.close()
 rows=[r for n in nodes for r in n['rows']];same=len(rows)==3 and len({r['controls'] for r in rows})==1
 v=dict(epoch=time.time(),nodes=nodes,same_control_steps=same,phase_order_if_same=[r['rank'] for r in sorted(rows,key=lambda r:r['health_local_epoch_estimate'])] if same else None,
  timestamp_scope='Health report written within env.step at the specified physical-control boundary, before subsequent PPO gradient collective. Clock offset estimated with SSH date response bounds; assumes no wall-clock step between phase and read. Not CUDA/NCCL kernel profiling or time-averaged causal attribution.',
  no_training_runtime_or_other_process_changes=True)
 p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v),flush=True)
if __name__=='__main__':main()
