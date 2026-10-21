"""One non-gating, read-only repair observation. No watcher, GPU test or checkpoint reads."""
from pathlib import Path
import json,sys,time
T=Path(__file__).resolve().parent;W=T.parent;N=T/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022';R=N/'reports'
q=json.loads((R/'PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert q['passed']
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
c=d.t.connect()
try:
 result=d.code(c,d.t.PY,"""from pathlib import Path
import json,psutil,time
B=Path(v['root']);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
expected=v['worker'];actual=None
try:
 p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'] and p.exe()==expected['exe'] and p.cmdline()==expected['argv'];actual=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline())
except psutil.NoSuchProcess:pass
out=B/'job0/production';completed=read(out/'OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json');prefix=read(out/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json');errors={str(p):read(p) for p in out.glob('*ORIGINAL_ERROR*.json')}
controls=prefix.get('controls',0) if prefix else 0;updates=completed.get('completed',0) if completed else 0
log=B/'job0/production_WORKER.log';tail=[]
if log.exists():
 with log.open('rb') as f:f.seek(max(0,log.stat().st_size-65536));tail=[x for x in f.read().decode('utf8','replace').splitlines() if 'h1_step270_arena_exit' in x][-8:]
print(json.dumps(dict(epoch=time.time(),actual_own_worker_snapshot=actual,completed_PPO_snapshot=updates,complete_control_prefix_rows_snapshot=controls,past_previous318_control_error_boundary=bool(actual and updates>=14 and controls>=336 and not errors),original_errors_actual=errors,arena_exit_term_log_lines=tail,actual_FINAL_present=(out/'FINAL.json').exists(),one_non_gating_observation_not_continuous_alive_or_skill_proof=True,no_checkpoint_NPZ_or_GPU_native_read=True,no_timeout_wait_or_repeat=True)))
""",dict(root=q['source210']['H1_actual_GO'] and json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())['roots']['h1'],worker=q['source210']['H1_worker']),timeout=30)
finally:c.close()
with (R/'PAIR_REPAIR_PREVIOUS_FAILURE_BOUNDARY_OBSERVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
