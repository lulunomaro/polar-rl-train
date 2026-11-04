"""Fresh resource observation then exactly one original nine-expert parent.
No training, ledger write, foreign signals, changed scheduler or model access.
"""
from pathlib import Path
import ast,hashlib,json,shlex,sys,time
D=Path(__file__).resolve().parent;T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';A=D;stage=json.loads((A/'EVAL_STAGE_RESULT.json').read_bytes());assert stage['returncode']==0;root=stage['root'];out=A/'EVAL_DISPATCH_RESULT.json';mark=A/'EVAL_DISPATCH_STARTED_ONCE.json';assert not out.exists()and not mark.exists();H=lambda b:hashlib.sha256(b).hexdigest();source=T.parent/'mod4v1_supermimic_bptt_20261102/observe_bound_probe_resources_after_zero_admission_timeout_once.py';tree=ast.parse(source.read_bytes());query=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='code'for t in n.targets)));assert'lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals=0'in query
sys.path.insert(0,str(T));from project_connector import connect72
c=connect72();s=c.open_sftp();B='/home/lc01/Zonglin Li/zonglin2'
try:
 i,o,e=c.exec_command(shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(query),timeout=60);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();assert rc==0,stderr;resource=json.loads(stdout)
 with (A/'EVAL_RESOURCE_PRELAUNCH.json').open('x',encoding='utf8')as f:json.dump(resource,f,indent=2)
 assert float(resource['canonical_summary']['remaining_training_seconds'])>float(resource['canonical_summary']['finite_minimum_remaining_seconds']);# Original parent still rechecks owner/privateEX/finiteEX and hardware with bounded wait
 assert stage['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 controller=r'''from pathlib import Path
import subprocess,json,os,time,hashlib,traceback
B=Path(ROOT);OWN=Path('/home/lc01/Zonglin Li/zonglin2');assert B.is_relative_to(OWN/'tasks')and not(B/'E3_ASSESSMENT_OUTER_DISPATCH.json').exists()and not(B/'PARENT_STARTED.json').exists()
def put(name,value):
 p=B/name;q=p.with_suffix('.partial');q.write_text(json.dumps(value,indent=2));q.replace(p)
def identity(pid):
 t=Path('/proc',str(pid),'stat').read_text();v=t[t.rfind(')')+2:].split();return dict(pid=pid,linux_start_ticks=int(v[19]))
plan=json.loads((B/'GROUP_PLAN.json').read_bytes());pin=next(x for x in plan['worker_files']if x['relative']=='single_gpu_group_supervisor.py');raw=(B/pin['relative']).read_bytes();assert(len(raw),hashlib.sha256(raw).hexdigest())==(pin['bytes'],pin['SHA']);child=None;parent=None;errors=[];start=time.time();controller=identity(os.getpid())
try:
 log=(B/'GROUP_SUPERVISOR_STDOUT_STDERR.log').open('xb');child=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/'single_gpu_group_supervisor.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();parent=identity(child.pid);put('E3_ASSESSMENT_OUTER_DISPATCH.json',dict(kind='ONE_E3_ORIGINAL_SCOPE_PARENT_NOT_SKILL_ADMISSION',epoch=time.time(),root=str(B),controller=controller,parent=parent,original_parent_SHA256=pin['SHA'],original_parent_Popen_calls=1))
 rc=child.wait()
except BaseException:
 errors.append(traceback.format_exc());rc=child.wait()if child is not None else None
finally:
 put('E3_ASSESSMENT_PARENT_WAITED_ACTUAL.json',dict(kind='E3_ACTUAL_EXTERNAL_POPEN_WAIT_V1',epoch=time.time(),root=str(B),controller=controller,parent=parent if child is not None else None,actual_parent_p_wait_returned=child is not None and child.poll()is not None,returncode=rc,errors=errors,wall_seconds=time.time()-start,original_parent_Popen_calls=1 if child is not None else 0,Cwrites_model_or_lock_operations=0))
'''.replace('ROOT',repr(root));ast.parse(controller)
 with_marker=dict(epoch=time.time(),root=root,GPU_UUID=stage['GPU_UUID'],controller_SHA256=H(controller.encode()),resource_snapshot_not_lease=True,original_resource_and_close_wait_logic_unchanged=True,single_E3_cardinality_variant=True)
 with mark.open('x',encoding='utf8')as f:json.dump(with_marker,f,indent=2)
 with s.open(root+'/assessment_outer_wait.py','wx')as f:f.write(controller.encode())
 start=r'''from pathlib import Path
import subprocess,json,time
B=Path(ROOT);log=(B/'OUTER_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'assessment_outer_wait.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close()
for _ in range(120):
 q=B/'E3_ASSESSMENT_OUTER_DISPATCH.json'
 if q.exists():print(q.read_text());break
 if p.poll()is not None:raise RuntimeError('Outer exited before dispatch; inspect own log, do not replay')
 time.sleep(.25)
else:raise RuntimeError('No dispatch publication; inspect own process, do not replay')
'''.replace('ROOT',repr(root));i,o,e=c.exec_command(shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(start),timeout=60);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(with_marker,returncode=rc,stdout=stdout,stderr=stderr)
 if rc==0:v['dispatch']=json.loads(stdout)
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 print(json.dumps(v,indent=2));assert rc==0,stderr
finally:s.close();c.close()
