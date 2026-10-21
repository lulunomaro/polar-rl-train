from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;N=W/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',B/'run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory)
REMOTE=r'''
from pathlib import Path
import hashlib,json,shutil,time
B=Path(v['root']);old=Path(v['old']);assert not B.exists();native=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1shared_eval50_2110v3');nf=json.loads((native/'out/FINAL.json').read_bytes());nr=json.loads((native/'PARENT_RETURNED_ACTUAL.json').read_bytes());assert nf['source_SHA']==v['source_SHA'] and nf['controls']==60 and nr['actual_child_waited'] and nr['own_eval_lock_released'] and not nr['original_error_paths'];assert v['CPU']['passed_small_diagnostic_native_CPU'] and v['CPU']['source_SHA']==v['source_SHA'] and v['CPU']['clipped_GPU_CPU_max_abs_difference']<1e-5
B.mkdir(parents=True);(B/'job0').mkdir();shutil.copytree(old/'lib',B/'lib');shutil.copytree(old/'job0/runtime',B/'job0/runtime');shutil.copytree(old/'job0/assets',B/'job0/assets');shutil.copy2(old/'job0/original_run_manifest.json',B/'job0/original_run_manifest.json');shutil.copy2(native/'job0/source.pt',B/'job0/source.pt');assert hashlib.sha256((B/'job0/source.pt').read_bytes()).hexdigest()==v['source_SHA'];(B/'worker.py').write_text(v['worker'],encoding='utf8');(B/'parent.py').write_text(v['parent'],encoding='utf8');(B/'NATIVE13_ALL_ROWS_CPU_ACTUAL.json').write_text(json.dumps(v['CPU'],indent=2));(B/'FROZEN_DIAGNOSTIC_CONFIG.json').write_text(json.dumps(dict(source_SHA=v['source_SHA'],source_Adam=v['source_Adam'],python=v['python'],GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',user_explicit_coexist_authorized=True,max_physical_seconds=15,policy_steps=750,small13_diagnostic_not_original104_graduation=True),indent=2));print(json.dumps(dict(root=str(B),prepared=True,no_GPU_launch_yet=True)))
'''
try:
 native=json.loads((R/'SHARED_H1_NATIVE13_V3_ALL_ROWS_CPU_V2_ACTUAL.json').read_bytes());assert native['passed_small_diagnostic_native_CPU'] and native['clipped_GPU_CPU_max_abs_difference']<1e-5
 worker=(B/'shared_H1_frozen50_diagnostic_worker_V3.py').read_text('utf8');worker=worker.replace("time.monotonic()-start<300","time.monotonic()-start<1800")
 needle="  env._physics_action_delay.queue.control_us=20000\n";extra="""  import subprocess
  compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
  own=[line for line in compute.splitlines() if len(line.split(','))>=2 and line.split(',')[1].strip()==str(os.getpid())]
  assert own and all('GPU-16828f91-2b45-b646-8dc0-9481138e2842' in line for line in own)
  put('ACTUAL_SHARED_GPU_COMPUTE.json',dict(epoch=time.time(),own_compute_rows=own,explicit_shared_GPU=True))
  original_term=env.termination_manager.compute
  def observed_term(*args,**kwargs):
   value=original_term(*args,**kwargs)
   if env.e3_frame is not None:
    env.e3_frame['credited_before_reset']=env.recovery.credited.clone()
    env.e3_frame['stable_units_before_reset']=env.recovery.stable.clone()
   return value
  env.termination_manager.compute=observed_term
""";assert needle in worker;worker=worker.replace(needle,needle+extra);ast.parse(worker)
 with (B/'shared_H1_frozen50_diagnostic_worker_FULL_V4.py').open('x',encoding='utf8') as f:f.write(worker)
 q=json.loads((N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());spec=q['specs']['recovery'];root='/home/lc01/Zonglin Li/zonglin2/tasks/H1shared_eval50_full13_2110v4';secret=memory.recover();c=d.connect72(secret);secret=None
 try:
  prepared=d.code(c,d.PY72,REMOTE,dict(root=root,old=q['roots']['recovery'],source_SHA=native['source_SHA'],source_Adam=native['source_Adam'],worker=worker,parent=(B/'shared_H1_frozen50_detached_parent.py').read_text('utf8'),CPU=native,python=spec['python']),timeout=90)
  i,o,e=c.exec_command(__import__('shlex').quote(d.PY72)+' -u -B '+__import__('shlex').quote(root+'/parent.py')+' --detach',timeout=30);raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,(err,raw);parent=json.loads(raw)
  evidence=d.code(c,d.PY72,"from pathlib import Path;import json,psutil,time;B=Path(v['root']);p=psutil.Process(v['parent']['pid']);assert p.create_time()==v['parent']['creation'] and p.cmdline()==v['parent']['argv'];until=time.monotonic()+20\nwhile not (B/'CHILD_STARTED_ACTUAL.json').is_file() and not (B/'PARENT_ORIGINAL_ERROR.json').is_file() and time.monotonic()<until:time.sleep(.25)\nx=json.loads((B/'CHILD_STARTED_ACTUAL.json').read_bytes());w=psutil.Process(x['worker']['pid']);assert w.create_time()==x['worker']['creation'];print(json.dumps(dict(epoch=time.time(),parent=v['parent'],child_started=x,worker_actual_create_argv=w.cmdline(),actual_learning=False,no_new_training_cost=True,not_future_FINAL=True)))",dict(root=root,parent=parent),timeout=30)
 finally:c.close()
 with (R/'SHARED_H1_FULL13_DETACHED_ACTUAL_STARTED.json').open('x',encoding='utf8') as f:json.dump(evidence,f,ensure_ascii=False,indent=2)
 print(json.dumps(evidence))
except BaseException:
 with (R/'SHARED_H1_FULL13_LAUNCH_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
