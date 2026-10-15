"""Finite read-only scaling inspection; no live learner edits, signals or benchmarking."""
from pathlib import Path
import argparse,getpass,hashlib,json,shlex,sys,time,paramiko,statistics,re
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import json,os,psutil,re,subprocess,sys,time
B=Path(sys.argv[1]);source='lc01' not in str(B);interface='enp4s0' if source else 'eno1';v=dict(epoch=time.time(),root=str(B),CPU=dict(logical=psutil.cpu_count(),physical=psutil.cpu_count(logical=False),loadavg=os.getloadavg()),interface=interface)
v['link']={}
for n in ('speed','duplex','mtu','operstate'):
 try:v['link'][n]=(Path('/sys/class/net')/interface/n).read_text().strip()
 except OSError:v['link'][n]=None
v['own_processes']=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cpu_times','memory_info','num_threads']):
 try:
  if str(B) in ' '.join(p.info['cmdline'] or []):
   r=p.info;r['cpu_times']=r['cpu_times']._asdict();r['memory_info']=r['memory_info']._asdict();r['affinity']=p.cpu_affinity();e=p.environ();r['selected_environment']={k:e[k] for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NCCL_SOCKET_IFNAME','NCCL_IB_DISABLE','CUDA_VISIBLE_DEVICES','RANK','LOCAL_RANK','WORLD_SIZE') if k in e};v['own_processes'].append(r)
 except psutil.Error:pass
cmd=['nvidia-smi','--query-gpu=index,uuid,utilization.gpu,utilization.memory,memory.used,memory.free,power.draw,clocks.current.sm,clocks.current.memory,pcie.link.gen.current,pcie.link.width.current','--format=csv,noheader,nounits']
p=subprocess.run(cmd,capture_output=True,text=True);v['GPU_snapshot']=dict(rc=p.returncode,stdout=p.stdout,stderr=p.stderr)
if source:
 p=B/'rank0/train_worker.log'
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-350000));raw=f.read()
 text=re.sub(r'\x1b\[[0-9;]*m','',raw.decode(errors='replace'));rows=[]
 for m in re.finditer(r'Learning iteration\s+(\d+)\s*/\s*(\d+).*?(?=Learning iteration|\Z)',text,re.S):
  b=m.group(0);r=dict(iteration=int(m.group(1)))
  for key,pattern in [('sps',r'Steps per second:\s*([\d,]+)'),('collection',r'Collection time:\s*([\d.]+)s'),('learning',r'Learning time:\s*([\d.]+)s'),('total',r'Iteration time:\s*([\d.]+)s')]:
   q=re.search(pattern,b)
   if q:r[key]=float(q.group(1).replace(',',''))
  if len(r)==5:rows.append(r)
 v['last_iterations']=rows[-12:];v['log_tail']=text
 for name in ('CURRENT_THREE_RANK_ACTUAL.json','OWNER_ORIGINAL_ERROR.json'):
  if (B/name).exists():v[name]=json.loads((B/name).read_bytes())
print(json.dumps(v))
'''
def main():
 p=R/'THREE_GPU_SCALING_FACTOR_CURRENT_READONLY_ACTUAL.json';assert not p.exists();nodes=[];c=None
 try:
  c=t.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -B - '+shlex.quote('/mnt/mod4_linux_durable_20261013/'+D.name),timeout=35);si.write(CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();nodes.append(json.loads(out))
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  si,so,se=c.exec_command("'/home/lc01/Zonglin Li/zonglin2/run-python.sh' -B - "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name),timeout=35);si.write(CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();nodes.append(json.loads(out))
 finally:pw=None;c.close()
 sample=nodes[0]['last_iterations'][-8:];assert sample
 s={k:sum(r[k] for r in sample)/len(sample) for k in ('collection','learning','total')};s.update(global_envsteps_s=len(sample)*1440000/sum(r['total'] for r in sample),single_GPU_30000_is_human_baseline_not_matched_rebenchmark=True,baseline_iteration_seconds_if_identical=480000/30000)
 s['scaling_vs_human_30000']=s['global_envsteps_s']/30000;s['parallel_efficiency_vs_ideal90000']=s['global_envsteps_s']/90000
 p.write_text(json.dumps(dict(epoch=time.time(),nodes=nodes,derived=s,learning_timer_includes_GAE_backward_adaptive_KL_allreduce_optimizer_wait_not_pure_network=True,per_rank_phase_latency_and_network_bandwidth_not_profiled=True,no_live_training_or_resource_configuration_modified=True),indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(p.resolve()),derived=s,nodes=[{k:v for k,v in x.items() if k not in ('log_tail','CURRENT_THREE_RANK_ACTUAL.json','last_iterations')} for x in nodes]),default=str),flush=True)
if __name__=='__main__':main()
