"""One bounded own-root performance snapshot; no learner mutation or extra watcher."""
from pathlib import Path
import hashlib,json,shlex,statistics,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import hashlib,importlib.util,json,re,sys,time
B=Path(sys.argv[1]);p=B/'rank0/train_worker.log'
with p.open('rb') as f:f.seek(max(0,p.stat().st_size-250000));raw=f.read()
text=re.sub(r'\x1b\[[0-9;]*m','',raw.decode(errors='replace'))
pattern=r'Learning iteration\s+(\d+)\s*/\s*(\d+).*?(?=Learning iteration|\Z)'
blocks=[]
for m in re.finditer(pattern,text,re.S):
 b=m.group(0);v=dict(iteration=int(m.group(1)),target=int(m.group(2)))
 for k,pat in [('sps',r'Computation:\s*([\d.]+)\s*steps/s'),('collection_seconds',r'collection:\s*([\d.]+)s'),('learning_seconds',r'learning\s*([\d.]+)s'),('iteration_seconds',r'Iteration time:\s*([\d.]+)s'),('elapsed',r'Time elapsed:\s*([^\n]+)'),('eta',r'ETA:\s*([^\n]+)')]:
  q=re.search(pat,b)
  if q:v[k]=q.group(1).strip() if k in ('elapsed','eta') else float(q.group(1))
 if 'iteration_seconds' in v:blocks.append(v)
v=dict(epoch=time.time(),root=str(B),log=dict(path=str(p),bytes=p.stat().st_size,tail_SHA=hashlib.sha256(raw).hexdigest(),tail=text),last_complete_iterations=blocks[-12:])
for name in ('CURRENT_THREE_RANK_ACTUAL.json','SINGLE_PPO_7H_LEARNING_ADMITTED.json','THREE_RANK_FINAL_ACTUAL.json','OWNER_ORIGINAL_ERROR.json'):
 q=B/name
 if q.exists():v[name]=json.loads(q.read_bytes())
spec=importlib.util.find_spec('rsl_rl');q=Path(spec.origin).parent/'utils/logger.py'
if q.exists():
 s=q.read_text();lines=s.splitlines();indices=[i for i,x in enumerate(lines) if any(z in x for z in ('fps =','total_num_steps','gpu_world_size','Computation:'))];selected=sorted({j for i in indices for j in range(max(0,i-2),min(len(lines),i+3))})
 v['actual_logger_source_formula']=dict(path=str(q),SHA=hashlib.sha256(q.read_bytes()).hexdigest(),lines=[dict(number=i+1,text=lines[i]) for i in selected])
print(json.dumps(v))
'''
def main():
 c=None
 try:
  c=t.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -B - '+shlex.quote('/mnt/mod4_linux_durable_20261013/'+D.name),timeout=40);si.write(CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,err.decode();v=json.loads(out)
 finally:t.close(c)
 assert v['last_complete_iterations'],'No complete iteration metric parsed; preserve raw log rather than invent SPS.'
 a=v['last_complete_iterations'][-8:];dur=sum(x['iteration_seconds'] for x in a);v['derived']=dict(last_n_iterations=len(a),global_envs=60000,per_rank_envs=20000,controls_per_iteration_per_rank=24,physics_substeps_per_control=4,mean_iteration_seconds=dur/len(a),control_vector_ticks_per_second=len(a)*24/dur,global_control_environment_transitions_per_second=len(a)*24*60000/dur,global_physics_environment_substeps_per_second=len(a)*24*60000*4/dur,measured_end_to_end_iteration_includes_rollout_and_PPO_learning=True,checkpoint_and_supervisor_wall_not_fully_in_iteration_timer=True,latest_logger_sps=a[-1].get('sps'))
 p=R/('SHARED_PPO_CURRENT_THROUGHPUT_ACTUAL_'+str(time.time_ns())+'.json');p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p.resolve()),epoch=v['epoch'],last_iterations=a,derived=v['derived'],phase=v.get('CURRENT_THREE_RANK_ACTUAL.json',{}).get('phase'),logger_formula=v.get('actual_logger_source_formula'))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('THROUGHPUT_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),read_only_no_learning_mutation=True),indent=2));raise
