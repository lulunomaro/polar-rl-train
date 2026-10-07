"""Derive a separate frozen-worker version; old0.5ms worker bytes and jobs remain intact."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
src=(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007/eval_worker.py').read_text(encoding='utf8')
out=src.replace('ROOT=Path(__file__).resolve().parent','ROOT=Path(__file__).resolve().parent\nBRIDGE_ROOT=ROOT.parent')
out=out.replace("ROOT/'vendor'","BRIDGE_ROOT/'vendor'").replace("ROOT/'secrets/known_hosts'","BRIDGE_ROOT/'secrets/known_hosts'").replace("ROOT/'secrets/eval_ed25519'","BRIDGE_ROOT/'secrets/eval_ed25519'")
out=out.replace("'ac8645c775af170ba06a3f4d37b0b0724a043cec3acb9c303556ebdcc953eb68'","'812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'")
out=out.replace("assert manifest['profile'] in ['nominal','white_v2','white_v3'] and manifest['num_envs']==(80 if manifest['kind']=='flat' else 88)",
 "assert manifest['profile'] in ['nominal','white_v2','white_v3']\n assert manifest['num_envs']==(10 if manifest['steps']==300 else 80) if manifest['kind']=='flat' else manifest['num_envs']==88\n assert manifest['architecture_variant'] in ['A0','A1','A2'] and manifest['physics_dt_s']==.001")
out=out.replace("cfg['RM_MOD4_USD']=str(runtime/'assets/robot.usd')", "assert float(cfg['RM_PHYSICS_DT_S'])==.001 and original['clock']['decimation']==10\n  cfg['RM_MOD4_USD']=str(runtime/'assets/robot.usd')")
out=out.replace("source=validate_checkpoint(ck);assert source['finite_tensors']==68", "source=validate_checkpoint(ck);assert source['finite_tensors']>=68\n data=__import__('torch').load(ck,map_location='cpu',weights_only=False)\n variant=data.get('history_architecture',{}).get('variant','A0');assert variant==manifest['architecture_variant']\n if variant!='A0':assert data['history_architecture']['actual_updates']==275 and not data['history_architecture']['teacher_is_actor_input']")
out=out.replace("{'flat':'validate_speed.py','spin':'contact_calibration_probe.py','world':'world_spin_probe.py'}", "{'flat':'frozen_history_flat.py','spin':'frozen_history_spin.py','world':'frozen_history_world.py'}")
out=out.replace("env.update(ISAACSIM_ACCEPT_EULA='Y'", "env.update(PYTHONPATH=str(runtime/'runtime')+os.pathsep+str(runtime/'runtime/isaac/mod4'),ISAACSIM_ACCEPT_EULA='Y'")
out=out.replace("launch=time.time()", "launch=time.time();memory=ObservedMemoryPeak();memory.start()")
out=out.replace("text=log.read_text(encoding='utf8',errors='replace');error_files", "memory.stop()\n text=log.read_text(encoding='utf8',errors='replace');error_files")
out=out.replace("'errors':bad_lines", "'physics_dt_s':.001,'architecture_variant':variant,'observed_GPU_memory_mib':memory.peak,'memory_sampling_period_s':2.,'observed_peak_not_continuous_peak':True,\n  'errors':bad_lines")
out=out.replace("lock_path=ROOT/'worker.lock'", "lock_path=BRIDGE_ROOT/'worker.lock'")
out=out.replace("jobs=rpc({'op':'list_jobs'})['jobs'];", "jobs=[j for j in rpc({'op':'list_jobs'})['jobs'] if j.startswith('clk1000-')];")
memory='''
class ObservedMemoryPeak:
 def __init__(self):
  import threading
  self.event=threading.Event();self.peak=0.;self.thread=threading.Thread(target=self.loop,daemon=True)
 def loop(self):
  while not self.event.is_set():
   p=subprocess.run(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,creationflags=0x08000000)
   try:self.peak=max(self.peak,float(p.stdout.strip().splitlines()[0]))
   except (ValueError,IndexError):pass
   self.event.wait(2.)
 def start(self):self.thread.start()
 def stop(self):self.event.set();self.thread.join(timeout=5)

'''
out=out.replace('def execute(job):',memory+'def execute(job):')
compile(out,'eval_worker_clock1000.py','exec')
(D/'eval_worker_clock1000.py').write_text(out,encoding='utf8')
proof=dict(original_worker_sha256=hashlib.sha256((D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007/eval_worker.py').read_bytes()).hexdigest(),
 new_worker_sha256=hashlib.sha256((D/'eval_worker_clock1000.py').read_bytes()).hexdigest(),changes=['Separate worker root, shared original single GPU lock/forced bridge secrets',
 'Only clk1000 immutable approved v1.5 jobs, matching architecture and1ms clock',
 'Original source219 hashes and sole Windows USD path adapter',
 'New frozen history inference entries; no PPO or production authority',
 'Observed2s GPU memory peak and measured process/transfer wall'])
(D/'reports/CLOCK1000_WORKER_SOURCE_REVIEW.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(proof))
