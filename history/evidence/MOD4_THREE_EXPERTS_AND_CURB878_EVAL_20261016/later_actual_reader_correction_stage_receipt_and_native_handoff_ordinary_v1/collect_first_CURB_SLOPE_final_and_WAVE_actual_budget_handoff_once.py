"""Collect closed first two expert models and actual handoff to independent WAVE."""
from pathlib import Path
import getpass,hashlib,importlib.util,json,paramiko,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports'
s=importlib.util.spec_from_file_location('own_read_pure',D/'read_independent_cohort_actual_bounded.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def final(c,py,root,job):
 n=m.read(c,py,root);r=next(x['data']['final'] for x in n['files'] if x['path']==root+'/job'+str(job)+'/run/FINAL.json');dst=D/'first_closed_expert_models'/('job'+str(job))/Path(r['path']).name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();tmp=dst.with_suffix('.pt.partial');sf=c.open_sftp()
 try:sf.get(r['path'],str(tmp))
 finally:sf.close()
 assert tmp.stat().st_size==r['bytes'] and H(tmp)==r['SHA'];tmp.replace(dst);return dict(node=n,final=r,local_path=str(dst.resolve()),complete_twohost_size_SHA=True)
def main():
 report=R/'FIRST_CURB_SLOPE_FINAL_AND_WAVE_ACTUAL_CANONICAL_HANDOFF_COLLECTION.json';assert not report.exists();c=None;rows=[]
 try:
  c=m.t.connect();rows.append(final(c,m.t.PY,'/mnt/mod4_linux_durable_20261013/'+D.name+'/train',0));code="from pathlib import Path;import json,psutil;B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(B.read_bytes());print(json.dumps(dict(active=c['active_segment'],charged=c['charged_training_seconds'],remaining=c['remaining_training_seconds'],previous_cohort=[z for z in c['completed_segments'] if z.get('owner_parent_pid')==462797],old_owner_absent=not psutil.pid_exists(462797),old_CURB_worker_absent=not psutil.pid_exists(462799),new_WAVE_owner=psutil.Process(466300).as_dict(attrs=['pid','create_time','cmdline']))))";si,so,se=c.exec_command(shlex.quote(m.t.PY)+' -B -c '+shlex.quote(code),timeout=30);raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();budget=json.loads(raw);assert budget['old_owner_absent'] and budget['old_CURB_worker_absent'] and budget['active']['owner_parent_pid']==466300 and len(budget['previous_cohort'])==1
 finally:m.t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';rows.append(final(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/train',1));wave=m.read(c,'/home/lc01/Zonglin Li/zonglin2/run-python.sh','/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/wave_episode_reviewed_v3')
 finally:pw=None;c.close()
 report.write_text(json.dumps(dict(epoch=time.time(),closed_experts=rows,actual_canonical=budget,wave=wave,prior_cohort_settled_once_new_WAVE_active_not_old_locked=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(report),closed=[{k:z[k] for k in ('final','local_path')} for z in rows],canonical=budget)),flush=True)
if __name__=='__main__':main()
