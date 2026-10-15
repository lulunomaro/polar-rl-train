from pathlib import Path
import getpass,hashlib,json,shlex,sys,time,paramiko
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import json,sys,time
B=Path(sys.argv[1]);rows=[]
for p in sorted(B.glob('rank*/logs/*/CLOCK_TRAINING_HEALTH.json')):
 x=json.loads(p.read_bytes());rows.append(dict(path=str(p),rank=int(p.parts[-4][4:]),epoch=x['epoch'],control_steps=x['control_steps'],actual_physics_callbacks=x['actual_physics_callbacks'],ordinary=x['ordinary_episode_reset_events'],integrity=x['integrity_task_reset_events'],unknown=x['unknown_task_reset_events'],nonfinite=x['nonfinite_observed'],STOP=x['stop_reason']))
print(json.dumps(dict(epoch=time.time(),rows=rows)))
'''
def main():
 out=R/'SAME_CONTROL_HEALTH_THREE_RANK_PHASE_TIMESTAMPS_ACTUAL.json';assert not out.exists();nodes=[];c=None
 try:
  c=t.connect();si,so,se=c.exec_command(shlex.quote(t.PY)+' -B - '+shlex.quote('/mnt/mod4_linux_durable_20261013/'+D.name),timeout=25);si.write(CODE);si.flush();si.channel.shutdown_write();b=so.read();e=se.read();assert so.channel.recv_exit_status()==0,e.decode();nodes.append(json.loads(b))
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  si,so,se=c.exec_command("'/home/lc01/Zonglin Li/zonglin2/run-python.sh' -B - "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name),timeout=25);si.write(CODE);si.flush();si.channel.shutdown_write();b=so.read();e=se.read();assert so.channel.recv_exit_status()==0,e.decode();nodes.append(json.loads(b))
 finally:pw=None;c.close()
 rows=[r for n in nodes for r in n['rows']];same_controls=len(set(r['control_steps'] for r in rows))==1
 v=dict(epoch=time.time(),nodes=nodes,same_control_steps=same_controls,epoch_spread_if_same=max(r['epoch'] for r in rows)-min(r['epoch'] for r in rows) if same_controls else None,not_GPU_kernel_or_network_profiler=True,no_runtime_changes=True);out.write_text(json.dumps(v,indent=2));print(json.dumps(v),flush=True)
if __name__=='__main__':main()
