from pathlib import Path
import importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ210=r'''
from pathlib import Path
import json,psutil,subprocess,time
B=Path(v['owner']['root']);expected=v['owner'];p=psutil.Process(expected['pid'])
assert p.create_time()==expected['creation'] and p.cmdline()==expected['argv']
until=time.monotonic()+570
while True:
 current=json.loads((B/'OWNER_CURRENT.json').read_bytes());rows=current['rows'];go=current['go']
 if all(go.get(k) and (rows.get(k,{}).get('latest_save') or {}).get('updates',0)>0 for k in ('h1',)):break
 if any(x.get('original_error') for x in rows.values()) or (B/'OWNER_ORIGINAL_ERROR.json').exists():
  raise AssertionError(dict(original_owner_error=(B/'OWNER_ORIGINAL_ERROR.json').read_text() if (B/'OWNER_ORIGINAL_ERROR.json').exists() else None,actual_rows=rows))
 assert time.monotonic()<until,'Actual positive PPO not observed for both slots; no rerun'
 time.sleep(3)
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());a=c['active_segment']
assert a['owner_parent_pid']==p.pid and set(a['experts'])==set(go)=={'h1'} and current['deferred_experts_without_GO']==['e2','recovery']
assert c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9
held=[x.path for x in p.open_files()]
assert str(C.parent/'native_floor_supervisor.lock') in held and '/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock' in held
H=Path(v['root']);node=json.loads((H/'NODE_IDENTITY.json').read_bytes());np=psutil.Process(node['pid']);assert np.create_time()==node['creation'] and np.cmdline()==node['argv']
w=rows['h1']['worker'];wp=psutil.Process(w['pid']);assert wp.create_time()==w['creation'] and wp.cmdline()==w['argv']
actual=json.loads((H/'GO_PRODUCTION.json').read_bytes())
assert actual==go['h1'] and actual['actual_H1_step270_scope_admitted'] and not actual['actual_H1_prelaunch_v2_scope_admitted']
assert actual['source_SHA']==v['source_SHA'] and actual['run_id']==v['run_id']
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
own=[x for x in compute.splitlines() if x.split(',')[1].strip()==str(wp.pid)]
assert own and all(v['GPU_UUID'] in x for x in own)
table={};table_lines=[]
with (H/'job0/production_WORKER.log').open(encoding='utf8',errors='replace') as f:
 for line in f:
  if '|' not in line:continue
  fields=[x.strip() for x in line.split('|')]
  if len(fields)>=5:
   try:weight=float(fields[3])
   except ValueError:continue
   table[fields[2]]=weight;table_lines.append(line.rstrip())
expected_rewards={'h1_step270_path_progress':1.,'h1_step270_requested_forward':3.,'h1_scut_fudan_air_wheel_zero_torque':.5,'h1_scut_fudan_leg_tuck':1.7,'h1_scut_fudan_wheel_below_base':.5}
assert all(table.get(k)==value for k,value in expected_rewards.items()),table
assert table.get('h1_control_events',0.)==0.
print(json.dumps(dict(epoch=time.time(),owner=expected,current=current,canonical_active=a,
 remaining_actual_snapshot=c['remaining_training_seconds'],actual_original_two_locks_open=True,
 H1_node=node,H1_worker=dict(pid=wp.pid,creation=wp.create_time(),exe=wp.exe(),argv=wp.cmdline()),
 H1_actual_GO=actual,H1_actual_own_compute=own,H1_actual_registered_reward_weights={k:table[k] for k in expected_rewards},H1_actual_reward_table_lines=table_lines,reward_table_matches_authorized_recipe=True,not_skill_or_future_FINAL_or_continuous_alive=True)))
'''
try:
 q=json.loads((R/'H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());put('H1_ONLY_FIRST_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),max_wait_seconds=570));c=d.t.connect()
 try:a=d.code(c,d.t.PY,READ210,dict(owner=q['owner_identity'],root=q['roots']['h1'],source_SHA=q['sources']['h1']['SHA'],GPU_UUID=q['specs']['h1']['GPU_UUID'],run_id=q['run_id']),timeout=600)
 finally:c.close()
 result=dict(epoch=time.time(),passed=True,run_id=q['run_id'],source210=a,actual_finite_returned=True,E3_no_GO_resource_deferred=True,reserve_seconds=7800,not_skill_or_future_FINAL=True)
 put('H1_ONLY_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json',result);print(json.dumps(dict(passed=True,run_id=q['run_id'],H1_updates=a['current']['rows']['h1']['latest_save']['updates'])))
except BaseException:
 put('H1_ONLY_FIRST_METADATA_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_rerun_or_hotpatch=True));raise
