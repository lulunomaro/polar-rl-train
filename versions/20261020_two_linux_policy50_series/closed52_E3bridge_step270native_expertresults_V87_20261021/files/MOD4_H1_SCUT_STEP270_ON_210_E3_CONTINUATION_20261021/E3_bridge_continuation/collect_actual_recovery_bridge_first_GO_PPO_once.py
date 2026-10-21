from pathlib import Path
import json,time,sys,traceback,importlib.util
B=Path(__file__).resolve().parent;W=B.parent.parent;R=B/'reports';sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
read210=r'''
from pathlib import Path
import json,time,psutil,fcntl
B=Path(v['owner']['root']);expected=v['owner'];p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'] and p.cmdline()==expected['argv'];until=time.monotonic()+570
while True:
 current=json.loads((B/'OWNER_CURRENT.json').read_bytes());row=current['rows'].get('recovery') or {};go=current['go'].get('recovery');save=row.get('latest_save') or {}
 if (go and save.get('updates',0)>0) or row.get('original_error') or (B/'OWNER_ORIGINAL_ERROR.json').exists():break
 assert time.monotonic()<until,'Actual positive PPO not yet observed; no replay'
 time.sleep(3)
assert go and save['updates']>0 and not row.get('original_error');C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());a=c['active_segment'];assert a['owner_parent_pid']==p.pid and set(a['experts'])=={'recovery'}
fds=psutil.Process(p.pid).open_files();held=[f.path for f in fds];assert str(C.parent/'native_floor_supervisor.lock') in held and '/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock' in held
assert c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8 and set(current['go'])=={'recovery'} and current['deferred_experts_without_GO']==['e2','h1']
print(json.dumps(dict(epoch=time.time(),owner=expected,current=current,canonical_active=a,remaining_actual_snapshot=c['remaining_training_seconds'],actual_original_writer_two_locks_open=True,H1_no_GO_no_learning_cost=True)))
'''
read72=r'''
from pathlib import Path
import json,psutil,subprocess,time
B=Path(v['root']);n=json.loads((B/'NODE_IDENTITY.json').read_bytes());p=psutil.Process(n['pid']);assert p.create_time()==n['creation'];w=v['row']['worker'];p=psutil.Process(w['pid']);assert p.create_time()==w['creation'] and p.cmdline()==w['argv'];go=json.loads((B/'job0/GO_PRODUCTION.json').read_bytes());assert go['run_id']==v['run_id'] and go['source_SHA']==v['source_SHA'];compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);own=[x for x in compute.splitlines() if x.split(',')[1].strip()==str(p.pid)];assert own and all(v['GPU_UUID'] in x for x in own)
print(json.dumps(dict(epoch=time.time(),node=n,worker=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline()),actual_GO=go,actual_own_compute=own,source_CPU=v['row']['closed_source_CPU'],latest_save=v['row']['latest_save'],not_continuous_alive_or_full_FINAL=True)))
'''
try:
 q=json.loads((R/'RECOVERY_BRIDGE_DETACHED_ACTUAL.json').read_bytes());c=d.t.connect()
 try:a=d.code(c,d.t.PY,read210,dict(owner=q['owner_identity']),timeout=600)
 finally:c.close()
 secret=m.recover();c=d.connect72(secret);secret=None
 try:z=d.code(c,d.PY72,read72,dict(root=q['root'],row=a['current']['rows']['recovery'],run_id=q['run_id'],source_SHA=q['source']['SHA'],GPU_UUID=q['spec']['GPU_UUID']),timeout=45)
 finally:c.close()
 assert z['latest_save']['updates']>0 and z['actual_GO']['source_SHA']==q['source']['SHA']
 v=dict(epoch=time.time(),passed=True,source210=a,source72=z,H1_native_preparation_no_GO=True,E2_deferred=True,original_budget_guard_reserved7800_not_lowered=True,actual_finite_returned=True)
 (R/'RECOVERY_BRIDGE_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps(dict(passed=True,run_id=q['run_id'],updates=z['latest_save']['updates'],Adam=z['latest_save'].get('Adam_step'),H1_no_learning_GO=True)))
except BaseException:
 (R/'RECOVERY_BRIDGE_FIRST_METADATA_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True),indent=2));raise
