"""Continue only the unexecuted Popen after retained str(Path,encoding) error."""
from pathlib import Path
import json
import transport_bodyframe_pipeline_v7 as t
CODE=r'''
from pathlib import Path
import json,hashlib,os,subprocess,psutil,fcntl,time
r=Path(CONTEXT['root']);assert (r/'ROOT_UNIQUE_DISPATCH_INTENT.json').is_file()
assert not (r/'ROOT_UNIQUE_DISPATCH_ACTUAL.json').exists() and not (r/'PIPELINE_ONCE_CONSUMED.json').exists() and not (r/'PARENT_IDENTITY.json').exists()
assert not any(p.name()=='python' and any(str(r) in arg for arg in p.cmdline()) for p in psutil.process_iter() if p.pid!=os.getpid())
# The retained original Popen argument construction raised before Popen itself.
proof=json.loads((r/'PIPELINE_TARGET_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['target_CPU_actual']
for row in proof['active_files']:assert hashlib.sha256((r/row['name']).read_bytes()).hexdigest()==row['sha256']
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');assert json.loads(B.read_bytes())['active_segment'] is None
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
intent=r/'ROOT_ONLY_UNEXECUTED_POPEN_AFTER_LITERAL_REVIEWED_INTENT.json';assert not intent.exists()
with intent.open('x') as f:json.dump(dict(epoch=time.time(),original_error='TypeError decoding to str need bytes-like PosixPath before Popen',original_intent_SHA=hashlib.sha256((r/'ROOT_UNIQUE_DISPATCH_INTENT.json').read_bytes()).hexdigest(),CPU_materialization_not_repeated=True,no_previous_ownprocess_or_GPU=True),f);f.flush();os.fsync(f.fileno())
env=os.environ.copy();env.pop('CUDA_VISIBLE_DEVICES',None)
argv=[CONTEXT['python'],'-u',str(r/'bodyframe_finite_pipeline_parent_v6.py')]
p=subprocess.Popen(argv,cwd=r,env=env,start_new_session=True,stdin=subprocess.DEVNULL,stdout=(r/'pipeline_parent.log').open('xb'),stderr=subprocess.STDOUT)
q=psutil.Process(p.pid);out=dict(epoch=time.time(),pid=p.pid,created=q.create_time(),argv=q.cmdline(),cwd=q.cwd(),source=proof['source'],target_CPU_passed=True,PPO_NOT_yet_claimed=True,only_original_unexecuted_Popen_continued=True)
with (r/'ROOT_UNIQUE_DISPATCH_ACTUAL.json').open('x') as f:json.dump(out,f,indent=2);f.flush();os.fsync(f.fileno())
print(json.dumps(out))
'''
def main():
 c=None
 try:
  c=t.connect();v,p=t.run(c,CODE,dict(root=t.ROOT,python=t.PY),'BODYFRAME_V7_ONLY_UNEXECUTED_POPEN_UNIQUE_DISPATCH_ACTUAL',timeout=90);print(json.dumps(dict(report=str(p),actual=v)))
 finally:t.close(c)
if __name__=='__main__':main()
