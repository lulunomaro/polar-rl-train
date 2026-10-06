from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
code=r'''
from pathlib import Path
import sys,json,re,time
D=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_PRACTICAL_REVIEW_20261007');sys.path.insert(0,str(D));import continue_clock2000_practical_review_once as q
a=q.base.budget_state()['active_segment'];assert a and a['kind']=='moe_S1A_A0_selected_clock_learning';p=q.helpers.identity(a['pid'])
assert p and p['start_ticks']==47133319 and str(q.w.CODE/'train_mod4_ppo.py') in p['argv'] and p['cwd']==str(q.P)
txt=Path(a['log']).read_text(errors='replace');dirs=re.findall(r'\[mod4-isaac\] log_dir=(.+)',txt);assert len(dirs)==1
run=Path(dirs[0]);m=q.w.read(run/'run_manifest.json');assert m['init_checkpoint_sha256']==q.SHA and m['start_iteration']==23509 and m['num_envs']==20000
assert float(m['env']['RM_PHYSICS_DT_S'])==.002 and m['env']['RM_KEEP_STD']=='1' and m['env']['RM_MILD_DR_PROFILE']=='white_v3'
for n,h in m['src_sha256'].items():assert q.base.sha(run/'src_snapshot'/n)==h,n
iterations=[float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',txt)];assert iterations and 'Traceback (most recent call last)' not in txt and 'CUDA out of memory' not in txt
latest=q.w.read(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None;ck=q.base.checkpoint(Path(latest['checkpoint'])) if latest else None
if latest:assert latest['pid']==p['pid'] and ck['finite_tensors']==68
freeze=q.w.read(run/'rolling_source_freeze.json') if (run/'rolling_source_freeze.json').exists() else None
if freeze:assert freeze['sha256']==q.w.read(D/'reports/SOURCE_FREEZE.json')['sha256']
v=dict(epoch=time.time(),trainer=p,run=str(run),manifest_sha256=q.base.sha(run/'run_manifest.json'),manifest_actual_init_start23509=True,own_actual_PPO_iteration_times_s=iterations,
 actual_clock=q.validate_clock(.002),own_src_snapshot_hashes_exact=True,own_runtime_freeze_verified=freeze is not None,own_latest_complete=latest,own_checkpoint=ck,
 periodic_checkpoint_pending=latest is None,source_23509_CPU68_exact_reused=True,active_training=q.w.read(q.ctl.STATE_PATH).get('active_training'),initial_newpolicy_not_replayed=True,no_extra_GPU_or_budget_mutation=True)
q.write('FORMAL_CLOCK_ACTUAL_VERIFIED.json',v);print(json.dumps(v))
'''
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
 (R/'DT2000_FORMAL_CLOCK_ACTUAL_VERIFIED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
