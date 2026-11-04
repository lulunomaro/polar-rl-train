"""One actual parent launch with a fresh read-only snapshot and actual outer wait."""
from pathlib import Path
import sys,json,ast,hashlib,shlex,time
D=Path(__file__).resolve().parent;T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';stage=json.loads((D/'STAGE_RESULT.json').read_bytes());assert stage['returncode']==stage['source_verification_rc']==0;root=stage['root'];assert not(D/'DISPATCH_STARTED_ONCE.json').exists();H=lambda b:hashlib.sha256(b).hexdigest();idx=json.loads((D/'SOURCE_DELTA.json').read_bytes());ownerSHA=next(r['SHA']for r in idx['source_files']if r['relative']=='eight_posttrain_original_owner_v1.py')
tr=ast.parse((D.parent/'mod4v1_supermimic_bptt_20261102/observe_bound_probe_resources_after_zero_admission_timeout_once.py').read_bytes());query=ast.literal_eval(next(n.value for n in tr.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='code'for t in n.targets)));assert 'lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals=0'in query
sys.path.insert(0,str(T));from project_connector import connect72
c=connect72();s=c.open_sftp()
def command(code,timeout=90):
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=timeout);i.close();a=o.read().decode();b=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,b);return a
try:
 resource=json.loads(command(query));(D/'RESOURCE_PRELAUNCH.json').write_text(json.dumps(resource,indent=2),encoding='utf8')
 controller=r'''from pathlib import Path
import sys,subprocess,time,json,hashlib,traceback
B=Path(ROOT);sys.path.insert(0,str(B));import three_slot_common_v1 as b
expected=OWNER_SHA;assert hashlib.sha256((B/'eight_posttrain_original_owner_v1.py').read_bytes()).hexdigest()==expected
assert not(B/'OUTER_DISPATCH.json').exists()and not(B/'OWNER_WAITED_ACTUAL.json').exists();child=None;errors=[];rc=None;start=time.time()
try:
 with (B/'OWNER_STDOUT_STDERR.log').open('xb')as log:child=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'eight_posttrain_original_owner_v1.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 b.put(B/'OUTER_DISPATCH.json',dict(epoch=time.time(),controller=b.ident(__import__('os').getpid()),parent=b.ident(child.pid),root=str(B),original_owner_SHA=expected,parent_Popen_calls=1))
 rc=child.wait()
except BaseException:errors.append(traceback.format_exc())
finally:
 if child is not None and child.poll()is None:rc=child.wait()
 b.put(B/'OWNER_WAITED_ACTUAL.json',dict(epoch=time.time(),actual_parent_p_wait_returned=child is not None and child.poll()is not None,returncode=rc,controller_errors=errors,wall_seconds=time.time()-start,parent_Popen_calls=1 if child is not None else 0,models_raw_SDK_C_or_lock_operations=0))
'''.replace('ROOT',repr(root)).replace('OWNER_SHA',repr(ownerSHA));ast.parse(controller)
 with s.open(root+'/e3_outer_wait.py','wx')as f:f.write(controller.encode())
 marker=dict(epoch=time.time(),root=root,owner_SHA=ownerSHA,controller_SHA=H(controller.encode()),only_E3=True,original_admission_rechecked_not_bypassed=True,read_only_resource_snapshot=resource['canonical_summary']);(D/'DISPATCH_STARTED_ONCE.json').write_text(json.dumps(marker,indent=2),encoding='utf8')
 code=r'''from pathlib import Path
import subprocess,time,json
B=Path(ROOT);log=(B/'OUTER_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'e3_outer_wait.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close()
for _ in range(120):
 q=B/'OUTER_DISPATCH.json'
 if q.exists():print(q.read_text());break
 if p.poll()is not None:raise RuntimeError('Outer failed before dispatch; inspect root, never replay')
 time.sleep(.25)
else:raise RuntimeError('No dispatch receipt; inspect process, never replay')
'''.replace('ROOT',repr(root));text=command(code);dispatch=json.loads(text);report=dict(marker,dispatch=dispatch,resource_snapshot_not_lease=True,admission_or_actual_learning_not_inferred_from_Popen=True);(D/'DISPATCH_RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
finally:s.close();c.close()
